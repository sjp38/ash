# Module for data control.
# Author : SeongJae Pakr <sj38.park@gmail.com>

from xml.etree.ElementTree import Element, SubElement, ElementTree, fromstring, tostring
from data_model import Event, EventStream, Binding, BindingSet
import log

# Data Manager class doesn't exist because best singleton in Python is module.
TAG = "Ash_data"

EVENT_ROOT_ELEMENT = "events"
EVENT_ELEMENT = "event"
EVENT_NAME = "name"
EVENT_TYPE = "type"
EVENT_XYS = "xy"
EVENT_DURATION = "duration"
EVENT_ACTION = "action"
EVENT_ARG = "arg"

ES_ROOT_ELEMENT = "eventstreams"
ES_ELEMENT = "eventstream"
ES_NAME = "name"
ES_ITEM_ELEMENT = "item"
ES_INTERV = "interval"

BINDING_ROOT_ELEMENT="bindings"
BINDING_ELEMENT = "binding"
BINDING_NAME = "name"
BINDING_KEYINPUT = "keyInput"
BINDING_ACTION = "action"

BS_ROOT_ELEMENT = "bindingSets"
BS_ELEMENT = "bindingSet"
BS_NAME = "name"
BS_BINDING_ELEMENT = "binding"

events = {}
eventstreams = {}
bindings = {}    # {name:binding}
bindingSets = {} # {name:bindingset{keyStream:binding}}
currentBindingSet = ""

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

def loadEvent(filePath):
    f = open(filePath, "r")
    tree = fromstring(f.read())
    f.close()

    elements = tree.findall(EVENT_ELEMENT)
    for child in elements:
        name = child.get(EVENT_NAME, "")
        evtType = child.get(EVENT_TYPE, "")
        xy = child.get(EVENT_XYS, "")
        duration = float(child.get(EVENT_DURATION, 0.0))
        action = child.get(EVENT_ACTION, "")
        arg = child.get(EVENT_ARG, "")
        if xy == '':
            xys = []
        else:
            xys = xy.split("/")
            for i in range(len(xys)):
                xys[i] = int(xys[i])

        event = Event(name, evtType, xys, duration, action, arg)
        events[name] = event

def saveEvent(filePath):
    root = Element(EVENT_ROOT_ELEMENT)
    for event in events.values():
        element = Element(EVENT_ELEMENT)
        element.attrib[EVENT_NAME] = event.name
        element.attrib[EVENT_TYPE] = event.evtType

        xys = ""
        for axis in event.xys:
            xys += "%s/" % axis
        xys = xys[0:-1]
        element.attrib[EVENT_XYS] = xys

        element.attrib[EVENT_DURATION] = "%s" % event.duration
        element.attrib[EVENT_ACTION] = event.action
        element.attrib[EVENT_ARG] = event.arg
        root.append(element)
    indent(root)
    f = open(filePath, "w")
    f.write(tostring(root, "UTF-8"))
    f.close()

def addEvent(event):
    events[event.name] = event

def removeEvent(eventName):
    del events[eventName]

def listEvent(onlyNames):
    if onlyNames:
        return events.keys()
    else:
        return events.values()

def getEvent(eventName):
    return Event.clone(events[eventName])



##################
# EventStream
##################

def loadEventStream(filePath):
    f = open(filePath, "r")
    tree = fromstring(f.read())
    f.close()

    elements = tree.findall(ES_ELEMENT)
    for es in elements:
        name = es.get(ES_NAME, "")

        itemLoaded = []
        for item in es:
            itemInterval = float(item.get(ES_INTERV, 0.0))
            itemName = item.get(ES_NAME, "")
            itemList = [itemInterval, itemName]
            itemLoaded.append(itemList)
        es = EventStream(name, itemLoaded)
        eventstreams[es.name] = es

def saveEventStream(filePath):
    root = Element(ES_ROOT_ELEMENT)
    for es in eventstreams.values():
        element = Element(ES_ELEMENT)
        element.attrib[ES_NAME] = es.name
        for item in es.items:
            itemElement = SubElement(element, ES_ITEM_ELEMENT)
            itemElement.attrib[ES_INTERV] = "%s" % item[0]
            itemElement.attrib[ES_NAME] = item[1]
        root.append(element)
    indent(root)
    f = open(filePath, "w")
    f.write(tostring(root, "UTF-8"))
    f.close()

def addEventStream(eventStream):
    eventstreams[eventStream.name] = eventStream

def removeEventStream(eventStreamName):
    del eventstreams[eventStreamName]

def listEventStream(onlyNames):
    if onlyNames:
        return eventstreams.keys()
    return eventstreams.values()

def getEventStream(eventStreamName):
    return EventStream.clone(eventstreams[eventStreamName])





########################################
# Keybinding
########################################

def loadBinding(filePath):
    f = open(filePath, "r")
    tree = fromstring(f.read())
    f.close()
    elements = tree.findall(BINDING_ELEMENT)
    for elem in elements:
        name = elem.get(BINDING_NAME, "")
        keyInput = elem.get(BINDING_KEYINPUT, "")
        event = elem.get(BINDING_ACTION, "")
        binding = Binding(name, keyInput, event)
        bindings[binding.name] = binding
    if len(bindingSets) <= 0:
        initBindingSet()

def saveBinding(filePath):
    root = Element(BINDING_ROOT_ELEMENT)
    for binding in bindings.values():
        element = Element(BINDING_ELEMENT)
        element.attrib[BINDING_NAME] = binding.name
        element.attrib[BINDING_KEYINPUT] = binding.keyInput
        element.attrib[BINDING_ACTION] = binding.action
        root.append(element)
    indent(root)
    f = open(filePath, "w")
    f.write(tostring(root, "UTF-8"))
    f.close()

def addBinding(binding):
    bindings[binding.name] = binding

    if len(bindingSets) <= 0:
        initBindingSet()
    global currentBindingSet
    bindingSets[currentBindingSet].bindings[binding.keyInput] = binding

def removeBinding(bindingName):
    target = bindings[bindingName]
    del bindings[bindingName]

    for bindingSet in bindingSets.values():
        if bindingSet.bindings.has_key(target.keyInput):
            del bindingSet.bindings[target.keyInput]

def listBinding(onlyNames):
    if onlyNames:
        return bindings.keys()
    return bindings.values()

def getBinding(bindingName):
    return Binding.clone(bindings[bindingName])

def getBindingWithKey(keyInput):
    return bindingSets[currentBindingSet].bindings[keyInput]


########################################
# BindingSet
########################################
INIT_BINDING_SET = "main"

def initBindingSet():
    global currentBindingSet
    currentBindingSet = INIT_BINDING_SET
    bindingSets[currentBindingSet] = BindingSet(currentBindingSet, {})

def loadBindingSet(filePath):
    tree = ElementTree()
    try:
        f = open(filePath, "r")
        tree = fromstring(f.read())
        f.close()
    except IOError, e:
        log.i(TAG, "IOError! Ignore this call.", e)
        return

    elements = tree.findall(BS_ELEMENT)
    for elem in elements:
        name = elem.get(BS_NAME, "")

        itemLoaded = []
        for subelem in elem:
            bindingName = subelem.get(BS_NAME, "")
            itemLoaded.append(bindingName)
        members = {}
        for bindingName in itemLoaded:
            if not bindings.has_key(bindingName):
                log.i(TAG, "No binding with name of %s. Ignore it!" % bindingName)
                continue
            binding = bindings[bindingName]
            members[binding.keyInput] = binding
        bindingSet = BindingSet(name, members)
        bindingSets[bindingSet.name] = bindingSet

def saveBindingSet(filePath):
    root = Element(BS_ROOT_ELEMENT)
    for bs in bindingSets.values():
        element = Element(BS_ELEMENT)
        element.attrib[BS_NAME] = bs.name
        for item in bs.bindings.values():
            itemElement = SubElement(element, BS_BINDING_ELEMENT)
            itemElement.attrib[BS_NAME] = item.name
        root.append(element)
    indent(root)
    try:
        f = open(filePath, "w")
        f.write(tostring(root, "UTF-8"))
        f.close()
    except IOError, e:
        log.i(TAG, "IOError! Ignore this call.", e)

def addBindingSet(bindingSet):
    bindingSets[bindingSet.name] = bindingSet

def removeBindingSet(name):
    del bindingSets[name]

def listBindings(name):
    bindingSet = bindingSets[name]
    return bindingSet.bindings.values()

def listBindingSet(onlyNames):
    if onlyNames:
        return bindingSets.keys()
    return bindingSets.values()

def switchBindingSet(name):
    global currentBindingSet
    if bindingSets.has_key(name):
        currentBindingSet = name
    else:
        return "No such binding set"

