#!/usr/bin/env python
# Module for data.
# Author : SeongJae Park <sj38.park@gmail.com>


from xml.etree.ElementTree import Element, SubElement, ElementTree, fromstring, tostring
import copy

import log

TAG = "Ash_data"

# target can be list or command or reference or None
# trigger can be None
class Ref:
    def __init__(self, name, trigger, target):
        self.name = name
        self.trigger = trigger
        self.target = target

    def __str__(self):
        targetstr = "%s" % self.target
        if isinstance(self.target, list):
            targetstr = ""
            for target in self.target:
                targetstr += "\n\t%s" % target
        return "[Reference] name : %s, trigger : %s, target : %s" % (self.name
                , self.trigger, targetstr) 

    def __repr__(self):
        return self.__str__()

    def __cmp__(self, other):
        return cmp(self.name, other.name)

class Command:
    def __init__(self, cmd, args, opts=[]):
        self.cmd = cmd
        self.args = args
        self.opts = opts

    def __str__(self):
        return "[Command] command : %s arguments : %s, options : %s" % (self.cmd, self.args, self.opts)

    def __repr__(self):
        return self.__str__()

class Trigger:
    def __init__(self, mode, trig_type, value):
        self.mode = mode
        self.trig_type = trig_type
        self.value = value
        self.key = self.makeKey()

    def makeKey(self):
        self.mode.replace("_", "__")
        self.trig_type.replace("_", "__")
        self.value.replace("_", "__")
        return self.mode + "_" + self.trig_type + "_" + self.value

    def __str__(self):
        return "[Trigger] mode : " + self.mode + ", type : " + self.trig_type + ", value : " + self.value + ", key : " + self.key

    def __repr__(self):
        return self.__str__()

DEFAULT_TRIGGER_MODE = "default"

REFERENCES = "refs"
REFERENCE = "ref"
REFERENCE_NAME = "name"

TRIGGER = "trigger"
TRIGGER_MODE = "mode"
TRIGGER_TYPE = "type"
TRIGGER_VALUE = "value"

LIST = "list"

COMMAND = "command"
COMMAND_CMD = "cmd"
COMMAND_ARG = "arg"
COMMAND_OPT = "opt"

references = {} # name:reference
triggers = {DEFAULT_TRIGGER_MODE:{}} # mode:{key:reference}
currentTriggerMode = DEFAULT_TRIGGER_MODE

def indent(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def triggerFromXml(element):
    mode = element.get(TRIGGER_MODE, DEFAULT_TRIGGER_MODE)
    type = element.get(TRIGGER_TYPE, "")
    value = element.get(TRIGGER_VALUE, "")
    return Trigger(mode, type, value)

def cmdFromXml(element):
    cmd = element.get(COMMAND_CMD, "")
    argentries = element.findall(COMMAND_ARG)
    args = []
    for arg in argentries:
        if cmd == "touch" and len(args) > 0:
            args.append(int(arg.text))
            continue
        elif cmd == "drag":
            if len(args) < 4:
                args.append(int(arg.text))
            else:
                args.append(float(arg.text))
            continue
        args.append(arg.text)
    optentries = element.findall(COMMAND_OPT)
    opts = []
    for opt in optentries:
        opts.append(opt.text)
    return Command(cmd, args, opts)

def targetFromXml(element):
    if element.tag == COMMAND:
        return cmdFromXml(element)
    elif element.tag == LIST:
        return listFromXml(element)
    elif element.tag == REFERENCE:
        return refFromXml(element)

def listFromXml(element):
    result = []
    for sub in element:
        result.append(targetFromXml(sub))
    return result

def refFromXml(element):
    name = element.get(REFERENCE_NAME)
    trigger = None
    target = None
    for item in element:
        if item.tag == TRIGGER:
            trigger = triggerFromXml(item)
        else:
            target = targetFromXml(item)
    return Ref(name, trigger, target)

def loadFrom(filePath):
    f = open(filePath, "r")
    tree = fromstring(f.read())
    f.close()

    elements = tree.findall(REFERENCE)
    for element in elements:
        ref = refFromXml(element)
        addReference(ref)

def xmlFromTrigger(trigger):
    element = Element(TRIGGER)
    element.attrib[TRIGGER_MODE] = trigger.mode
    element.attrib[TRIGGER_TYPE] = trigger.trig_type
    element.attrib[TRIGGER_VALUE] = trigger.value
    return element

def xmlFromCommand(cmd):
    element = Element(COMMAND)
    element.attrib[COMMAND_CMD] = cmd.cmd
    for arg in cmd.args:
        argelement = Element(COMMAND_ARG)
        argelement.text = str(arg)
        element.append(argelement)
    for opt in cmd.opts:
        argelement = Element(COMMAND_OPT)
        argelement.text = opt
        element.append(argelement)

    return element

def xmlFromList(targetList):
    element = Element(LIST)
    for target in targetList:
        subelement = xmlFromTarget(target)
        element.append(subelement)
    return element

def xmlFromTarget(target):
    if isinstance(target, Command):
        return xmlFromCommand(target)
    elif isinstance(target, Ref):
        return xmlFromRef(target)
    elif isinstance(target, list):
        return xmlFromList(target)

def xmlFromRef(ref):
    element = Element(REFERENCE)
    element.attrib[REFERENCE_NAME] = ref.name
    if ref.trigger:
        trigger = xmlFromTrigger(ref.trigger)
        element.append(trigger)
    if ref.target:
        target = xmlFromTarget(ref.target)
        element.append(target)
    return element

def saveTo(filePath):
    root = Element(REFERENCES)
    values = references.values()
    values.sort()
    for ref in values:
        element = xmlFromRef(ref)
        root.append(element)
    indent(root)
    f = open(filePath, "w")
    f.write(tostring(root, "UTF-8"))
    f.close()

def isTriggerExist(trigger):
    if triggers.has_key(trigger.mode):
        return triggers[trigger.mode].has_key(trigger.key)
    else:
        return False

def addReference(ref):
    ref = copy.deepcopy(ref)
    if references.has_key(ref.name):
        log.d(TAG, "Same name reference already exist." + ref.name)
        return "Same name reference already exist!"
    if ref.trigger and isTriggerExist(ref.trigger):
        log.d(TAG, "Same trigger reference already exist." + ref.trigger.key)
        return "Same trigger reference already exist!"
    references[ref.name] = ref
    if ref.trigger:
        setTrigger(ref, ref.trigger)

def removeReference(refName):
    if not references.has_key(refName):
        log.d(TAG, "There is no reference with name " + refName)
        return "There is no reference with name " + refName
    del references[refName]

def setTrigger(ref, trigger):
    if not references.has_key(ref.name):
        log.d(TAG, "Can't set trigger to unregistered reference! %s" % ref)
        return "Can't set trigger to unregistered reference!"

    ref = references[ref.name]
    trigger = copy.deepcopy(trigger)

    if ref.trigger and isTriggerExist(ref.trigger):
        del triggers[ref.trigger.mode][ref.trigger.key]
    if not triggers.has_key(trigger.mode):
        triggers[trigger.mode] = {}
    triggers[trigger.mode][trigger.key] = ref
    ref.trigger = trigger

def switchTriggerMode(mode):
    global currentTriggerMode
    currentTriggerMode = mode

def listReferences(listAll, trigger_mode):
    result = []
    if trigger_mode:
        if triggers.has_key(trigger_mode):
            if not listAll: result = triggers[trigger_mode].keys()
            else: result = triggers[trigger_mode].values()
        else:
            log.d(TAG, "Required to list unexisting trigger mode")
    else:
        if not listAll: result = references.keys()
        else: result = references.values()
    if listAll: result = copy.deepcopy(result)
    result.sort()
    return result

def listTriggerModes():
    result = triggers.keys()
    result.sort()
    return result

def getRef(name):
    return copy.deepcopy(references[name])

def getTargetByRef(name):
    return getRef(name).target

def getReferenceByTrigger(trigger):
    if not trigger.mode:
        trigger.mode = currentTriggerMode
    if not isTriggerExist(trigger):
        log.d(TAG, "Requested not existing trigger. %s" % trigger)
        return "There is no trigger like that."
    return triggers[trigger.mode][trigger.key]
