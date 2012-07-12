# Module for device control.
# Author : SeongJae Park <sj38.park@gmail.com>

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage

import log
import os
import socket
import threading
import time

import directControl

TAG = "Ash_deviceControl"
CONNECTION_TIMEOUT = 10
AGI_CONNECTION_LIMIT = 150

AGI_CONN_PORT_HEAD = 6789
AGI_CONN_PORT_TAIL = 8789
agiConnectionPort = AGI_CONN_PORT_HEAD
connectedDevices = []
devConnListener = None
stopAutoConnectionFlag = True

# size for virtual screen.
#Axis recalculated to fit on this screen when touch, drag command comes.
virtualScrSize = [320, 480]

class Device:
    serialno = None
    mdevice = None
    socket = None
    virtualScrRatio = None
    screenSize = None
    productName = None
    focused = None

    def __init__(self):
        pass

    def __init__(self, serial, mdev, sock, ratio, screenSize, name):
        self.serialno = serial
        self.mdevice = mdev
        self.socket = sock
        self.virtualScrRatio = ratio
        self.screenSize = screenSize
        self.productName = name

    def __str__(self):
        return "[Device] name : %s serialno : %s mdevice : %s socket : %s virtualScrRatio : %s screenSize : %s" % (self.productName, self.serialno, self.mdevice, self.socket, self.virtualScrRatio, self.screenSize)

    def __repr__(self):
        return self.__str__()

def listDevices(opts=[]):
    if "ash" in opts:
        result = []
        for device in connectedDevices:
            if "serial" in opts:
                result.append(device.serialno)
            else:
                result.append([device.productName, device.serialno])
        return result
    return _getUsbConnectedDevices()

def startAutoConnection():
    global stopAutoConnectionFlag
    stopAutoConnectionFlag = False
    DevicePNPerThread().start()

def stopAutoConnection():
    global stopAutoConnectionFlag
    stopAutoConnectionFlag = True

def _connectTo(serialnos):
    global connectedDevices

    newConnectedDevices = []
    reusedSockets = []
    changed = False
    for serialno in serialnos:
        reused = False
        # Recycling is a good habit.
        for dev in connectedDevices:
            if serialno == dev.serialno:
                newConnectedDevices.append(dev)
                reusedSockets.append(dev.socket)
                reused = True
                break
        if not reused:
            changed = True
            mdevice = MonkeyRunner.waitForConnection(CONNECTION_TIMEOUT, serialno)

            width = mdevice.getProperty("display.width")
            height = mdevice.getProperty("display.height")
            resolScaleRatioX = float(width) / virtualScrSize[0]
            resolScaleRatioY = float(height) / virtualScrSize[1]
            resolScaleRatio = (resolScaleRatioX, resolScaleRatioY)

            name = mdevice.getProperty("build.model")

            socket = _connectAgi(serialno)

            device = Device(serialno, mdevice, socket, resolScaleRatio, (width, height),
                    name)
            newConnectedDevices.append(device)
    # Close sockets for unplugged device
    for device in connectedDevices:
        if device.socket in reusedSockets:
            continue
        changed = True
        if device.socket:
            device.socket.close()

    if changed:
        connectedDevices = newConnectedDevices
        nofocus = True
        for device in connectedDevices:
            if device.focused:
                nofocus = False
                break
        if nofocus and len(connectedDevices) > 0:
            connectedDevices[0].focused = True
#       notifyCurrentDevices()
        print "new connected devices are : ", newConnectedDevices

class DevicePNPerThread(threading.Thread):
    def run(self):
        while(1):
            if stopAutoConnectionFlag:
                break
            usbConnected = _getUsbConnectedDevices()
            _connectTo(usbConnected)

            time.sleep(1)

def _getUsbConnectedDevices():
    f = os.popen("adb devices")
    results = f.readlines()
    f.close()
    parsed = []
    for result in results[1:-1]:
        parsed.append(result.split()[0])
    return parsed

def _connectAgi(serialno):
    log.i(TAG, "Connect AGI at " + serialno)
    result = None
    for i in range(AGI_CONNECTION_LIMIT):
        try:
            result = _doConnectAgi(serialno)
        except Exception, e:
            if i == AGI_CONNECTION_LIMIT:
                # TODO Cleanup this device from device list.
                log.e(TAG, "Failed to connect AGI.")
    return result

def _doConnectAgi(serialno):
    global agiConnectionPort
    agiConnectionPort += 1
    if agiConnectionPort > AGI_CONN_PORT_TAIL:
        agiConnectionPort = AGI_CONN_PORT_HEAD
    cmd = "adb -s %s forward tcp:%d tcp:9991" % (serialno, agiConnectionPort)
    os.popen(cmd)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect(("127.0.0.1", agiConnectionPort))
    return sock

def calcAxis(xy, device):
    xy[0] = int(xy[0] * device.virtualScrRatio[0])
    xy[1] = int(xy[1] * device.virtualScrRatio[1])
    return xy

# SHOW <x axis> <y axis> ["pressed"]
def showCursor(x, y, isPressed):
    for device in connectedDevices:
        if not device.focused:
            continue
        xy = calcAxis([x, y], device)
        sock = device.socket
        query = "SHOW %d %d" % (xy[0], xy[1])
        if isPressed:
            query += " pressed"
        length = "%03d" % len(query)
        try:
            sock.sendall(length)
            sock.sendall(query)
        except Exception, e:
            log.e(TAG, "Fail to send query to AGI! Connect again.", e)
            sock.close()
            device.sock = _connectAgi(device.serialno)

# HIDE
def hideCursor():
    for device in connectedDevices:
        if not device.focused:
            continue
        sock = device.socket
        query = "HIDE"
        length = "%03d" % len(query)
        try:
            sock.sendall(length)
            sock.sendall(query)
        except Exception, e:
            log.e(TAG, "Fail to send query to AGI! Connect again.", e)
            sock.close()
            device.sock = _connectAgi(device.serialno)

# @param    name    serial_no of device.
def connect(name):
    devices = _getUsbConnectedDevices()

    nameConnected = False
    for device in devices:
        if device == name:
            nameConnected = True
            break
    if not nameConnected:
        return "No usb connected device with name %s." % name

    _connectTo([name])

def focus(indexs):
    for i in range(len(connectedDevices)):
        if i in indexs:
            connectedDevices[i].focused = True
        else:
            connectedDevices[i].focused = False

def focusTo(direction):
    if not direction in ["left", "right"]:
        return "Direction is wrong!"
    nextFocus = []
    connectedDevicesLen = len(connectedDevices)
    for device in connectedDevices:
        if device.focused:
            target = 0
            if direction == "left":
                target = connectedDevices.index(device) + 1
            else:
                target = connectedDevices.index(device) - 1
            if target > 0 and target < connectedDevicesLen:
                nextFocus.append(target)
            if target < 0:
                return "Can't focus to right side"
    if len(nextFocus) <= 0:
        return "No more device to move focus!"
    focus(nextFocus)


def setVirtualScreen(width, height):
    global virtualScrSize
    if width <= 0 or height <= 0:
        return "Width and Height should be bigger than 0"
    virtualScrSize = [width, height]
    for device in connectedDevices:
        ratioX = float(device.screenSize[0]) / virtualScrSize[0]
        ratioY = float(device.screenSize[1]) / virtualScrSize[1]
        device.virtualScrRatio = (ratioX, ratioY)

def touch(x, y, action, onVirtualAxis = False):
    for device in connectedDevices:
        if not device.focused: continue
        if onVirtualAxis:
            xy = calcAxis([x, y], device)
            x = xy[0]
            y = xy[1]
        try:
            device.mdevice.touch(x, y, eval("MonkeyDevice.%s" % action))
        except BaseException, e:
            log.e(TAG, "Unexpected exception while touch.", e)
            raise

def keyPress(keyCode, action):
    for device in connectedDevices:
        if not device.focused: continue
        try:
            device.mdevice.press("KEYCODE_%s" % keyCode, eval("MonkeyDevice.%s" % action))
        except BaseException, e:
            log.e(TAG, "Unexpected exception while keypress.", e)
            raise

def drag(xys, duration, onVirtualAxis = False):
    if len(xys) < 4: return "drag called with xys that element is less than 4."
    for device in connectedDevices:
        if not device.focused: continue
        if onVirtualAxis:
            xy1 = calcAxis([xys[0], xys[1]], device)
            xy2 = calcAxis([xys[2], xys[3]], device)
            xys = [xy1[0], xy1[1], xy2[0], xy2[1]]
        try:
            device.mdevice.drag((xys[0], xys[1]), (xys[2], xys[3]), duration)
        except BaseException, e:
            log.e(TAG, "Unexpected exception while drag.", e)
            raise

def type(text):
    if len(text) <= 0: return "type called with no text"
    for device in connectedDevices:
        if not device.focused: continue
        try:
            device.mdevice.type(text)
        except BaseException, e:
            log.e(TAG, "Unexpected exception while type.", e)
            raise

def wake():
    for device in connectedDevices:
        if not device.focused: continue
        try:
            device.mdevice.wake()
        except BaseException, e:
            log.e(TAG, "Unexpected exception while wake.", e)
            raise

def reboot():
    for device in connectedDevices:
        if not device.focused: continue
        try:
            device.mdevice.reboot()
        except BaseException, e:
            log.e(TAG, "Unexpected exception while reboot.", e)
            raise

def getProperty(prop):
    if len(prop) <= 0 : return "getProperty called with no prop name"
    result = []
    for device in connectedDevices:
        if not device.focused: continue
        try:
            result.append(device.mdevice.getProperty(prop))
        except BaseException, e:
            log.e(TAG, "Unexpected exception while getProp.", e)
            raise

def shell(command):
    if len(command) <= 0 : return "shell called with no command"
    for device in connectedDevices:
        if not device.focused: continue
        try:
            return device.mdevice.shell(command)
        except BaseException, e:
            log.e(TAG, "Unexpected exception while shell.", e)
            raise

# Do for only first focused device.
def snapshot(filePath):
    for device in connectedDevices:
        if not device.focused: continue
        try:
            snapshot = device.mdevice.takeSnapshot()
            if len(filePath) <= 0 : return snapshot
            snapshot.writeToFile(filePath, "png")
            return
        except BaseException, e:
            log.e(TAG, "Unexpected exception while takeSnapshot.", e)
            raise

