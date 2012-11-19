#!/usr/bin/env monkeyrunner
# Devices manager.
# Manage devices connection and devices control.
# Provide devices connection PnP feature, too.
# Author : SeongJae Park <sj38.park@gmail.com>
# License : GPLv3

import os
import socket
import threading
import time

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage
from java.awt import Robot, Toolkit
from java.awt.event import InputEvent, KeyEvent

import ash
import ashmon

TYPE_ANDROID = "android"
TYPE_PC = "pc"
CONNECT_FAIL = "Fail to connect"
FOCUS_FAIL = "Fail to focus"

MONK_CONN_TIMEOUT = 10
_AGI_CONN_LIMIT = 150
_AGI_CONN_PORT_HEAD = 6789
_AGI_CONN_PORT_TAIL = 9789
_agi_conn_port = _AGI_CONN_PORT_HEAD

_DEVMGR_PORT = 10101

DEV_TYPE_INDX = 0
DEV_ID_INDX = 1
DEV_NAME_INDX = 2
DEV_CONN_INDX = 3
DEV_FOCUSED_INDX = 4
DEV_RESOL_INDX = 5

# device is list of type, id, name, connections, focused, resolution.
# type is "android" or "pc"
# id is address for device. ip or serial #.
# name is product name or PC host name.
# connections is connections for device control.
# If PC, just one socket to pc_controller.
# If Android, list of MonkeyDevice and AGI connected socket.
# focused is whether this device will be controlled.
# resolution is screen resolution

_devices = []
_stop_device_lookup_thread = False

robot = Robot()
_stop_accepting = False
_stop_listening = False
waiter_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
waiter_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
waiter_sock.bind(('', _DEVMGR_PORT))
waiter_sock.listen(1)

dimension = Toolkit.getDefaultToolkit().getScreenSize()
_resolution = [dimension.width, dimension.height]

def devices():
    f = os.popen("adb devices")
    results = f.readlines()
    f.close()
    parsed = []
    for result in results[1:-1]:
        devid = result.split()[0]
        f = os.popen("adb -s %s shell getprop ro.product.model" % devid)
        name = f.readlines()[0][0:-1]
        f.close()

        parsed.append("%s\t%s\t%s" % (TYPE_ANDROID, devid, name))
    #TODO: See PCs.
    return parsed

def connected_devices(develop_view=None):
    results = []
    for device in _devices:
        if develop_view:
            results.append("%s %s %s %s, %s, %s" % (
                device[DEV_TYPE_INDX], device[DEV_ID_INDX],
                device[DEV_NAME_INDX], device[DEV_CONN_INDX],
                device[DEV_FOCUSED_INDX], device[DEV_RESOL_INDX]))
        else:
            focused = ""
            if device[DEV_FOCUSED_INDX]:
                focused = "[focused]"
            results.append("%s %s %s" %
                    (focused, device[DEV_TYPE_INDX], device[DEV_NAME_INDX]))
    return results

def _convert_arg(arg, type_, range_):
    if isinstance(arg, type_):
        return arg
    try:
        arg = type_(arg)
    except:
        return "argument is not %s" % type_
    if range_ and (arg < range_[0] or arg > range_[1]):
        return "argument is not in range of %d, %d" % (range_[0], range_[1])
    return arg

def _connect_agi(id_):
    result = None
    for i in range(_AGI_CONN_LIMIT):
        try:
            result = _do_connect_agi(id_)
        except Exception, e:
            print "exception!!!"
            if i == _AGI_CONN_LIMIT:
                # TODO Cleanup this device from device list.
                print "Failed to connect AGI."
    return result

def _do_connect_agi(id_):
    global _agi_conn_port
    _agi_conn_port += 1
    if _agi_conn_port > _AGI_CONN_PORT_TAIL:
        _agi_conn_port = _AGI_CONN_PORT_HEAD
    cmd = "adb -s %s forward tcp:%d tcp:9991" % (id_, _agi_conn_port)
    os.popen(cmd)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect(("127.0.0.1", _agi_conn_port))
    return sock

# If specified device is already connected, recycle and return True
# else, return False
def _recycle_connected(device_id):
    for i in range(len(_devices)):
        device = _devices[i]
        if device[DEV_ID_INDX] == device_id:
            del _devices[i]
            _devices.append(device)
            return True
    return False

# Connect devmgr of ash at type_, devid.
def _connect_devmgr(devid, type_):
    if _recycle_connected(devid):
        return
    if type_ == TYPE_ANDROID:
        # TODO: Connect android via ip. Currently, only serial.
        mdev = MonkeyRunner.waitForConnection(MONK_CONN_TIMEOUT, devid)
        #TODO: Install/start AGI from here
        agiconn = _connect_agi(devid)
        focused = False
        name = mdev.getProperty("build.model")
        resolution = [int(mdev.getProperty("display.width")),
                int(mdev.getProperty("display.height"))]
        _devices.append([TYPE_ANDROID, devid, name,
                [mdev, agiconn], focused, resolution])
    elif type_ == TYPE_PC:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((devid, _DEVMGR_PORT))
        _devices.append([TYPE_PC, devid, devid, [sock], False, [1024, 768]])

# if type_ is none, id_ is just index from devices list.
def connect(id_, type_=None):
    if not type_:
        devices_ = devices()
        nth = _convert_arg(id_, int, (0, len(devices_) - 1))
        if not isinstance(nth, int):
            return "%s : %s" % (CONNECT_FAIL, nth)

        dev_base_info = devices_[nth].split()
        devid = dev_base_info[1]
        # TODO: Support PC connection via index, too.
        _connect_devmgr(devid, TYPE_ANDROID)
    else:
        return _connect_devmgr(id_, type_)

# focus with no argument is same as clear focus.
def focus(*nths):
    will_focuses = []
    for nth in nths:
        nth = _convert_arg(nth, int, (0, len(_devices) - 1))
        if not isinstance(nth, int):
            return "%s : %s" % (FOCUS_FAIL, nth)

        will_focuses.append(nth)
    for device in _devices:
        device[DEV_FOCUSED_INDX] = False
    for i in will_focuses:
        _devices[i][DEV_FOCUSED_INDX] = True

def _control_android(collect_result, lambda_, *args):
    results = []
    for dev in _devices:
        if dev[DEV_TYPE_INDX] != TYPE_ANDROID:
            continue
        if dev[4]:
            results.append(lambda_(dev[DEV_CONN_INDX][0], args,
                dev[DEV_RESOL_INDX]))
    if collect_result:
        return results

def drag(x1, y1, x2, y2, percentage=False, duration=0.1, steps=10):
    if percentage == "False":
        percentage = False
    if percentage:
        x1 = _convert_arg(x1, float, None) / 100.0
        y1 = _convert_arg(y1, float, None) / 100.0
        x2 = _convert_arg(x2, float, None) / 100.0
        y2 = _convert_arg(y2, float, None) / 100.0
    else:
        x1 = _convert_arg(x1, int, None)
        y1 = _convert_arg(y1, int, None)
        x2 = _convert_arg(x2, int, None)
        y2 = _convert_arg(y2, int, None)
    duration = _convert_arg(duration, float, None)
    steps = _convert_arg(steps, int, None)
    if percentage:
        _control_android(False,
                lambda x,y,z: x.drag((int(y[0] * z[0]), int(y[1] * z[1]),),
                    (int(y[2] * z[0]), int(y[3] * z[1])), y[4], y[5]),
                x1, y1, x2, y2, duration, steps)
        return
    _control_android(False,
            lambda x,y,z: x.drag((y[0], y[1]), (y[2], y[3]), y[4], y[5]),
            x1, y1, x2, y2, duration, steps)

def get_property(key):
    return _control_android(True,
            lambda x,y,z: x.getProperty(y[0]),
            key)

def get_system_property(key):
    return _control_android(True,
            lambda x,y,z: x.getSystemProperty(y[0]),
            key)

def install_package(path):
    _control_android(False, lambda x,y,z: x.installPackage(y[0]), path)

def press(type_, name):
    name = "KEYCODE_%s" % name
    type_ = eval("MonkeyDevice.%s" % type_)
    _control_android(False, lambda x,y,z: x.press(y[0], y[1]), name, type_)

def reboot(bootload_type):
    _control_android(False, lambda x,y,z: x.reboot(y[0]), bootload_type)

def remove_package(package):
    _control_android(False, lambda x,y,z: x.remove_package(y[0]), package)

def shell(*cmd):
    cmd = " ".join(cmd)
    return _control_android(True, lambda x,y,z: x.shell(y[0]), cmd)

def take_snapshot(path=None):
    if not path:
        now = time.localtime()
        path = "ash_snapshot_%04d-%02d-%02d-%02d-%02d-%02d" % (
                now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    results = _control_android(True, lambda x,y,z: x.takeSnapshot())
    for i in range(len(results)):
        result = results[i]
        result.writeToFile("%s_%d" % (path, i), "png")

def touch(type_, x, y, percentage=False):
    if percentage == "False":
        percentage = False
    type_ = eval("MonkeyDevice.%s" % type_)
    if percentage:
        x = _convert_arg(x, float, None) / 100
        y = _convert_arg(y, float, None) / 100
        _control_android(False, lambda x,y,z: x.touch(
                int(y[0] * z[0]), int(y[1] * z[1]), y[2]), x, y, type_)
        return
    x = _convert_arg(x, int, None)
    y = _convert_arg(y, int, None)
    _control_android(False, lambda x,y,z: x.touch(y[0], y[1], y[2]), x, y, type_)

def show_cursor(x, y, percentage=False, pressed=False):
    if percentage == "False":
        percentage = False
    if percentage:
        x = _convert_arg(x, float, None) / 100
        y = _convert_arg(y, float, None) / 100
    else:
        x = _convert_arg(x, int, None)
        y = _convert_arg(y, int, None)

    for device in _devices:
        if device[DEV_FOCUSED_INDX]:
            if percentage:
                query = "SHOW %d %d" % (int(x * device[DEV_RESOL_INDX][0]),
                        int(y * device[DEV_RESOL_INDX][1]))
            else:
                query = "SHOW %d %d" % (x, y)
            if pressed:
                query += " pressed"
            length = "%03d" % len(query)
            try:
                device[DEV_CONN_INDX][1].sendall(length)
                device[DEV_CONN_INDX][1].sendall(query)
            except:
                print "Fail to sen AGI query! connect again"
                if device[DEV_CONN_INDX][1]:
                    device[DEV_CONN_INDX][1].close()
                    device[DEV_CONN_INDX][1] = _connect_agi(device[1])

def hide_cursor():
    for device in _devices:
        if device[DEV_FOCUSED_INDX]:
            query = "HIDE"
            length = "%03d" % len(query)
            try:
                device[DEV_CONN_INDX][1].sendall(length)
                device[DEV_CONN_INDX][1].sendall(query)
            except:
                print "Fail to send AGI query! connect again"
                if device[DEV_CONN_INDX][1]:
                    device[DEV_CONN_INDX][1].close()
                    device[DEV_CONN_INDX][1] = _connect_agi(device[1])

def wake():
    _control_android(False, lambda x,y,z: x.wake())

def _control_pc(collect_result, expr):
    results = []
    for dev in _devices:
        if dev[DEV_TYPE_INDX] != TYPE_PC:
            continue
        if dev[DEV_FOCUSED_INDX]:
            sock = dev[DEV_CONN_INDX][0]
            sock.sendall(expr + ashmon.END_OF_MSG)
            tokens = ''
            while True:
                received = sock.recv(1024)
                if not received:
                    print "connection with devmgrmon crashed!"
                    sock.close()
                msgs, tokens = ashmon.get_complete_message(received, tokens)
                for msg in msgs:
                    result = eval(msg)
                    break
    if collect_result:
        return results

# If target_me, control me.
# If not, control connected devices.
def move_mouse(x, y, percentage=False, target_me=False):
    if not target_me:
        return _control_pc(False, "move_mouse %s %s %s True" % (
                x, y, percentage))
    if percentage == "False":
        percentage = False
    if percentage:
        x = _convert_arg(x, float, None) / 100 * _resolution[0]
        y = _convert_arg(y, float, None) / 100 * _resolution[1]
    else:
        x = _convert_arg(x, int, None)
        y = _convert_arg(y, int, None)

    robot.mouseMove(int(x), int(y))

def press_mouse(right_button=False, target_me=False):
    if not target_me:
        return _control_pc(False, "press_mouse %s True" % (right_button))
    button = InputEvent.BUTTON1_MASK
    if eval(right_button):
        button = InputEvent.BUTTON3_MASK
    robot.mousePress(button)

def release_mouse(right_button=False, target_me=False):
    if not target_me:
        return _control_pc(False, "release_mouse %s True" % (right_button))
    button = InputEvent.BUTTON1_MASK
    if eval(right_button):
        button = InputEvent.BUTTON3_MASK
    robot.mouseRelease(button)

def wheel_mouse(notches, target_me=False):
    if not target_me:
        return _control_pc(False, "wheel_mouse %s True" % notches)
    robot.mouseWheel(int(eval(notches)))

def press_key(keycode, target_me=False):
    if not target_me:
        return _control_pc(False, "press_key %s True" % keycode)
    robot.keyPress(eval("KeyEvent.VK_%s" % keycode))

def release_key(keycode, target_me=False):
    if not target_me:
        return _control_pc(False, "release_key %s True" % keycode)
    robot.keyRelease(eval("KeyEvent.VK_%s" % keycode))

def start_devmgrmon():
    _stop_listening = False
    _stop_accepting = False
    acceptor = _AcceptorThread()
    acceptor.start()

class _AcceptorThread(threading.Thread):
    def run(self):
        global waiter_sock
        while True:
            if _stop_accepting:
                global _stop_listening
                _stop_listening = False
                break
            conn, addr = waiter_sock.accept()
            print "devmgr connected by ash. start listener"
            listener = _ListenerThread(conn)
            listener.start()

class _ListenerThread(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        tokens = ''
        while True:
            if _stop_listening:
                break
            received = self.conn.recv(1024)
            if not received:
                print "devmgr not received! stop listening!"
                break
            msgs, tokens = ashmon.get_complete_message(received, tokens)
            for msg in msgs:
                result = ash.input(msg)
                self.conn.sendall("%s%s" % (result, ashmon.END_OF_MSG))
        self.conn.close()


# Device connection lookup thread.
class _DeviceLookupThread(threading.Thread):
    def run(self):
        while True:
            if _stop_device_lookup_thread: break
            #TODO: get current physically connected device, connect logically.
