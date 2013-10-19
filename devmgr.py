#!/usr/bin/env monkeyrunner

"""Devices manager.
Manage devices connection and devices control.
Provide devices connection PnP feature, too."""

__author__ = "SeongJae Park"
__email__ = "sj38.park@gmail.com"
__copyright__ = "Copyright (c) 2011-2013, SeongJae Park"
__license__ = "GPLv3"

import os
import socket
import threading
import time

import ashmon

class _Device:
    """
Abstract class for device
    Concrete device may be Android device or PC or any other device.

Field
    type_: type of device
        e.g., "android", "pc"
    addr: tuple for address of device in form of (<value> <address type>).
        e.g., ("10.0.0.1", "ip"), ("+82-10-1234-4567", "phone number")
    name: name of device.
        e.g., "Desktop of James", "tuna"
    ashconn: connection to ash on device
        It can be tcp/ip or bluetooth or anything.
        But, should able to use duck typing using read / write.
    focused: whether this device is focused
    """

    TYPE_ANDROID = "android"
    TYPE_PC = "pc"

    def __init__(self, type_, address, name, conn, focused):
        self.type_ = type_
        self.addr = address
        self.name = name
        self.ashconn = conn
        self.focused = focused

    def __str__(self):
        return """
[Device
    type: %s,
    address: %s,
    name: %s,
    ashconn: %s,
    focused: %s,
    resolution: %s]
""" %  (self.type_, self.addr, self.name, self.ashconn,
        self.focused, self.resolution)

    def __repr__(self):
        return self.__str__()

    def get_property(key):
        pass

    def shutdown(operation, delay):
        pass

    def shell(*cmd):
        pass

    def take_snapshot(path=None):
        pass

    def remove_package(package):
        "Android specific feature"
        pass

    def unlock_screen():
        pass

    def mouse(type_, x, y, percentage=False):
        pass

    def whell(notches):
        pass

    def press_key(type_, keycode):
        pass

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

_stop_accepting = False
_stop_listening = False
waiter_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
waiter_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
waiter_sock.bind(('', _DEVMGR_PORT))
waiter_sock.listen(1)

OFFICIAL_AGAIN_BY_VERSION3 = """
Hidden feature

Will be publicated again or deprecated officially by v3.0"""

def devices(scan_area="192.168.1", scan_port=ashmon.DEFAULT_PORT):
    "Scan devices"
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
    for i in range(256):
        ip = "%s.%d" % i
        if ashmon.connectable_with(ip):
            parsed.append("%s\t%s" % (TYPE_PC, ip))
    return parsed

def connected_devices(develop_view=None):
    return OFFICIAL_AGAIN_BY_VERSION3
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
            #print "exception!!!"
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
    return OFFICIAL_AGAIN_BY_VERSION3
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
    return OFFICIAL_AGAIN_BY_VERSION3
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
        if dev[DEV_FOCUSED_INDX]:
            results.append(lambda_(dev[DEV_CONN_INDX][0], args,
                dev[DEV_RESOL_INDX]))
    if collect_result:
        return results

def drag(x1, y1, x2, y2, percentage=False, duration=0.1, steps=10):
    return OFFICIAL_AGAIN_BY_VERSION3
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
    return OFFICIAL_AGAIN_BY_VERSION3
    return _control_android(True,
            lambda x,y,z: x.getProperty(y[0]),
            key)

def get_system_property(key):
    return OFFICIAL_AGAIN_BY_VERSION3
    return _control_android(True,
            lambda x,y,z: x.getSystemProperty(y[0]),
            key)

def install_package(path):
    return OFFICIAL_AGAIN_BY_VERSION3
    _control_android(False, lambda x,y,z: x.installPackage(y[0]), path)

def press(type_, name):
    """Press down or up a button or key"""
    return OFFICIAL_AGAIN_BY_VERSION3
    name = "KEYCODE_%s" % name
    type_ = eval("MonkeyDevice.%s" % type_)
    _control_android(False, lambda x,y,z: x.press(y[0], y[1]), name, type_)

def reboot(bootload_type):
    return OFFICIAL_AGAIN_BY_VERSION3
    _control_android(False, lambda x,y,z: x.reboot(y[0]), bootload_type)

def remove_package(package):
    return OFFICIAL_AGAIN_BY_VERSION3
    _control_android(False, lambda x,y,z: x.remove_package(y[0]), package)

def shell(*cmd):
    return OFFICIAL_AGAIN_BY_VERSION3
    cmd = " ".join(cmd)
    return _control_android(True, lambda x,y,z: x.shell(y[0]), cmd)

def take_snapshot(path=None):
    return OFFICIAL_AGAIN_BY_VERSION3
    if not path:
        now = time.localtime()
        path = "ash_snapshot_%04d-%02d-%02d-%02d-%02d-%02d" % (
                now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    results = _control_android(True, lambda x,y,z: x.takeSnapshot())
    for i in range(len(results)):
        result = results[i]
        result.writeToFile("%s_%d" % (path, i), "png")

def touch(type_, x, y, percentage=False):
    """Lay down or up or move finger on screen"""
    return OFFICIAL_AGAIN_BY_VERSION3
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

def _ask_ashfa(device, cmd, length=0):
    if length == 0:
        length = "%03d" % len(cmd)
    try:
        device[DEV_CONN_INDX][1].sendall(length)
        device[DEV_CONN_INDX][1].sendall(cmd)
    except:
        #print "Fail to send AGI query! connect again"
        if device[DEV_CONN_INDX][1]:
            device[DEV_CONN_INDX][1].close()
            device[DEV_CONN_INDX][1] = _connect_agi(device[1])

def show_cursor(x, y, percentage=False, pressed=False):
    return OFFICIAL_AGAIN_BY_VERSION3
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
            _ask_ashfa(device, query, length)

def hide_cursor():
    return OFFICIAL_AGAIN_BY_VERSION3
    for device in _devices:
        if device[DEV_FOCUSED_INDX]:
            query = "HIDE"
            length = "%03d" % len(query)
            _ask_ashfa(device, query, length)

def wake():
    return OFFICIAL_AGAIN_BY_VERSION3
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
    return OFFICIAL_AGAIN_BY_VERSION3
    if not target_me:
        return _control_pc(False, "move_mouse %s %s %s True" % (
                x, y, percentage))
    if percentage == "False":
        percentage = False
    if percentage:
        # convert percentage to actual value in pixel
        pass
    else:
        x = _convert_arg(x, int, None)
        y = _convert_arg(y, int, None)

def press_mouse(right_button=False, target_me=False):
    return OFFICIAL_AGAIN_BY_VERSION3
    if not target_me:
        return _control_pc(False, "press_mouse %s True" % (right_button))
    button = InputEvent.BUTTON1_MASK
    if eval(right_button):
        button = InputEvent.BUTTON3_MASK

def release_mouse(right_button=False, target_me=False):
    return OFFICIAL_AGAIN_BY_VERSION3
    if not target_me:
        return _control_pc(False, "release_mouse %s True" % (right_button))
    button = InputEvent.BUTTON1_MASK
    if eval(right_button):
        button = InputEvent.BUTTON3_MASK

def wheel_mouse(notches, target_me=False):
    return OFFICIAL_AGAIN_BY_VERSION3
    if not target_me:
        return _control_pc(False, "wheel_mouse %s True" % notches)

def press_key(keycode, target_me=False):
    return OFFICIAL_AGAIN_BY_VERSION3
    if not target_me:
        return _control_pc(False, "press_key %s True" % keycode)

def release_key(keycode, target_me=False):
    return OFFICIAL_AGAIN_BY_VERSION3
    if not target_me:
        return _control_pc(False, "release_key %s True" % keycode)

def accept_remote_connection():
    ashmon.start_deamon()

def block_remote_connection():
    ashmon.stop_daemon()

# Device connection lookup thread.
class _DeviceLookupThread(threading.Thread):
    def run(self):
        while True:
            if _stop_device_lookup_thread: break
            #TODO: get current physically connected device, connect logically.
