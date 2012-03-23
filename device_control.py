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
        return connectedDevice.getProperty(prop)
    except BaseException, e:
        log.e(TAG, "Unexpected exception while getProp.", e)
        raise

def shell(command):
    if not connectedDevice : return "Device not connected."
    if len(command) <= 0 : return "shell called with no command"
    try:
        return connectedDevice.shell(command)
    except BaseException, e:
        log.e(TAG, "Unexpected exception while shell.", e)
        raise

def snapshot(filePath):
    if not connectedDevice : return "Device not connected."
    try:
        snapshot = connectedDevice.takeSnapshot()
        if len(filePath) <= 0 : return snapshot
        snapshot.writeToFile(filePath, "png")
    except BaseException, e:
        log.e(TAG, "Unexpected exception while takeSnapshot.", e)
        raise

