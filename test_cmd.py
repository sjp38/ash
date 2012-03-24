# Path setting for Damn Windows.
import sys
import os
srcFileDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(srcFileDir)
sys.path = [srcFileDir] + sys.path

from cmd import *

def testExecution():
    print "test execution"
    try:
        cmd = Cmd("listDevices", [], [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("connectDevice", ["test"], [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("loadEvent", ["test_xmls/event_sample.xml"], [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("sleep", ["0.2"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("saveEvent", ["test_xmls/saveEventTest.xml"], [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("addEvent", ["eventTest", "touch"], ["x1100", "y1200", "actDOWN_AND_UP"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("addEvent", ["eventTest2", "press"], ["argA", "actDOWN"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("addEvent", ["eventTest3", "drag"], ["x1100", "y1200", "x2400", "y2200", "dur1.0"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("removeEvent", ["eventTest2"], [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("showEvent", ["eventTest"], [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("listEvent", [], [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("execEvent", ["eventTest3"], [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("execInstEvent", ["touch"], ["x1100", "y1200", "actDOWN_AND_UP"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("loadEventstream", ["test_xmls/eventstream_sample.xml"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("saveEventstream", ["test_xmls/saveEventstream_test.xml"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("addEventstream", ["eventstreamtest2", "eveventTest3"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("addEventstream", ["eventstreamtest1", "eveventTest", 0.1, "eveventTest3"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("removeEventstream", ["eventstreamtest2"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("showEventstream", ["eventstreamtest1"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("listEventstream", [], ["a"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("execEventstream", ["eventstreamtest1"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("recordEventstream", ["recordTest1"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("execEvent", ["eventTest3"], [])
        print CmdExecutor.execute(cmd)

        time.sleep(0.3)

        cmd = Cmd("execEventstream", ["eventstreamtest1"])
        print CmdExecutor.execute(cmd)

        time.sleep(0.7)

        cmd = Cmd("execEvent", ["eventTest3"], [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("doneEventstreamRecording", [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("showEventstream", ["recordTest1"], [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("loadBinding", ["test_xmls/keybinding_sample.xml"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("saveBinding", ["test_xmls/keybinding_savetest.xml"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("addBinding", ["bindingTest1", "Ctrl-K", "eveventstreamtest1"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("addBinding", ["bindingTest2", "A", "esrecordTest1"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("addBinding", ["bindingTest3", "B", "cmd\"switchBindingset main\""])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("removeBinding", ["bindingTest1"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("showBinding", ["bindingTest2"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("listBinding", [], ["a"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("execBinding", ["bindingTest2"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("execBinding", ["bindingTest3"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("execBindingWithKey", ["B"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("loadBindingset", ["test_xmls/bindingset_sample.xml"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("saveBindingset", ["test_xmls/bindingset_save_test.xml"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("newBindingset", ["bindingTest"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("removeBindingset", ["bindingTest"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("showBindingset", ["bindingSet2"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("listBindingset", [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("currentBindingset", [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("switchBindingset", ["bindingSet1"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("currentBindingset", [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("execScript", ["test_xmls/script_sample.xml"], [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("startGui", ["test_xmls/gui_keylayout_sample.xml"])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("startGuiAutoRefresh", [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("stopGuiAutoRefresh", [])
        print CmdExecutor.execute(cmd)

        cmd = Cmd("stopGui", [])
        print CmdExecutor.execute(cmd)

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
    userInput = "listEvent -abc -b -dc testarg testarg2 arg\"this is enclosing\" arg2"
    cmd = CmdParser.parse(userInput)
    compare = Cmd("listEvent", ["testarg", "testarg2", "arg\"this is enclosing\"", "arg2"], ["abc", "b", "dc"])
    if not Cmd.equals(compare, cmd):
        print "Fail test 5"
        print "cmd : ", cmd
        print "compare : ", compare
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
