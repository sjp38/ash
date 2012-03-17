# Module for device control.
# Author : SeongJae Park <sj38.park@gmail.com>

import os
import log
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage

TAG = "Ash_deviceControl"
CONNECTION_TIMEOUT = 10

connectedDevice = None

def getConnectedDevices():
    f = os.popen("adb devices")
    results = f.readlines()
    f.close()
    parsed = []
    for result in results[1:-1]:
        parsed.append(result.split()[0])
    return parsed

def connect(name):
    devices = getConnectedDevices()

    nameConnected = False
    for device in devices:
        if device == name:
            nameConnected = True
            break
    if not nameConnected:
        return "No connected device with name %s." % name

    global connectedDevice
    connectedDevice = MonkeyRunner.waitForConnection(CONNECTION_TIMEOUT, name)

def touch(x, y, action):
    if not connectedDevice : return "Device not connected."
    try:
        connectedDevice.touch(x, y, eval("MonkeyDevice.%s" % action))
    except BaseException, e:
        log.e(TAG, "Unexpected exception while touch.", e)
        raise

def keyPress(keyCode, action):
    if not connectedDevice : return "Device not connected."
    try:
        connectedDevice.press("KEYCODE_%s" % keyCode, eval("MonkeyDevice.%s" % action))
    except BaseException, e:
        log.e(TAG, "Unexpected exception while keypress.", e)
        raise

def drag(xys, duration):
    if not connectedDevice : return "Device not connected."
    if len(xys) < 4: return "drag called with xys that element is less than 4."
    try:
        connectedDevice.drag((xys[0], xys[1]), (xys[2], xys[3]), duration)
    except BaseException, e:
        log.e(TAG, "Unexpected exception while drag.", e)
        raise

def type(text):
    if not connectedDevice : return "Device not connected."
    if len(text) <= 0: return "type called with no text"
    try:
        connectedDevice.type(text)
    except BaseException, e:
        log.e(TAG, "Unexpected exception while type.", e)
        raise

def wake():
    if not connectedDevice : return "Device not connected."
    try:
        connectedDevice.wake()
    except BaseException, e:
        log.e(TAG, "Unexpected exception while wake.", e)
        raise

def reboot():
    if not connectedDevice : return "Device not connected."
    try:
        connectedDevice.reboot()
    except BaseException, e:
        log.e(TAG, "Unexpected exception while reboot.", e)
        raise

def getProperty(prop):
    if not connectedDevice : return "Device not connected."
    if len(prop) <= 0 : return "getProperty called with no prop name"
    try:
        connectedDevice.getProperty(prop)
    except BaseException, e:
        log.e(TAG, "Unexpected exception while getProp.", e)
        raise

def shell(command):
    if not connectedDevice : return "Device not connected."
    if len(command) <= 0 : return "shell called with no command"
    try:
        connectedDevice.shell(command)
    except BaseException, e:
        log.e(TAG, "Unexpected exception while shell.", e)
        raise

def snapshot(filePath):
    if not connectedDevice : return "Device not connected."
    if len(filePath) <= 0 : return "snapshot called with no file path"
    try:
        snapshot = connectedDevice.takeSnapshot()
        snapshot.writeToFile(filePath, "png")
    except BaseException, e:
        log.e(TAG, "Unexpected exception while takeSnapshot.", e)
        raise




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
#        raise
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

def testKeyPress():
    print "test keyPress"
    try:
        keyPress("A", "DOWN_AND_UP")
    except:
#        raise
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

# Success if execute with no exception.
def testGetConnectedDevices():
    print "test getConnectedDevices"
    try:
        getConnectedDevices()
    except:
        return True
    return False

# Success if execute with no exception.
def testConnect():
    print "test connect"
    try :
        connect("test")
    except:
        return True
    return False


def testModule():
    result = testGetConnectedDevices()
    if result:
        print "Fail! ", result
        return

    result = testConnect()
    if result:
        print "Fail! ", result
        return

    global connectedDevice
    connectedDevice = MonkeyRunner.waitForConnection()

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
