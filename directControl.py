#!/usr/bin/env monkeyrunner
# Module for direct control mode(use device screen as screen)
# Comes from MonkeyPySon.
#
# Author : SeongJae Park <sj38.park@gmail.com>

from java.awt import BorderLayout, Dimension, Robot, Color, Cursor, Toolkit, Point, Font
from java.awt.event import KeyListener, WindowFocusListener, KeyEvent
from java.awt.image import BufferedImage
from java.io import ByteArrayInputStream
from java.lang import System
from javax.imageio import ImageIO
from javax.swing import JButton, JFrame, JLabel, JPanel, JTextArea, JScrollPane, ScrollPaneConstants, BoxLayout, JTextField
from javax.swing.event import MouseInputAdapter
from pawt import swing

import os
import sys
import threading
import time

import cmd
import data
import log


if System.getProperty("os.name").startswith("Windows"):
    import os
    srcFileDir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(srcFileDir)
    sys.path = [srcFileDir] + sys.path


REMAP_WIDTH = 480
REMAP_HEIGHT = 800
MARGIN = 10

robot = Robot()

TAG = "Ash_directControl"
FRAME_TITLE = "Ash - directControl"


frame = None
contentPane = None

def start():
    global frame
    frame = JFrame(FRAME_TITLE)
    frame.setContentPane(getContentPane())
    frame.windowClosing = lambda x: windowClosing()
    frame.pack()
    frame.setVisible(True)
    frame.addWindowFocusListener(GuiWindowFocusListener())
    cmd.CmdExecutor.execute(data.Command("setVirtualScreen", [REMAP_WIDTH, REMAP_HEIGHT]))
    cmd.CmdExecutor.execute(data.Command("startAutoConnection", []))

def stop():
    cmd.CmdExecutor.execute(data.Command("stopAutoConnection", []))
    frame.dispose()

def windowClosing():
    cmd.CmdExecutor.execute(data.Command("stopAutoConnection", []))
    sys.exit()


mainScreen = None
mainScreenImg = None
def getContentPane():
    global contentPane
    global REMAP_WIDTH
    global REMAP_HEIGHT
    global MARGIN
    if not contentPane:
        global mainScreen
        global mainScreenImg
        mainScreen = JLabel()

        cursorImg = BufferedImage(16,16,BufferedImage.TYPE_INT_ARGB)
        blankCursor = Toolkit.getDefaultToolkit().createCustomCursor(cursorImg, Point(0,0), "blank cursor")
        mainScreen.setCursor(blankCursor)
        mainScreen.setPreferredSize(
                Dimension(REMAP_WIDTH + MARGIN, REMAP_HEIGHT + MARGIN))
        mainScreen.setText("main screen!")
        image = BufferedImage(REMAP_WIDTH + MARGIN, REMAP_HEIGHT + MARGIN
                , BufferedImage.TYPE_INT_ARGB)
        g = image.createGraphics()
        g.setColor(Color.BLACK)
        g.fillRect(0, 0, REMAP_WIDTH + MARGIN, REMAP_HEIGHT + MARGIN)
        g.setColor(Color.WHITE)
        g.setFont(Font("Serif", Font.BOLD, 20))
        g.drawString("Cursor will display on your device.", 50, 30)
        mainScreenImg = image
        mainScreen.setIcon(swing.ImageIcon(image))

        mouseListener = ScrMouseListener()
        mainScreen.addMouseListener(mouseListener)
        mainScreen.addMouseMotionListener(mouseListener)
        mainScreen.addMouseWheelListener(mouseListener)

        keyListener = ScrKeyListener()
        mainScreen.addKeyListener(keyListener)

        mainScreen.setFocusable(True)

        scrPanel = JPanel()
        scrPanel.setLayout(BoxLayout(scrPanel, BoxLayout.Y_AXIS))
        scrPanel.add(mainScreen)


        contentPane = JPanel()
        contentPane.setLayout(BorderLayout())
        contentPane.add(scrPanel, BorderLayout.WEST)
        # TODO Add control panel in future.
#        contentPane.add(controlPanel(). BorderLayout.EAST)

    return contentPane

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
        x = calcAxis(event.getX() - (MARGIN / 2), True)
        y = calcAxis(event.getY() - (MARGIN / 2), False)
        cmd.CmdExecutor.execute(data.Command("showCursor", [x, y], ["pressed"]))
        cmd.CmdExecutor.execute(data.Command("touch", ["DOWN", x, y], ["v"]))
        self.time1 = time.time()
        self.xy1 = (x, y)

    def mouseReleased(self, event):
        x = calcAxis(event.getX() - (MARGIN / 2), True)
        y = calcAxis(event.getY() - (MARGIN / 2), False)

        cmd.CmdExecutor.execute(data.Command("showCursor", [x, y, False]))
        if self.dragging:
            self.dragging = False
            time2 = time.time()
            cmd.CmdExecutor.execute(data.Command("drag",
                [self.xy1[0], self.xy1[1], x, y, time2 - self.time1], ["v"]))
            return
        cmd.CmdExecutor.execute(data.Command("touch", ["UP", x, y], ["v"]))

    # Return error message if fail to move focus.
    def moveFocus(self, toLeft, y):
        direction = "left"
        if not toLeft:
            direction = "right"
        result = cmd.CmdExecutor.execute(data.Command("focusTo", [direction]))
        if result:
            return result

        newXAxis = MARGIN / 2
        if toLeft:
            newXAxis += REMAP_WIDTH
        else:
            newFocusIndex = index-1
        cmd.CmdExecutor.execute(data.Command("hideCursor",[]))
        basePoint = mainScreen.getLocationOnScreen()
        robot.mouseMove(int(basePoint.getX() + newXAxis), int(basePoint.getY() + y))
        notifyCurrentDevices()

    def processMouseMove(self, event):
        global mainScreen
        x = event.getX()
        y = event.getY()
        # Move focus to next
        margin = MARGIN / 2
        leftLimit = margin
        rightLimit = REMAP_WIDTH + margin
        result = False

        focusChanged = False
        basePoint = mainScreen.getLocationOnScreen()

        self.lastAxis = (int(basePoint.getX()) + x, int(basePoint.getY()) + y)

        if x < leftLimit:
            focusChanged = not self.moveFocus(True, y)

        elif x > rightLimit:
            focusChanged = not self.moveFocus(False, y)
            if not focusChanged: self.lastAxis = None

        return focusChanged

    def mouseDragged(self, event):
        if self.processMouseMove(event):
            self.dragging = False
            return
        x = calcAxis(event.getX() - (MARGIN / 2), True)
        y = calcAxis(event.getY() - (MARGIN / 2), False)
        cmd.CmdExecutor.execute(data.Command("showCursor", [x, y], ["pressed"]))
        self.dragging = True


    def mouseMoved(self, event):
        if self.processMouseMove(event): return
        x = calcAxis(event.getX() - (MARGIN / 2), True)
        y = calcAxis(event.getY() - (MARGIN / 2), False)

        cmd.CmdExecutor.execute(data.Command("showCursor", [x, y]))

    def mouseExited(self, event):
        if self.lastAxis: robot.mouseMove(self.lastAxis[0], self.lastAxis[1])

    def mouseWheelMoved(self, event):
        notches = event.getWheelRotation()
        direction = ""
        if notches < 0:
            direction = "UP"
        else:
            direction = "DOWN"
        cmd.CmdExecutor.execute(data.Command("press", ["DOWN_AND_UP", direction]))

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

        try :
            command = data.Command("exec",
                    [data.Trigger(data.currentTriggerMode, "keyboard", keyValue)])
            result = cmd.CmdExecutor.execute(command)
            if result:
                notifyResult(result)
        except Exception, e:
            if self.metaKeyState.has_key(keyInput):
                keyInput = keyInput + "_LEFT"
            if isDown: action = "DOWN"
            else: action = "UP"

            print "action:%s, keyInput:%s" % (action, keyInput)
            command = data.Command("press", [action, keyInput])
            cmd.CmdExecutor.execute(command)

    def keyPressed(self, event):
        self.processKey(event, True)

    def keyReleased(self, event):
        self.processKey(event, False)

    def keyTyped(self, event):
        pass


if __name__ == "__main__":
    start()
