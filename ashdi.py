#!/usr/bin/env monkeyrunner

"""Module for direct ui(use keyboard/mouse as input, device screen as screen).
Just one example application."""

__author__ = "SeongJae Park"
__email__ = "sj38.park@gmail.com"
__copyright__ = "Copyright (c) 2011-2013, SeongJae Park"
__license__ = "GPLv3"

import os
import sys
import threading
import time

from xml.etree.ElementTree import Element, SubElement, ElementTree, fromstring, tostring

from java.awt import BorderLayout, Dimension, Robot, Color, Cursor, Toolkit, Point, Font
from java.awt.event import KeyListener, WindowFocusListener, KeyEvent
from java.awt.image import BufferedImage
from java.io import ByteArrayInputStream
from java.lang import System
from javax.imageio import ImageIO
from javax.swing import JButton, JFrame, JLabel, JPanel, JTextArea, JScrollPane, ScrollPaneConstants, BoxLayout, JTextField
from javax.swing import JList, ListSelectionModel, JScrollPane, DefaultListModel, JComponent
from javax.swing.event import MouseInputAdapter
from pawt import swing

import ashval
import data
import log


if System.getProperty("os.name").startswith("Windows"):
    import os
    srcFileDir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(srcFileDir)
    sys.path = [srcFileDir] + sys.path

TAG = "ashdi"
FRAME_TITLE = "ash - direct interface"

ROW_ELEMENT = "row"
KEY_ELEMENT = "key"
LABEL_ATTR = "label"
CODE_ATTR = "code"

ALL_DEVICES = "All devices"
CONNECTED_DEVICES = "Connected devices"
CONNECT = "Connect"
FOCUS = "Focus"

_stop_android_waker = False
keyLayout = None

frame = None
contentPane = None
devicesList = None
devicesPanel = None
keyboardPanel = None

def start_ashdi():
    loadKeyLayout("data_2.0/ashdi_keylayout.xml")

    global frame
    frame = JFrame(FRAME_TITLE)
    frame.setContentPane(getContentPane())
    frame.windowClosing = lambda x: windowClosing()
    frame.pack()
    frame.setVisible(True)
    frame.addWindowFocusListener(GuiWindowFocusListener())
    start_android_waker()
    handleConnectedDevBtn(True)

def stop():
    _stop_android_waker()
    frame.dispose()

def start_android_waker():
    thread = _AndroidWaker()
    _stop_android_waker = False
    thread.start()

def stop_android_waker():
    _stop_android_waker = True

def windowClosing():
    stop_android_waker()
    sys.exit()

mainScreen = None
mainScreenImg = None
devicesListLabel = None

connectButton = None
focusButton = None

def getContentPane():
    global contentPane
    global devicesList
    global devicesPanel

    if not contentPane:
        global devicesListLabel
        devicesListLabel = JLabel("Devices")

        global devicesList
        devicesList = JList([])
        devicesList.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)
        listScroller = JScrollPane(devicesList)
        listScroller.setPreferredSize(Dimension(600, 400))

        global connectButton
        global focusButton
        allDevsButton = JButton(ALL_DEVICES, actionPerformed=handleAllDevsBtn)
        connectedDevsButton = JButton(CONNECTED_DEVICES,
                actionPerformed=handleConnectedDevBtn)
        connectButton = JButton(CONNECT, actionPerformed=handleConnectBtn)
        focusButton = JButton(FOCUS, actionPerformed=handleFocusBtn)
        focusButton.setVisible(False)
        goInButton = JButton("Go in device", actionPerformed=handleGoInBtn)

        deviceListButtons = JPanel()
        deviceListButtons.add(allDevsButton)
        deviceListButtons.add(connectedDevsButton)
        deviceListButtons.add(connectButton)
        deviceListButtons.add(focusButton)
        deviceListButtons.add(goInButton)

        devicesPanel = JPanel()
        devicesPanel.setLayout(BoxLayout(devicesPanel, BoxLayout.Y_AXIS))
        devicesPanel.add(devicesListLabel)
        devicesPanel.add(listScroller)
        devicesPanel.add(deviceListButtons)

        contentPane = JPanel()
        contentPane.setLayout(BorderLayout())
        contentPane.add(devicesPanel, BorderLayout.WEST)
        contentPane.add(getControlPanel(), BorderLayout.EAST)
        contentPane.add(getScreenPanel(), BorderLayout.CENTER)
        getScreenPanel().setVisible(False)
    return contentPane

terminalResult = None
terminalInput = None

def getControlPanel():
    global controlPanel
    controlPanel = JPanel()
    controlPanel.setLayout(BoxLayout(controlPanel, BoxLayout.Y_AXIS))
    for row in keyLayout:
        rowPanel = JPanel()
        rowPanel.setLayout(BoxLayout(rowPanel, BoxLayout.X_AXIS))
        controlPanel.add(rowPanel)
        for key in row:
            button = JButton(key[0], actionPerformed=handleKeyButton)
            button.setActionCommand(key[1])
            rowPanel.add(button)

    global terminalResult
    terminalResult = JTextArea()
    scroller = JScrollPane(terminalResult)
    terminalResult.setLineWrap(True)
    scroller.setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS)
    scroller.setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER)
    controlPanel.add(scroller)

    global terminalInput
    termInputPanel = JPanel()
    termInputPanel.setLayout(BoxLayout(termInputPanel, BoxLayout.X_AXIS))
    termInputLabel = JLabel("Command")
    termInputPanel.add(termInputLabel)
    terminalInput = JTextField(actionPerformed=handleTerminalInput)
    minimumSize = terminalInput.getMinimumSize()
    maximumSize = terminalInput.getMaximumSize()
    terminalInput.setMaximumSize(Dimension(maximumSize.width, minimumSize.height))

    termInputPanel.add(terminalInput)
    controlPanel.add(termInputPanel)

    return controlPanel

mainScreen = None
scrPanel = None

def getScreenPanel():
    global mainScreen
    global scrPanel
    if not scrPanel:
        mainScreen = JButton()
        cursorImg = BufferedImage(16,16,BufferedImage.TYPE_INT_ARGB)
        blankCursor = Toolkit.getDefaultToolkit().createCustomCursor(cursorImg, Point(0,0), "blank cursor")
        mainScreen.setCursor(blankCursor)
        mainScreen.setPreferredSize(
                Dimension(700, 700))
        image = BufferedImage(700, 700, BufferedImage.TYPE_INT_ARGB)
        g = image.createGraphics()
        g.setColor(Color.BLACK)
        g.fillRect(0, 0, 700, 700)
        g.setColor(Color.WHITE)
        g.setFont(Font("Serif", Font.BOLD, 20))
        g.drawString("Move your mouse here to controlfocused device.", 50, 30)
        mainScreenImg = image
        mainScreen.setIcon(swing.ImageIcon(image))

        mouseListener = ScrMouseListener()
        mainScreen.addMouseListener(mouseListener)
        mainScreen.addMouseMotionListener(mouseListener)
        mainScreen.addMouseWheelListener(mouseListener)

        mainScreen.setFocusable(True)
        keyListener = ScrKeyListener()
        mainScreen.addKeyListener(keyListener)


        scrPanel = JPanel()
        scrPanel.setLayout(BoxLayout(scrPanel, BoxLayout.Y_AXIS))
        scrPanel.add(mainScreen)
        scrPanel.setFocusable(True)
    return scrPanel

def loadKeyLayout(layoutFile):
    global keyLayout
    f = open(layoutFile, "r")
    tree = fromstring(f.read())
    f.close()

    keyLayout = []
    rows = tree.findall(ROW_ELEMENT)
    for row in rows:
        rowKeys = []
        for key in row:
            label = key.get(LABEL_ATTR)
            code = key.get(CODE_ATTR)
            rowKeys.append([label, code])
        keyLayout.append(rowKeys)

def listDevices(devices):
    listModel = DefaultListModel()
    for device in devices:
        listModel.addElement(" ".join(device.split()))
    devicesList.setModel(listModel)

def handleAllDevsBtn(event):
    connectButton.setVisible(True)
    focusButton.setVisible(False)
    devices = ashval.ashval("devices")
    listDevices(devices)

def handleConnectedDevBtn(event):
    connectButton.setVisible(False)
    focusButton.setVisible(True)
    devices = ashval.ashval("connected_devices")
    listDevices(devices)

def handleConnectBtn(event):
    selectedIndices = devicesList.getSelectedIndices()
    for selected in selectedIndices:
        result = ashval.ashval("connect %d" % selected)
        notifyResult(result)

def handleFocusBtn(event):
    selectedIndices = devicesList.getSelectedIndices()
    args = ""
    for selected in selectedIndices:
        args += "%d " % selected
    result = ashval.ashval("focus %s" % args)
    notifyResult(result)
    handleConnectedDevBtn(True)

def handleGoInBtn(event):
    getScreenPanel().setVisible(True)
    frame.pack()

def handleKeyButton(event):
    if event.getActionCommand() == "WAKE":
        ashval.ashval("wake")
    else:
        cmd = "press DOWN_AND_UP %s" % event.getActionCommand()
        cmd = cmd.encode("utf-8")
        result = ashval.ashval(cmd)
        notifyResult(result)

def handleTerminalInput(event):
    global terminalInput
    userInput = terminalInput.getText()
    userInput = userInput.encode("utf-8")
    terminalInput.setText("")
    if not userInput:
        # TODO: Show manual.
        return
    result = ashval.ashval(userInput)
    if result:
        notifyResult(result)

def notifyResult(results, depth=0):
    if results.__class__ == list:
        for result in results:
            if result.__class__ == list:
                notifyResult(result, depth + 1)
            elif result:
                terminalResult.append("\n" + depth * '\t' + "%s" % result)
    else:
        terminalResult.append("\n" + "%s" % results)


def notifyCurrentDevices():
    global mainScreenImg
    global mainScreen

    g = mainScreenImg.createGraphics()
    g.setFont(Font("Monospaced", Font.BOLD, 13))
    g.drawString("[Detected devices]", 70, 100)


    g.setColor(Color.BLACK)
    g.fillRect(70, 100, REMAP_WIDTH + MARGIN, REMAP_HEIGHT + MARGIN)

    g.setFont(Font("Monospaced", Font.PLAIN, 13))
    g.setColor(Color.GRAY)
    g.setBackground(Color.BLACK)

    devices = cmd.CmdExecutor.execute(data.Command("listDevices", ["ash"]))
    for device in devices:
        text = "%s(%s)" % (device[0], device[1])
        if device.focused:
            g.setColor(Color.WHITE)
            text = "Focused : " + text
        g.drawString(text, 70, 100 + 30*(devices.index(device)+1))
        if device.focused:
            g.setColor(Color.GRAY)
    mainScreen.setIcon(swing.ImageIcon(mainScreenImg))

class GuiWindowFocusListener(WindowFocusListener):
    def windowGainedFocus(self, event):
        if False:
            global mainScreen
            basePoint = mainScreen.getLocationOnScreen()

            robot.mouseMove(int(basePoint.getX() + REMAP_WIDTH / 2),
                    int(basePoint.getY() + REMAP_HEIGHT / 2))

    def windowLostFocus(self, event):
        pass

def calcAxis(value, isXAxis):
    return value

class ScrMouseListener(MouseInputAdapter):
    def __init__(self):
        self.dragging = False
        self.time1 = None
        self.xy1 = None
        self.lastAxis = None

    def mousePressed(self, event):
        x = event.getX() * 100.0 / event.getComponent().getWidth()
        y = event.getY() * 100.0 / event.getComponent().getHeight()
        ashval.ashval("show_cursor %d %d 1 pressed" % (x, y))
        ashval.ashval("touch DOWN %d %d 1" % (x, y))
        self.time1 = time.time()
        self.xy1 = (x, y)

    def mouseReleased(self, event):
        x = event.getX() * 100.0 / event.getComponent().getWidth()
        y = event.getY() * 100.0 / event.getComponent().getHeight()
        ashval.ashval("show_cursor %d %d 1" % (x, y))
        if self.dragging:
            self.dragging = False
            time2 = time.time()
            ashval.ashval("drag %d %d %d %d 1 %f" % (
                self.xy1[0], self.xy1[1], x, y, time2 - self.time1))
            return
        ashval.ashval("touch UP %d %d 1" % (x, y))

    def mouseDragged(self, event):
        x = event.getX() * 100.0 / event.getComponent().getWidth()
        y = event.getY() * 100.0 / event.getComponent().getHeight()

        ashval.ashval("show_cursor %d %d 1 pressed" % (x,y))
        self.dragging = True


    def mouseMoved(self, event):
        x = event.getX() * 100.0 / event.getComponent().getWidth()
        y = event.getY() * 100.0 / event.getComponent().getHeight()

        ashval.ashval("show_cursor %d %d 1" % (int(x), int(y)))
        devicesListLabel.setText("%s / %s" % (int(x), int(y)))

    def mouseWheelMoved(self, event):
        notches = event.getWheelRotation()
        direction = ""
        if notches < 0:
            direction = "DPAD_UP"
        else:
            direction = "DPAD_DOWN"
        ashval.ashval("press DOWN_AND_UP %s" % direction)

FUNCTION_KEY_MAP = {
        "F1":"HOME",
        "F2":"BACK",
        "F3":"MENU",
        "F4":"SEARCH",
        "F5":"POWER",
        "F6":"VOLUME_UP",
        "F7":"VOLUME_DOWN",
        "F8":"CALL",
        "F9":"ENDCALL",
        "BACKSPACE":"DEL",
        "UP":"DPAD_UP",
        "DOWN":"DPAD_DOWN",
        "LEFT":"DPAD_LEFT",
        "RIGHT":"DPAD_RIGHT"
        }
KEYCODE_MAP = {
        KeyEvent.VK_SHIFT:"SHIFT",
        KeyEvent.VK_ALT:"ALT",
        KeyEvent.VK_CONTROL:"CTRL",
        KeyEvent.VK_SPACE:"SPACE",
        KeyEvent.VK_BACK_SPACE:"BACKSPACE",
        KeyEvent.VK_UP:"UP",
        KeyEvent.VK_DOWN:"DOWN",
        KeyEvent.VK_LEFT:"LEFT",
        KeyEvent.VK_RIGHT:"RIGHT",
        }

class ScrKeyListener(KeyListener):
    metaKeyState = {"SHIFT":False, "ALT":False, "CTRL":False}

    def processKey(self, event, isDown):
        keyCode = event.getKeyCode()
        keyInput = event.getKeyText(event.getKeyCode()).upper()

        if KEYCODE_MAP.has_key(keyCode):
            keyInput = KEYCODE_MAP[keyCode]

        if FUNCTION_KEY_MAP.has_key(keyInput):
            keyInput = FUNCTION_KEY_MAP[keyInput]


        keyValue = keyInput
        if isDown:
            if self.metaKeyState.has_key(keyValue):
                self.metaKeyState[keyValue] = True
            elif self.metaKeyState["SHIFT"]:
                keyValue = "Shift-" + keyValue
            elif self.metaKeyState["ALT"]:
                keyValue = "Alt-" + keyValue
            elif self.metaKeyState["CTRL"]:
                keyValue = "Ctrl-" + keyValue
            keyValue = keyValue + "_DOWN"
        else:
            if self.metaKeyState.has_key(keyValue):
                self.metaKeyState[keyValue] = False
            keyValue = keyValue + "_UP"

        keyValue = keyValue.encode('utf8')
        keyInput = keyInput.encode('utf8')
        code = ashval.ashval("get_callback default keyboard %s" % keyValue)
        if code and code != data.NO_CALLBACK:
            ashval.ashval("event default keyboard %s" % keyValue)
        else:
            if self.metaKeyState.has_key(keyInput):
                keyInput = keyInput + "_LEFT"
            if isDown: action = "DOWN"
            else: action = "UP"
            ashval.ashval("press %s %s" % (action, keyInput))

    def keyPressed(self, event):
        self.processKey(event, True)

    def keyReleased(self, event):
        self.processKey(event, False)

    def keyTyped(self, event):
        pass

class _AndroidWaker(threading.Thread):
    def run(self):
        while True:
            if _stop_android_waker:
                break
            ashval.ashval("wake")
            time.sleep(5)

if __name__ == "__main__":
    start()
