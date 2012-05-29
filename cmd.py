# Module for command processing.
# Author : SeongJae Park <sj38.park@gmail.com>
import sys
import log
import time

import data
from data import Ref, Command, Trigger
import device_control
import gui
import directControl

TAG = "Ash_Command"


class CmdParser:
    @staticmethod
    def parse(rawInput):
        splitted = rawInput.split()
        cmd = splitted[0]
        del splitted[0]
        args = []
        options = []
        enclosedArg = ""
        encloseLevel = 0
        for split in splitted:
            if len(splitted) <= 0:
                break
            if enclosedArg == "" and split[0] == "-":
                options.append(split[1:])
            else:
                if enclosedArg != "":
                    enclosedArg += " " + split
                if "(" in split:
                    encloseLevel += split.count("(")
                    if enclosedArg == "":
                        enclosedArg = split
                if (encloseLevel > 0):
                    encloseLevel -= split.count(")")
                    if encloseLevel == 0:
                        args.append(enclosedArg)
                        enclosedArg = ""
                    continue
                if enclosedArg == "":
                    args.append(split)
        return Command(cmd, args, options)

def connectDevice(args):
    if len(args) > 0:
        return device_control.connect(args[0])
    devices = device_control.listDevices()
    if len(devices) <= 0:
        return "No connected device."
    return device_control.connect(devices[0])

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

def snapshot(args):
    arg = ""
    if args: arg = args[0]
    return device_control.snapshot(arg)

def listData(args, opts):
    if args[0] == "reference":
        trigger_mode = None
        for opt in opts:
            if opt.startswith("trigger_mode="):
                trigger_mode = opt.split("=")[1]
        return data.listReferences("a" in opts, trigger_mode)
    elif args[0] == "trigger_mode":
        return data.listTriggerModes()

_recording = False
_recorded = []
RECORD_TARGET = ["touch", "press", "drag", "type", "wake", "reboot",
        "getProp", "shell", "snapshot", "connectDevice"]
def record(name):
    global _recording
    _recording = name

def finishRecord():
    global _recording
    global _recorded
    sleepTimes = []
    for i in range(len(_recorded)):
        if i > 0:
            sleepTime = _recorded[i].startTime - _recorded[i-1].startTime
            if sleepTime < 0: sleepTime = 0
            sleepTimes.append(sleepTime)
    for i in range(len(sleepTimes)):
        _recorded.insert(i*2 + 1, Command("sleep", [str(sleepTimes[i])]))

    ref = Ref(_recording, None, _recorded)
    data.addReference(ref)
    _recording = False
    _recorded = []

def setTrigger(args, opts):
    ref = data.getRef(args[0])
    trigger = args[1]
    return data.setTrigger(ref, trigger)

def makeCommand(args, opts):
    raw_cmd = ""
    for arg in args:
        raw_cmd += arg + " "
    for opt in opts:
        raw_cmd += "-" + opt + " "
    return CmdParser.parse(raw_cmd)

def makeReference(args, opts):
    name = args[0]
    if len(args) < 2:
        return data.getRef(name)
    if len(opts) > 0 and opts[0] == "notrigger":
        return Ref(name, None, args[1])
    else:
        return Ref(name, args[1], args[2])

def makeTrigger(args, opts):
    mode = data.currentTriggerMode
    if len(opts) > 0 and opts[0].startswith("mode"):
        mode = opts[0][4:]
    trig_type = args[0]
    value = args[1]
    return Trigger(mode, trig_type, value)

class CmdExecutor:
    CMD_MAPS = {
            "listDevices": lambda args, opts: device_control.listDevices(opts),
            "connectDevice": lambda args, opts: connectDevice(args),
            "startGui": lambda args, opts: gui.start(args[0]),
            "startGuiAutoRefresh": lambda args, opts: gui.startAutoRefresh(True),
            "stopGuiAutoRefresh": lambda args, opts: gui.startAutoRefresh(False),
            "stopGui": lambda args, opts: gui.stop(),

            "startDirectControl": lambda args, opts: directControl.start(),
            "stopDirectControl":lambda args, opts: directControl.stop(),

            "startAutoConnection":
                lambda args, opts: device_control.startAutoConnection(),
            "stopAutoConnection": lambda args, opts: device_control.stopAutoConnection(),
            "focus": lambda args, opts: device_control.focus(args),
            "focusTo": lambda args, opts: device_control.focusTo(args),

            # show, hide cursor is for internal. doesn't show at manual.
            # showCursor <x> <y> [-pressed]
            "showCursor": lambda args, opts:
                    device_control.showCursor(int(args[0]), int(args[1]), "pressed" in opts),
            "hideCursor": lambda args, opts: device_control.hideCursor(),

            "sleep": lambda args, opts: time.sleep(float(args[0])),

            "exit": lambda args, opts: sys.exit(),
#            "help": lambda args, opts: manual.help(args[0]),

            "setVirtualScreen": lambda args, opts:
                    device_control.setVirtualScreen(int(args[0]), int(args[1])),
            "touch": lambda args, opts:
                    device_control.touch(int(args[1]), int(args[2]), args[0],
                        "v" in opts),
            "press": lambda args, opts: device_control.keyPress(args[1], args[0]),
            "drag": lambda args, opts:
                    device_control.drag([args[0], args[1], args[2], args[3]], args[4],
                        "v" in opts),
            "type": lambda args, opts: device_control.type(args[0]),
            "wake": lambda args, opts: device_control.wake(),
            "reboot": lambda args, opts: device_control.reboot(),
            "getProp": lambda args, opts: device_control.getProperty(args[0]),
            "shell": lambda args, opts: device_control.shell(args[0][1:-1]),
            "snapshot": lambda args, opts: snapshot(args),

            "execScript": lambda args, opts: execScript(args[0]),
            "exec": lambda args, opts: CmdExecutor.execute(args[0]),
            "load": lambda args, opts: data.loadFrom(args[0]),
            "save": lambda args, opts: data.saveTo(args[0]),
            "remove": lambda args, opts: data.removeReference(args[0]),
            "show": lambda args, opts: data.getRef(args[0]),
            "listData": lambda args, opts: listData(args, opts),
            "currentTriggerMode": lambda args, opts: data.currentTriggerMode,
            "switchTriggerMode": lambda args, opts: data.switchTriggerMode(args[0]),
            "record": lambda args, opts: record(args[0]),
            "finishRecording": lambda args, opts: finishRecord(),
            "setTrigger": lambda args, opts: setTrigger(args, opts),
            "register": lambda args, opts: data.addReference(args[0]),

            "cmd": lambda args, opts: makeCommand(args, opts),
            "list": lambda args, opts: args,
            "reference": lambda args, opts: makeReference(args, opts),
            "trigger": lambda args, opts: makeTrigger(args, opts)
            }

    # Return false if something wrong.
    @staticmethod
    def execute(cmd):
        if isinstance(cmd, list):
            result = []
            for elem in cmd:
                result.append(CmdExecutor.execute(elem))
            return result

        if isinstance(cmd, Ref):
            if not cmd.target:
                reference = data.getRef(reference.name)
            return CmdExecutor.execute(cmd.target)

        if isinstance(cmd, Trigger):
            reference = data.getReferenceByTrigger(cmd)
            if not isinstance(reference, Ref):
                return "No reference for this trigger.", cmd
            return CmdExecutor.execute(reference.target)

        if cmd.cmd not in CmdExecutor.CMD_MAPS:
            log.i(TAG, "Wrong command %s" % cmd.cmd)
            return False
        for i in range(len(cmd.args)):
            if not isinstance(cmd.args[i], str): continue
            splits = cmd.args[i].split("(")
            if len(splits) > 1 and splits[0] in ["cmd", "list", "reference", "trigger"]:
                argStart = cmd.args[i].find("(")
                subCmd = cmd.args[i][0:argStart] + " " + cmd.args[i][argStart+1:-1]
                subCmd = CmdParser.parse(subCmd)
                cmd.args[i] = CmdExecutor.execute(subCmd)

        global _recording
        global _recorded
        global RECORD_TARGET
        if _recording and cmd.cmd in RECORD_TARGET:
            if not (cmd.cmd == "snapshot" and len(cmd.args) <= 0):
                cmd.startTime = time.time()
                _recorded.append(cmd)
        result = CmdExecutor.CMD_MAPS[cmd.cmd](cmd.args, cmd.opts)
        return result

