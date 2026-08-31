-- Releasing a command key that was held on its own, with no other modifier,
-- key, click or scroll in between, switches the Japanese input mode: left ⌘
-- sends 英数 (eisu), right ⌘ sends かな (kana). There is no hold-duration
-- limit, so any length of solo hold fires on release.

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
    -- false leaves the event in place; these taps only observe.
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
      -- Without an explicit delay keyStroke sleeps 200ms inside this callback.
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

-- All three watchers below are global on purpose: a local would be garbage
-- collected and the underlying event tap would stop delivering events.
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

-- Precautionary: waking has been reported to leave event taps not delivering
-- events. Unverified on this machine, so the taps are re-armed unconditionally.
sleepWatcher = hs.caffeinate.watcher.new(function(eventType)
  if eventType == hs.caffeinate.watcher.systemDidWake then
    pendingCmd = nil
    cmdFlagsWatcher:stop():start()
    otherInputWatcher:stop():start()
  end
end)
sleepWatcher:start()
