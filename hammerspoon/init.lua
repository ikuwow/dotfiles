-- Releasing a command key held on its own, with no other modifier, key, click
-- or scroll in between, switches the Japanese input mode. There is no
-- hold-duration limit, so any length of solo hold fires on release, and
-- Secure Keyboard Entry blocks event taps from other applications, so nothing
-- fires while it is on. Both callbacks return false so every event passes
-- through untouched.

local TAP_TARGET = {
  [hs.keycodes.map.cmd] = hs.keycodes.map.eisu,
  [hs.keycodes.map.rightcmd] = hs.keycodes.map.kana,
}

local pendingCmd = nil

local function onFlagsChanged(event)
  local keyCode = event:getKeyCode()
  local target = TAP_TARGET[keyCode]
  if not target then
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
      -- Pass 0: keyStroke's default delay is a 200ms usleep that would block
      -- this callback and invite macOS to disable the tap.
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

-- Every watcher and timer in this file is global so it outlives this chunk.
-- Collecting one runs its __gc, which stops it.
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

-- Esc and ` trade places on the HHKB Professional alone. hidutil sets the swap
-- as a UserKeyMapping on the HID service matching its vendor and product ID,
-- so other keyboards keep their layout. macOS drops the mapping along with the
-- service when the HHKB is unplugged and on restart, so it is applied when this
-- config loads and again each time the HHKB is plugged in.

local HHKB_VENDOR_ID = 0x0853
local HHKB_PRODUCT_ID = 0x0100

-- Keyboard usage page 7: 0x29 is Escape, 0x35 is the ` and ~ key.
local HHKB_KEY_MAPPING = '{"UserKeyMapping":['
  .. '{"HIDKeyboardModifierMappingSrc":0x700000029,"HIDKeyboardModifierMappingDst":0x700000035},'
  .. '{"HIDKeyboardModifierMappingSrc":0x700000035,"HIDKeyboardModifierMappingDst":0x700000029}'
  .. ']}'

local function applyHHKBKeyMapping()
  local matching = string.format('{"VendorID":%d,"ProductID":%d}', HHKB_VENDOR_ID, HHKB_PRODUCT_ID)
  hs.execute("/usr/bin/hidutil property --matching '" .. matching .. "' --set '" .. HHKB_KEY_MAPPING .. "'")
end

hhkbUsbWatcher = hs.usb.watcher.new(function(device)
  if device.eventType == "added" and device.vendorID == HHKB_VENDOR_ID and device.productID == HHKB_PRODUCT_ID then
    -- The 1-second delay is one a replug worked with, not a measured minimum.
    hhkbMappingTimer = hs.timer.doAfter(1, applyHHKBKeyMapping)
  end
end)
hhkbUsbWatcher:start()

applyHHKBKeyMapping()
