#!/usr/bin/env monkeyrunner
# Module for manual.
# Author : SeongJae Pakr <sj38.park@gmail.com>

CMDS = """
listDevices
connectDevice [device name]

startGui <keymapfilename>
startGuiAutoReferesh
stopGuiAutoRefresh
stopGui

sleep <time in seconds>

loadEevent <event file name>
saveEvent <event file name>
addEvent <name> <event type> [-arg<arg>] [-x1<x>] [-y1<y>] [-x2<x2>] [-y2<y2>] [-act{UP|DOWN|DOWN_AND_UP}] [-dur<duration>]
removeEvent <name>
showEvent <name>
listEvent [-a]
execEvent <name>
execInstEvent <event type> [-arg<arg>] [-x1<x>] [-y1<y>] [-x2<x2>] [-y2<y2>] [-act{UP|DOWN|DOWN_AND_UP}] [-dur<duration>]

loadEventstream <eventstream file name>
saveEventstream <eventstream file name> [name]
addEventstream <name> <{ev|es}event or stream name> [interval1] [{ev|es}event or stream2 name2] [interval2] ...
removeEventstream <name>
showEventstream <name>
listEventstream [-a]
execEventstream <name>
recordEventstream <name>
doneEventstreamRecording

loadBinding <binding file name>
saveBinding <binding file name>
addBinding <name> <Keystream. e.g. Ctrl-K> <{ev|es|cmd"}event or event stream name or command[" if start with cmd]>
# Meta key is only Ctrl-Alt-Shift. Order is as typed above.
removeBinding <name>
showBinding <name>
listBinding [-a]
execBinding <name>
execBindingWithKey <keyInput e.g. Ctrl-K>

loadBindingset <file name>
saveBindingset <file name>
newBindingset <name>
removeBindingset <name>
showBindingset <name>
listBindingset [-a]
currentBindingset
switchBindingset <name>

execScript <scriptName>

exit
"""

