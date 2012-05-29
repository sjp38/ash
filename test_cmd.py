#!/usr/bin/env monkeyrunner

from java.lang import System
if System.getProperty("os.name").startswith("Windows"):
    import os
    srcFileDir = os.path.dirname(os.path.abspath(__file__))
    print srcFileDir
    os.chdir(srcFileDir)
    sys.path = [srcFileDir] + sys.path

from cmd import *
from data import Command

def testExecution():
    print "test execution"
    testcmds = ["listDevices",
            "connectDevice test",
            "load test_xmls/data_sample.xml",
            "sleep 0.2",
            "save test_xmls/data_save_cmd_test.xml",
            "register reference(eventTest -notrigger cmd(touch DOWN_AND_UP 100 200))",
            "register reference(eventTest2 -notrigger cmd(press DOWN A))",
            "register reference(eventTest3 -notrigger cmd(drag 100 200 400 200 1.0))",
            "remove eventTest2",
            "show eventTest",
            "listData reference",
            "exec reference(eventTest3)",
            "exec cmd(touch DOWN_AND_UP 100 200)",

            "register reference(eventstreamtest2 -notrigger reference(eventTest3))",
            "register reference(eventstreamtest1 -notrigger list(reference(eventTest) cmd(sleep 0.1) reference(eventTest3)))",
            "remove eventstreamtest2",
            "show eventstreamtest1",
            "listData reference",
            "exec reference(eventstreamtest1)",
            "record recordTest1",
            "exec reference(eventTest3)",
            "exec reference(eventstreamtest1)",
            "exec reference(eventTest3)",
            "exec cmd(touch DOWN_AND_UP 100 200)",
            "press DOWN_AND_UP MENU",
            "finishRecording",
            "show recordTest1",
            # TODO NEXT

            "setTrigger eventstreamtest1 trigger(keyboard Ctrl-K_DOWN)",
            "setTrigger recordTest1 trigger(keyboard A_DOWN)",
            "register reference(bindingTest3 trigger(keyboard B_DOWN) cmd(switchTriggerMode main))",
            "setTrigger eventstreamtest1 trigger(-modenull null null)",
            "exec trigger(keyboard A_DOWN)",
            "show recordTest1",
            "listData reference -a",

            "listData trigger_mode",
            "currentTriggerMode",
            "switchTriggerMode null",
            "currentTriggerMode",

            "execScript test_xmls/script_sample.xml",
            "startGui test_xmls/gui_keylayout_sample.xml",
            "startGuiAutoRefresh",
            "stopGuiAutoRefresh",
            "stopGui",
            "startDirectControl",
            "stopDirectControl",
            "startAutoConnection",
            "stopAutoConnection",
            "focus 0"
            ]

    try:
        for cmd in testcmds:
            print "raw command : ", cmd
            print "parsed command : ", CmdParser.parse(cmd)
            print CmdExecutor.execute(CmdParser.parse(cmd))

    except:
        raise
        return True
    return False



def testParsing():
    print "test parsing"
    userInput = "startGui keymap.xml"
    cmd = CmdParser.parse(userInput)
    compare = Command("startGui", ["keymap.xml"])
    if compare.__str__() != cmd.__str__():
        print "Fail test 1", cmd, compare
        return True

    userInput = "register reference(testRef -notrigger cmd(touch DOWN_AND_UP 320 540))"
    cmd = CmdParser.parse(userInput)
    compare = Command("register", ["reference(testRef -notrigger cmd(touch DOWN_AND_UP 320 540))"])
    if compare.__str__() != cmd.__str__():
        print "Fail test 2\n%s\n%s" % (cmd, compare)
        return True

    userInput = "list reference"
    cmd = CmdParser.parse(userInput)
    compare = Command("list", ["reference"])
    if compare.__str__() != cmd.__str__():
        print "Fail test 3\n%s\n%s" % (cmd, compare)
        return True

    userInput = "list reference -a"
    cmd = CmdParser.parse(userInput)
    compare = Command("list", ["reference"], ["a"])
    if compare.__str__() != cmd.__str__():
        print "Fail test 4\n%s\n%s" % (cmd, compare)
        return True

    # Currently does not use this cmd. Just for format test.
    userInput = "listEvent -abc -b -dc testarg testarg2 arg(this is sub(this is sub enclosing) enclosing) arg2"
    cmd = CmdParser.parse(userInput)
    compare = Command("listEvent", ["testarg", "testarg2", "arg(this is sub(this is sub enclosing) enclosing)", "arg2"], ["abc", "b", "dc"])
    if compare.__str__() != cmd.__str__():
        print "Fail test 5\n%s\n%s" % (cmd, compare)
        return True

    return False

def testModule():
    if testParsing():
        print "Fail!"
        return

    if testExecution():
        print "Fail!"
        return
    print "Success!"

if __name__ == "__main__":
    testModule()
