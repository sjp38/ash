#!/usr/bin/env monkeyrunner
from device_control import *
import device_control

from java.lang import System
if System.getProperty("os.name").startswith("Windows"):
    import os
    import sys
    srcFileDir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(srcFileDir)
    sys.path = [srcFileDir] + sys.path

# Test
def testSnapshot():
    print "test snapshot"
    if not snapshot(""):
        print "case 1"
        return True
    try:
        snapshot("test.png")
    except:
        return True
    return False

def testShell():
    print "test shell"
    if not shell(""):
        print "case 1"
        return True
    try:
        shell("ls -l")
    except:
        return True
    return False

def testGetProperty():
    print "test getProperty"
    if not getProperty(""):
        print "case 1"
        return True
    try:
        getProperty("display.width")
    except:
        return True
    return False

def testReboot():
    print "test reboot"
    try:
        reboot()
    except:
        return True
    return False

def testWake():
    print "test wake"
    try:
        wake()
    except:
        return True
    return False

def testType():
    print "test type"
    result = type("")
    if not result:
        print "case 1"
        return True
    try:
        type("abcd")
    except:
        print "exception"
        raise
        return True
    return False

def testDrag():
    print "test drag"
    try:
        drag((100,100,400,400), 1.0)
    except:
        print "exception!"
#        raise
        return True

    try:
        drag((100,100,400,400), 1.0, True)
    except:
        print "case 2!"
#        raise
        return True

def testKeyPress():
    print "test keyPress"
    try:
        keyPress("A", "DOWN_AND_UP")
    except:
#        raise
        return True

def testSetVirtualScreen():
    print "test setVirtualScreen"
    try:
        setVirtualScreen(800, 480)
    except:
        print "case 1"
        raise
        return True

    try:
        setVirtualScreen(-1, -1)
    except:
        print "case 2"
        #raise
        return True

def testTouch():
    print "testTouch"
    try:
        touch(100, 200, "UP")
    except:
        print "case 1"
#        raise
        return True
    try:
        # float to int just make warning.
        touch(10.0, 20.5, "UP")
    except:
        print "case 2"
#        raise
        return True

    try:
        touch(100, 200, "ABCD")
        print "case 3"
        return True
    except:
        pass

    try:
        touch(100, 200, "UP", True)
    except:
        print "case 4"
        return True

# Success if execute with no exception.
def testListDevices():
    print "test listDevices"
    try:
        print listDevices([])
        print listDevices(["ash"])
        print listDevices(["ash", "serial"])
    except:
        return True
    return False

# Success if execute with no exception.
def testConnect():
    print "test connect"
    try :
        connect("test")
    except:
        raise
        return True
    return False

def testStartAutoConnection():
    print "test startAutoConnection"
    try :
        startAutoConnection()
        time.sleep(5)
    except:
        raise
        return True
    return False

def testStopAutoConnection():
    print "test stopAutoConnection"
    try :
        stopAutoConnection()
    except:
        return True
    return False

def testShowCursor():
    print "test showCursor"
    try :
        showCursor(10, 20, True)
    except:
        return True
    return False

def testHideCursor():
    print "test hideCursor"
    try :
        hideCursor()
    except:
        return True
    return False


def testModule():
    result = testStartAutoConnection()
    if result:
        print "Fail! ", result
        return

    result = testStopAutoConnection()
    if result:
        print "Fail! ", result
        return

    result = testShowCursor()
    if result:
        print "Fail! ", result
        return

    result = testHideCursor()
    if result:
        print "Fail! ", result
        return

    result = testListDevices()
    if result:
        print "Fail! ", result
        return

    result = testConnect()
    if result:
        print "Fail! ", result
        return

    startAutoConnection()
    time.sleep(5)

    result = testSetVirtualScreen()
    if result:
        print "Fail!", result
        return

    result = testTouch()
    if result:
        print "Fail! ", result
        return

    result = testKeyPress()
    if result:
        print "Fail! ", result
        return

    result = testDrag()
    if result:
        print "FAil! ", result
        return

    result = testType()
    if result:
        print "Fail! ", result
        return

    result = testWake()
    if result:
        print "Fail! ", result
        return

#    result = testReboot()
    if result:
        print "Fail! ", result
        return

    result = testGetProperty()
    if result:
        print "Fail!", result
        return

    result = testShell()
    if result:
        print "Fail!", result
        return

    result = testSnapshot()
    if result:
        print "Fail!", result
        return

    print "Success!"

if __name__ == "__main__":
    testModule()
