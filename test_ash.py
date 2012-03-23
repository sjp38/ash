from ash import *
import time


def testExecution():
    try:
        cmd = "listDevices"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "connectDevice test"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "loadEvent test_xmls/event_sample.xml"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "sleep 0.2"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "saveEvent test_xmls/saveEventTest.xml"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "addEvent eventTest touch -x1100 -y1200 -actDOWN_AND_UP"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "addEvent eventTest2 press -argA -actDOWN"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "addEvent eventTest3 drag -x1100 -y1200 -x2400 -y2200 -dur1.0"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "removeEvent eventTest2"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "showEvent eventTest"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "listEvent"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "execEvent eventTest3"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "execInstEvent touch -x1100 -y1200 -actDOWN_AND_UP"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "loadEventstream test_xmls/eventstream_sample.xml"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "saveEventstream test_xmls/saveEventstream_test.xml"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "addEventstream eventstreamtest2 eveventTest3"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "addEventstream eventstreamtest1 eveventTest 0.1 eveventTest3"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "removeEventstream eventstreamtest2"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "showEventstream eventstreamtest1"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "listEventstream -a"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "execEventstream eventstreamtest1"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "recordEventstream recordTest1"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        time.sleep(0.7)

        cmd = "execEventstream eventstreamtest1"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        time.sleep(0.7)

        cmd = "execEvent eventTest3"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "doneEventstreamRecording"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "showEventstream recordTest1"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "loadBinding test_xmls/keybinding_sample.xml"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "saveBinding test_xmls/keybinding_savetest.xml"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "addBinding bindingTest1 Ctrl-K eveventstreamtest1"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "addBinding bindingTest2 A esrecordTest1"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "addBinding bindingTest3 B cmd\"switchBindingset main\""
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "removeBinding bindingTest1"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "showBinding bindingTest2"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "listBinding -a"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "execBinding bindingTest2"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "execBinding bindingTest3"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "execBindingWithKey B"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "loadBindingset test_xmls/bindingset_sample.xml"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "saveBindingset test_xmls/bindingset_save_test.xml"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "newBindingset bindingTest"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "removeBindingset bindingTest"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        parseAndExecute("listBindingset")

        cmd = "showBindingset bindingSet2"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "listBindingset"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "currentBindingset"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "switchBindingset bindingSet1"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "currentBindingset"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "execScript test_xmls/script_sample.xml"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "startGui test_xmls/gui_keylayout_sample.xml"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "startGuiAutoRefresh"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "stopGuiAutoRefresh"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

        cmd = "stopGui"
        print "\ncmd : ", cmd
        parseAndExecute(cmd)

    except:
        print "FAIL!"
    print "SUCCESS!"



if __name__ == "__main__":
    testExecution()
