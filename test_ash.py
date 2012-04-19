# Path setting for Damn Windows.
import sys
import os
srcFileDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(srcFileDir)
sys.path = [srcFileDir] + sys.path

from ash import *
import time


def testExecution():
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
            "stopGui"
            ]
    try:
        for cmd in testcmds:
            print "\ncmd : ", cmd
            parseAndExecute(cmd)

    except:
        print "FAIL!"
    print "SUCCESS!"



if __name__ == "__main__":
    testExecution()
