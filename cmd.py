# Module for command processing.
# Author : SeongJae Park <sj38.park@gmail.com>
import sys
import log
import time

import data
from data_model import Event, EventStream, Binding, BindingSet
import device_control

TAG = "Ash_Command"

class Cmd:
    def __init__(self, cmd, args, options=[]):
        self.cmd = cmd
        self.args = args
        self.options = options

    @staticmethod
    def equals(cmd1, cmd2):
        if cmd1.cmd != cmd2.cmd:
            return False
        if cmd1.args != cmd2.args:
            return False
        if cmd1.options != cmd2.options:
            return False
        return True

    def __str__(self):
        return "cmd : %s, args : %s, options: %s" % (self.cmd, self.args, self.options)


class CmdParser:
    @staticmethod
    def parse(rawInput):
        splitted = rawInput.split()
        cmd = splitted[0]
        del splitted[0]
        args = []
        options = []
        for split in splitted:
            if len(splitted) <= 0:
                break
            if split[0] == "-":
                options.append(split[1:])
            else:
                args.append(split)
        return Cmd(cmd, args, options)


def listDevices():
    devices = device_control.getConnectedDevices()
    print devices
    #TODO care Gui
    # if gui:
    #   Do something

def addEventStream(args, options):
    name = args[0] 
    del args[0]
    args = [0.0] + args
    items = []
    for i in range(len(args)/2):
        items.append(args[2*i:2*i+2])
    eventstream = EventStream(name, items)
    data.addEventStream(eventstream)

def addEvent(args, options):
    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0
    duration = 0.0
    action = ""
    arg = ""
    for opt in options:
        if opt[0:2] == "x1":
            x1 = int(opt[2:])
            continue
        elif opt[0:2] == "y1":
            y1 = int(opt[2:])
            continue
        elif opt[0:2] == "x2":
            x2 = int(opt[2:])
            continue
        elif opt[0:2] == "y2":
            y2 = int(opt[2:])
            continue
        elif opt[0:3] == "act":
            action = opt[3:]
            continue
        elif opt[0:3] == "dur":
            duration = float(opt[3:])
        elif opt[0:3] == "arg":
            arg = opt[3:]
    xys = [x1, y1, x2, y2]

    event = Event(args[0], args[1], xys, duration, action, arg) 
    data.addEvent(event)

def showEvent(eventName):
    event = data.getEvent(eventName)
    print event
    # TODO: consider Gui mode.
    #if guiRunning:
    #    blah blah blah

def listEvents(onlyName):
    print data.listEvent(onlyName)
    # TODO: consider Gui mode.
    #if guiRunning:
    #    blah blah blah

def showEventStream(esName):
    es = data.getEventStream(esName)
    print es
    # TODO: consider Gui mode.

def listEventStreams(onlyName):
    print data.listEventStream(onlyName)
    # TODO: consider Gui mode.

def touch(event):
    device_control.touch(event.xys[0], event.xys[1], event.action)
def press(event):
    device_control.keyPress(event.arg, event.action)
def drag(event):
    device_control.drag(event.xys, event.duration)
def type(event):
    device_control.type(event.arg)
def wake(event):
    device_control.wake()
def reboot(event):
    device_control.reboot()
def getProp(event):
    device_control.getProperty(event.arg)
def shell(event):
    device_control.shell(event.arg)
def snapshot(event):
    device_control.snapshot(event.arg)

def execEvent(eventName):
    event = data.getEvent(eventName)
    eval("%s(event)" % event.evtType)

def execEventStream(esName):
    es = data.getEventStream(esName)
    for item in es.items:
        interval = item[0]
        name = item[1]
        if interval > 0:
            time.sleep(interval)
        if name[0:2] == "ev":
            execEvent(data.getEvent(name[2:]).name)
        else:
            execEventStream(name[2:])

RECORD_ES_FILTER = ("execEvent", "execEventstream")
recording = False
recordName = ""
recordQ = []

def startRecording(name):
    global recording
    global recordName
    global recordQ
    recording = True
    recordName = name
    recordQ = []

def onFinishRecording():
    global recordQ
    global recordName
    global recording
    items = []
    for i in range(len(recordQ)):
        cmd = recordQ[i]
        if cmd.cmd == RECORD_ES_FILTER[0]:
            event = "ev" + cmd.args[0]
        else:
            event = "es" + cmd.args[0]
        interv = 0.0
        if i > 0:
            interv = recordQ[i-1].time - cmd.time 
            print "interv : " , interv
        items.append([interv, event])
    es = EventStream(recordName, items)
    data.addEventStream(es)

    recordQ = []
    recordName = ""
    recording = False

def showBinding(name):
    binding = data.getBinding(name)
    print binding
    # TODO : Consider GUI.

def listBindings(onlyName):
    # TODO : Consider GUI.
    print data.listBinding(onlyName)

def execBinding(name):
    binding = data.getBinding(name)
    if binding.events[0:2] == "ev":
        execEvent(binding.events[2:])
    else:
        execEventStream(binding.events[2:])

def showBindingSet(name):
    # TODO : Consider GUI.
    print data.listBindings(name)

def listBindingSets(onlyName):
    # TODO : Consider GUI.
    print data.listBindingSet(onlyName)


class CmdExecutor:
    CMD_MAPS = {
            "listDevices": lambda args, opts: listDevices(),
            "connectDevice": lambda args, opts: device_control.connect(args[0]),

#            "startGui": lambda args, opts: guiManager.start(args[0]),
#            "startGuiAutoRefresh": lambda args, opts, guiManager.startAutoReresh(True),
#            "stopGuiAutoRefresh": lambda args, opts, guiManager.startAutoReresh(False),
#            "stopGui": lambda args, opts, guiManager.stop(),

            "loadEvent": lambda args, opts: data.loadEvent(args[0]),
            "saveEvent": lambda args, opts: data.saveEvent(args[0]),
            "addEvent": lambda args, opts: addEvent(args, opts),
            "removeEvent": lambda args, opts: data.removeEvent(args[0]),
            "showEvent": lambda args, opts: showEvent(args[0]),
            "listEvent": lambda args, opts: listEvents(len(opts) == 0 or opts[0] != "a"),
            "execEvent": lambda args, opts: execEvent(args[0]),

            "loadEventstream": lambda args, opts: data.loadEventStream(args[0]),
            "saveEventstream": lambda args, opts: data.saveEventStream(args[0]),
            "addEventstream": lambda args, opts: addEventStream(args, opts),
            "removeEventstream": lambda args, opts: data.removeEventStream(args[0]),
            "showEventstream": lambda args, opts: showEventStream(args[0]),
            "listEventstream":
                lambda args, opts: listEventStreams(len(opts) == 0 or opts[0] != "a"),
            "execEventstream": lambda args, opts: execEventStream(args[0]),
            "recordEventstream": lambda args, opts: startRecording(args[0]),
            "doneEventstreamRecording": lambda args, opts: onFinishRecording(),

            "loadBinding": lambda args, opts: data.loadBinding(args[0]),
            "saveBinding": lambda args, opts: data.saveBinding(args[0]),
            "addBinding":
                lambda args, opts: data.addBinding(Binding(args[0], args[1], args[2])),
            "removeBinding": lambda args, opts: data.removeBinding(args[0]),
            "showBinding": lambda args, opts: showBinding(args[0]),
            "listBinding":
                lambda args, opts: listBindings(len(opts) == 0 or opts[0] != "a"),
            "execBinding": lambda args, opts: execBinding(args[0]),

            "loadBindingset": lambda args, opts: data.loadBindingSet(args[0]),
            "saveBindingset": lambda args, opts: data.saveBindingSet(args[0]),
            "newBindingset":
                lambda args, opts: data.addBindingSet(BindingSet(args[0], {})),
            "removeBindingset": lambda args, opts: data.removeBindingSet(args[0]),
            "showBindingset": lambda args, opts: showBindingSet(args[0]),
            "listBindingset":
                 lambda args, opts: listBindingSets(len(opts) == 0 or opts[0] != "a"),
            "currentBindingset":
                lambda args, opts: showBindingSet(data.currentBindingSet),
            "switchBindingset": lambda args, opts: data.switchBindingSet(args[0])
            }



    # Return false if something wrong.
    @staticmethod
    def execute(cmd):
        if cmd.cmd not in CmdExecutor.CMD_MAPS:
            log.i(TAG, "Wrong command %s" % cmd.cmd)
            return False
        if recording:
            if cmd.cmd in RECORD_ES_FILTER:
                global recordQ
                cmd.time = time.time()
                print "record time : " , cmd.time
                recordQ.append(cmd)

        result = CmdExecutor.CMD_MAPS[cmd.cmd](cmd.args, cmd.options)
        print result
        return result




def testExecution():
    print "test execution"
    try:
        cmd = Cmd("listDevices", [], [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("connectDevice", ["test"], [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("loadEvent", ["event_sample.xml"], [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("saveEvent", ["saveEventTest.xml"], [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("addEvent", ["eventTest", "touch"], ["x1100", "y1200", "actDOWN_AND_UP"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("addEvent", ["eventTest2", "press"], ["argA", "actDOWN"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("addEvent", ["eventTest3", "drag"], ["x1100", "y1200", "x1400", "y1200", "dur1.0"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("removeEvent", ["eventTest2"], [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("showEvent", ["eventTest"], [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("listEvent", [], [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("execEvent", ["eventTest3"], [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("loadEventstream", ["eventstream_sample.xml"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("saveEventstream", ["saveEventstream_test.xml"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("addEventstream", ["eventstreamtest2", "eventTest3"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("addEventstream", ["eventstreamtest1", "eveventTest", 0.1, "eveventTest3"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("removeEventstream", ["eventstreamtest2"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("showEventstream", ["eventstreamtest1"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("listEventstream", [], ["a"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("execEventstream", ["eventstreamtest1"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("recordEventstream", ["recordTest1"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("execEvent", ["eventTest3"], [])
        CmdExecutor.execute(cmd)

        time.sleep(0.3)

        cmd = Cmd("execEventstream", ["eventstreamtest1"])
        CmdExecutor.execute(cmd)

        time.sleep(1.2)

        cmd = Cmd("execEvent", ["eventTest3"], [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("doneEventstreamRecording", [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("showEventstream", ["recordTest1"], [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("loadBinding", ["keybinding_sample.xml"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("saveBinding", ["keybinding_savetest.xml"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("addBinding", ["bindingTest1", "Ctrl-K", "eveventstreamtest1"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("addBinding", ["bindingTest2", "A", "esrecordTest1"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("removeBinding", ["bindingTest1"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("showBinding", ["bindingTest2"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("listBinding", [], ["a"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("execBinding", ["bindingTest2"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("loadBindingset", ["bindingset_sample.xml"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("saveBindingset", ["bindingset_save_test.xml"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("newBindingset", ["bindingTest"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("removeBindingset", ["bindingTest"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("showBindingset", ["bindingSet2"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("listBindingset", [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("currentBindingset", [])
        CmdExecutor.execute(cmd)

        cmd = Cmd("switchBindingset", ["bindingSet1"])
        CmdExecutor.execute(cmd)

        cmd = Cmd("currentBindingset", [])
        CmdExecutor.execute(cmd)

    except:
        raise
        return True
    return False



def testParsing():
    print "test parsing"
    userInput = "startGui keymap.xml"
    cmd = CmdParser.parse(userInput)
    compare = Cmd("startGui", ["keymap.xml"])
    if not Cmd.equals(compare, cmd):
        print "Fail test 1", cmd, compare
        return True

    userInput = "addEvent testEvent touch -x1320 -y1540 -actDOWN_AND_UP"
    cmd = CmdParser.parse(userInput)
    compare = Cmd("addEvent", ["testEvent", "touch"],
            ["x1320", "y1540", "actDOWN_AND_UP"])
    if not Cmd.equals(compare, cmd):
        print "Fail test 2 ", cmd, compare
        return True

    userInput = "listEvent"
    cmd = CmdParser.parse(userInput)
    compare = Cmd("listEvent", [])
    if not Cmd.equals(compare, cmd):
        print "Fail test 3", cmd, compare
        return True

    userInput = "listEvent -a"
    cmd = CmdParser.parse(userInput)
    compare = Cmd("listEvent", [], ["a"])
    if not Cmd.equals(compare, cmd):
        print "Fail test 4", cmd, compare
        return True

    # Currently does not use this cmd. Just for format test.
    userInput = "listEvent -abc -b -dc testarg testarg2"
    cmd = CmdParser.parse(userInput)
    compare = Cmd("listEvent", ["testarg", "testarg2"], ["abc", "b", "dc"])
    if not Cmd.equals(compare, cmd):
        print "Fail test 5", cmd, compare
        return True
    return False

def testModule():
    result = testParsing()
    if result :
        print "Fail!"
        return

    result = testExecution()
    if result:
        print "Fail!"
        return
    print "Success!"

if __name__ == "__main__":
    testModule()
