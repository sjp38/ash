#!/usr/bin/env monkeyrunner
# Gui management module.
# Author : SeongJae Pakr <sj38.park@gmail.com>

from xml.etree.ElementTree import Element, SubElement, ElementTree, fromstring, tostring

from com.android.monkeyrunner import MonkeyImage

from java.awt import BorderLayout, Dimension
from java.awt.event import KeyListener
from java.awt.image import BufferedImage
from java.io import ByteArrayInputStream
from javax.imageio import ImageIO
from javax.swing import JButton, JFrame, JLabel, JPanel, JTextArea, JScrollPane, ScrollPaneConstants, BoxLayout, JTextField
from javax.swing.event import MouseInputAdapter
from pawt import swing

import threading
import time


import manual
import cmd
import log

TAG = "Ash_gui"

FRAME_TITLE = "Ash_gui"

DEFAULT_SCREEN_SHORTER_SIZE = 320.0
scrZoomRatio = 1.0

axisLabel = None

ROW_ELEMENT = "row"
KEY_ELEMENT = "key"
LABEL_ATTR = "label"
CODE_ATTR = "code"

frame = None
contentPane = None
deviceScreen = None
devScrPanel = None
scrCtrlPanel = None
controlPanel = None

deviceScrMouseListener = None

refreshDeviceScr = False
scrRatio = None

keyLayout = None

terminalResult = None
terminalInput = None

def start(layoutFile):
    global frame
    loadKeyLayout(layoutFile)

    frame = JFrame(FRAME_TITLE)
    frame.setContentPane(getContentPane())
    frame.windowClosing = lambda x: windowClosing()
    frame.pack()
    frame.setVisible(True)

def stop():
    startAutoRefresh(False)
    frame.dispose()
    pass

def startAutoRefresh(start):
    global refreshDeviceScr
    if start:
        refreshDeviceScr = start
        scrPlayer = DeviceScrPlayerThread()
        scrPlayer.run()
    refreshDeviceScr = start

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

def getContentPane():
    global contentPane
    global deviceScreen
    global deviceScrMouseListener
    global scrCtrlPanel
    global devScrPanel
    if not contentPane:
        deviceScreen = JLabel()

        deviceScrMouseListener = DeviceScrMouseListener()
        deviceScrKeyListener = DeviceScrKeyListener()
        deviceScreen.addMouseListener(deviceScrMouseListener)
        deviceScreen.addMouseMotionListener(deviceScrMouseListener)
        deviceScreen.addKeyListener(deviceScrKeyListener)
        deviceScreen.setFocusable(True)
        devScrPanel = JPanel()
        devScrPanel.add(deviceScreen)

        scrPanel = JPanel()
        scrPanel.setLayout(BoxLayout(scrPanel, BoxLayout.Y_AXIS))
        scrCtrlPanel = JPanel()
        scrCtrlPanel.setLayout(BoxLayout(scrCtrlPanel, BoxLayout.X_AXIS))
        zoominBtn = JButton("Zoom in", actionPerformed=handleZoominBtn)
        zoomoutBtn = JButton("Zoom out", actionPerformed=handleZoomoutBtn)

        global axisLabel
        axisLabel = JLabel("0000/0000")
        scrCtrlPanel.add(zoominBtn)
        scrCtrlPanel.add(zoomoutBtn)
        scrCtrlPanel.add(axisLabel)

        scrPanel.add(scrCtrlPanel)
        scrPanel.add(devScrPanel)

        contentPane = JPanel()
        contentPane.setLayout(BorderLayout())
        contentPane.add(scrPanel, BorderLayout.WEST)
        contentPane.add(getControlPanel(), BorderLayout.EAST)
    return contentPane

def windowClosing():
    global refreshDeviceScr
    refreshDeviceScr = False

def handleZoominBtn(event):
    global scrZoomRatio
    scrZoomRatio += 0.1

def handleZoomoutBtn(event):
    global scrZoomRatio
    if scrZoomRatio <= 0.1:
        return
    scrZoomRatio -= 0.1

def handleKeyButton(event):
    global deviceScreen
    if event.getActionCommand() == "WAKE":
        command = cmd.Cmd("execInstEvent", ["wake"], [])
    else:
        command = cmd.Cmd("execInstEvent", ["press"],
                ["arg%s" % event.getActionCommand(), "actDOWN_AND_UP"])
    cmd.CmdExecutor.execute(command)
    deviceScreen.requestFocus()

def handleTerminalInput(event):
    global terminalInput
    userInput = terminalInput.getText()
    terminalInput.setText("")
    if not userInput:
        notifyResult(manual.CMDS)
        return
    try:
        parsed = cmd.CmdParser.parse(userInput)
        result = cmd.CmdExecutor.execute(parsed)
        if result:
            notifyResult(result)
    # Errors came with exception.
    except Exception, e:
        log.e(TAG, "Exception.", e)


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



def notifyResult(results):
    if results.__class__ == list:
        for result in results:
            if result.__class__ == list:
                notifyResult(result)
            elif result:
                terminalResult.append("\n" + "%s" % result)
    else:
        terminalResult.append("\n" + "%s" % results)


class DeviceScrPlayerThread(threading.Thread):
    def __init__(self):
        self.stop = False

    def run(self):
        global deviceScreen
        global frame
        global scrRatio
        global scrCtrlPanel
        global controlPanel
        global devScrPanel
        lastWidth = 0.0

        controlPanelWidth = controlPanel.getSize().width
        devScrPanelWidth = devScrPanel.getSize().width
        scrCtrlPanelHeight = scrCtrlPanel.getSize().height
        while(1):
            if not refreshDeviceScr:
                break
            image = cmd.CmdExecutor.execute(cmd.Cmd("execInstEvent", ["snapshot"]))
            if not image or image.__class__ != MonkeyImage:
                log.e(TAG, "Can't get snapshot. returned : %s" % image)
                break
            inputStream = ByteArrayInputStream(image.convertToBytes())
            image = ImageIO.read(inputStream)
            width = image.getWidth()
            height = image.getHeight()
            shorter = min(width, height)
            scrRatio = DEFAULT_SCREEN_SHORTER_SIZE * scrZoomRatio / shorter

            calWidth = int(width * scrRatio)
            calHeight = int(height * scrRatio)

            resize = BufferedImage(calWidth, calHeight, BufferedImage.TYPE_INT_ARGB)
            g = resize.createGraphics()
            g.drawImage(image, 0, 0, resize.getWidth(), resize.getHeight(), None)
            g.dispose()

            deviceScreen.setIcon(swing.ImageIcon(resize))

            if lastWidth != calWidth:
                minWidth = int(max(calWidth, devScrPanelWidth)
                        + controlPanelWidth + 30)
                minHeight = int(calHeight + scrCtrlPanelHeight + 45)
                frame.setMinimumSize(Dimension(minWidth, minHeight))
                lastWidth = calWidth



class DeviceScrMouseListener(MouseInputAdapter):
    def __init__(self):
        self.dragging = False
        self.time1 = None
        self.xy1 = None
    def recalXY(self, x, y):
        return (int(x / scrRatio), int(y / scrRatio))

    def mousePressed(self, event):
        global deviceScreen
        deviceScreen.requestFocus()
        self.time1 = time.time()
        self.xy1 = self.recalXY(event.getX(), event.getY())
        command = cmd.Cmd("execInstEvent", ["touch"],
                ["x1%s" % self.xy1[0], "y1%s" % self.xy1[1], "actDOWN"])
        cmd.CmdExecutor.execute(command)

    def mouseReleased(self, event):
        if self.dragging:
            self.dragging = False
            xy2 = self.recalXY(event.getX(), event.getY())
            time2 = time.time()
            command = cmd.Cmd("execInstEvent", ["drag"],
                    ["x1%s" % self.xy1[0], "y1%s" % self.xy1[1],
                        "x2%s" % xy2[0], "y2%s" % xy2[1],
                        "dur%s" % (time2 - self.time1)])
            cmd.CmdExecutor.execute(command)
            return
        xy = self.recalXY(event.getX(), event.getY())
        command = cmd.Cmd("execInstEvent", ["touch"],
                ["x1%s" % xy[0], "y1%s" % xy[1], "actDOWN_AND_UP"])
        cmd.CmdExecutor.execute(command)

    def mouseDragged(self, event):
        self.dragging = True

    def mouseMoved(self, event):
        xy = self.recalXY(event.getX(), event.getY())
        global axisLabel
        axisLabel.setText("%04d / %04d" % (xy[0], xy[1]))
        pass

class DeviceScrKeyListener(KeyListener):
    metaKeyState = {"SHIFT":False, "ALT":False, "CTRL":False}
    def keyPressed(self, event):
        keyInput = event.getKeyText(event.getKeyCode()).upper()
        if self.metaKeyState.has_key(keyInput):
            self.metaKeyState[keyInput] = True
        elif self.metaKeyState["SHIFT"]:
            keyInput = "Shift-" + keyInput
        elif self.metaKeyState["ALT"]:
            keyInput = "Alt-" + keyInput
        elif self.metaKeyState["CTRL"]:
            keyInput = "Ctrl-" + keyInput

        try :
            command = cmd.Cmd("execBindingWithKey", [keyInput])
            result = cmd.CmdExecutor.execute(command)
            if result:
                notifyResult(result)
        except Exception, e:
            log.i(TAG, "Failed to bind key.", e)
            key = event.getKeyText(event.getKeyCode()).upper()
            if key == "BACKSPACE":
                key = "DEL"
            elif key in ["UP", "DOWN", "LEFT", "RIGHT"]:
                key = "DPAD_" + key

            command = cmd.Cmd("execInstEvent", ["press"], ["arg" + key, "actDOWN_AND_UP"])
            cmd.CmdExecutor.execute(command)
        log.d(TAG, "released " + keyInput)


    def keyReleased(self, event):
        keyInput = event.getKeyText(event.getKeyCode()).upper()
        if self.metaKeyState.has_key(keyInput):
            self.metaKeyState[keyInput] = False

    def keyTyped(self, event):
        pass
