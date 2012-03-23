# Module for command processing.
# Author : SeongJae Park <sj38.park@gmail.com>
import sys
import log
import time

import data
from data_model import Event, EventStream, Binding, BindingSet
import device_control
import gui

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
        enclosedArg = ""
        for split in splitted:
            if len(splitted) <= 0:
                break
            if split[0] == "-":
                options.append(split[1:])
            else:
                if enclosedArg != "":
                    enclosedArg += " " + split
                if "\"" in split:
                    if enclosedArg == "":
                        enclosedArg = split
                    else:
                        args.append(enclosedArg)
                        enclosedArg = ""
                    continue
                if enclosedArg == "":
                    args.append(split)
        return Cmd(cmd, args, options)


def listDevices():
    devices = device_control.getConnectedDevices()
    return devices

def connectDevice(args):
    if len(args) > 0:
        return device_control.connect(args[0])
    devices = device_control.getConnectedDevices()
    if len(devices) <= 0:
        return "No connected device."
    return device_control.connect(devices[0])



def addEventStream(args, options):
    name = args[0] 
    del args[0]
    args = [0.0] + args
    items = []
    for i in range(len(args)/2):
        item = args[2*i:2*i + 2]
        item[0] = float(item[0])
        items.append(item)
    eventstream = EventStream(name, items)
    data.addEventStream(eventstream)

def makeEvent(args, options):
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

    return Event(args[0], args[1], xys, duration, action, arg) 

def addEvent(args, options):
    event = makeEvent(args, options)
    data.addEvent(event)

def showEvent(eventName):
    event = data.getEvent(eventName)
    return event

def listEvents(onlyName):
    events = data.listEvent(onlyName)
    return events

def showEventStream(esName):
    es = data.getEventStream(esName)
    return es

def listEventStreams(onlyName):
    ess = data.listEventStream(onlyName)
    return ess

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
    return device_control.getProperty(event.arg)
def shell(event):
    return device_control.shell(event.arg)
def snapshot(event):
    return device_control.snapshot(event.arg)

def execEvent(eventName):
    event = data.getEvent(eventName)
    return eval("%s(event)" % event.evtType)

def execInstEvent(arg, opt):
    arg = ["tmp"] + arg
    event = makeEvent(arg, opt)
    return eval("%s(event)" % event.evtType)


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
            interv = cmd.time - recordQ[i-1].time
        items.append([interv, event])
    es = EventStream(recordName, items)
    data.addEventStream(es)

    recordQ = []
    recordName = ""
    recording = False

def showBinding(name):
    binding = data.getBinding(name)
    return binding

def listBindings(onlyName):
    bindings = data.listBinding(onlyName)
    return bindings

def execBinding(binding):
    actionType = binding.action[0:2]
    action = binding.action[2:]
    if actionType == "ev":
        execEvent(action)
    elif actionType == "es":
        execEventStream(action)
    else:
        parsed = CmdParser.parse(binding.action[4:-1])
        return CmdExecutor.execute(parsed)

def execBindingWithName(name):
    binding = data.getBinding(name)
    return execBinding(binding)

def execBindingWithKey(keyInput):
    binding = data.getBindingWithKey(keyInput)
    return execBinding(binding)

def showBindingSet(name):
    bindingSet = data.listBindings(name)
    return bindingSet

def listBindingSets(onlyName):
    bss = data.listBindingSet(onlyName)
    return bss

def execScript(filePath):
    f = open(filePath, "r")
    cmds = f.readlines()
    f.close()
    results = []
    for cmd in cmds:
        parsed = CmdParser.parse(cmd)
        result = CmdExecutor.execute(parsed)
        results.append(result)
    return results


class CmdExecutor:
    CMD_MAPS = {
            "listDevices": lambda args, opts: device_control.getConnectedDevices(),
            "connectDevice": lambda args, opts: connectDevice(args),
            "startGui": lambda args, opts: gui.start(args[0]),
            "startGuiAutoRefresh": lambda args, opts: gui.startAutoRefresh(True),
            "stopGuiAutoRefresh": lambda args, opts: gui.startAutoRefresh(False),
            "stopGui": lambda args, opts: gui.stop(),

            "sleep": lambda args, opts: time.sleep(float(args[0])),

            "loadEvent": lambda args, opts: data.loadEvent(args[0]),
            "saveEvent": lambda args, opts: data.saveEvent(args[0]),
            "addEvent": lambda args, opts: addEvent(args, opts),
            "removeEvent": lambda args, opts: data.removeEvent(args[0]),
            "showEvent": lambda args, opts: showEvent(args[0]),
            "listEvent": lambda args, opts: listEvents(len(opts) == 0 or opts[0] != "a"),
            "execEvent": lambda args, opts: execEvent(args[0]),
            "execInstEvent": lambda args, opts: execInstEvent(args, opts),

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
            "execBinding": lambda args, opts: execBindingWithName(args[0]),
            "execBindingWithKey": lambda args, opts: execBindingWithKey(args[0]),

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
            "switchBindingset": lambda args, opts: data.switchBindingSet(args[0]),

            "execScript": lambda args, opts: execScript(args[0])
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
                recordQ.append(cmd)

        result = CmdExecutor.CMD_MAPS[cmd.cmd](cmd.args, cmd.options)
        return result

