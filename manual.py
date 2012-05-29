#!/usr/bin/env monkeyrunner
# Module for manual.
# Author : SeongJae Pakr <sj38.park@gmail.com>

CMDS = """
listDevices [-ash] [-serial]
connectDevice [device name]

startGui <keymapfilename>
startGuiAutoReferesh
stopGuiAutoRefresh
stopGui

startDirectControl
stopDirectControl
startAutoConnection
stopAutoConnection

focus <order of device in device list>...
focusTo <left | right>

sleep <time in seconds>

exit
help [command]

setVirtualScreen <width> <height>
touch <DOWN | UP | DOWN_AND_UP> <x> <y> [-v]
press <DOWN | UP | DOWN_AND_UP> <key code>
drag <x1> <y1> <x2> <y2> [duration] [-v]
type <text>
wake
reboot
getProp <property name>
shell <"("shell command")">
snapshot [file name]

execScript <file path>
exec <cmd|list|reference|trigger>
load <file path>
save <file path> # Unreferenced datas not saved.
remove <reference name>
show <reference name>
listData <"reference" | "trigger_mode"> [-a] [-trigger_mode=<mode>]
currentTriggerMode
switchTriggerMode <mode name>
record <name> # return reference with no trigger
finishRecording
setTrigger <reference name> <trigger>
register <reference>

cmd(string)
list(cmds / references / lists seperated by ' ')
reference(name [{trigger|-notrigger}] [{cmd|list|reference}])
trigger([-mode<mode>] <type> <value>)

# data type = cmd, list, reference.
# list get cmds /references / lists.
# cmd is just one line string.
# reference is reference for cmd / list / reference with name, trigger(has mode, type, key).

ex)
reference(event1 modeA keyboard Shift-K_DOWN cmd(press UP 100 200))
reference(event2 modeA keyboard Shift-K_UP list(cmd(press UP 100 200), reference(event1), list(cmd(press UP 100 200), reference(event1)))
exec event1
exec reference(cmd(press UP MENU))
exec cmd(touch DOWN_AND_UP 300 400) # Maybe no one do this.
exec list(reference(event1), reference(event2), list(cmd(touch UP 200 300)))
switchmode modeA

"""
