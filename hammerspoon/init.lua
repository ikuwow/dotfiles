-- Releasing a command key that was held on its own, with no other modifier,
-- key, click or scroll in between, switches the Japanese input mode: left ⌘
-- sends 英数 (eisu), right ⌘ sends かな (kana). There is no hold-duration
-- limit, so any length of solo hold fires on release. Secure Keyboard Entry
-- blocks event taps from other applications, so nothing fires while it is on.
-- Both callbacks return false, leaving every event in place; these taps only
-- observe.

local TAP_TARGET = {
  [hs.keycodes.map.cmd] = hs.keycodes.map.eisu,
  [hs.keycodes.map.rightcmd] = hs.keycodes.map.kana,
}

-- Keycode of the command key that is currently a solo-tap candidate.
local pendingCmd = nil

local function onFlagsChanged(event)
  local keyCode = event:getKeyCode()
  local target = TAP_TARGET[keyCode]
  if not target then
    -- Any other modifier changing state means the command key was not alone.
    pendingCmd = nil
    return false
  end

  local flags = event:getFlags()
  if flags.cmd then
    if flags:containExactly({ "cmd" }) then
      pendingCmd = keyCode
    else
      pendingCmd = nil
    end
  else
    if pendingCmd == keyCode then
      -- keyStroke's default delay is a 200ms usleep between key down and up,
      -- which would block the main thread inside this callback and invite
      -- macOS to disable the tap. Pass 0.
      hs.eventtap.keyStroke({}, target, 0)
    end
    pendingCmd = nil
  end
  return false
end

local function onOtherInput()
  pendingCmd = nil
  return false
end

-- The three watchers below are global so they outlive this chunk. Collecting
-- a watcher runs its __gc, which stops it and takes its tap or observer down.
cmdFlagsWatcher = hs.eventtap.new({ hs.eventtap.event.types.flagsChanged }, onFlagsChanged)
cmdFlagsWatcher:start()

otherInputWatcher = hs.eventtap.new({
  hs.eventtap.event.types.keyDown,
  hs.eventtap.event.types.leftMouseDown,
  hs.eventtap.event.types.rightMouseDown,
  hs.eventtap.event.types.otherMouseDown,
  hs.eventtap.event.types.scrollWheel,
}, onOtherInput)
otherInputWatcher:start()

-- Guard for a tap that does not resume after sleep, and discard a solo-tap
-- candidate stranded from before it. Cycling a live tap is idempotent.
sleepWatcher = hs.caffeinate.watcher.new(function(eventType)
  if eventType == hs.caffeinate.watcher.systemDidWake then
    pendingCmd = nil
    cmdFlagsWatcher:stop():start()
    otherInputWatcher:stop():start()
  end
end)
sleepWatcher:start()
