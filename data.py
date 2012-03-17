# Module for data control.
# Author SeongJae Pakr <sj38.park@gmail.com>

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
BINDING_EVENT = "event"

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
        duration = child.get(EVENT_DURATION, 0.0)
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
        event = elem.get(BINDING_EVENT, "")
        binding = Binding(name, keyInput, event)
        bindings[binding.name] = binding

def saveBinding(filePath):
    root = Element(BINDING_ROOT_ELEMENT)
    for binding in bindings.values():
        element = Element(BINDING_ELEMENT)
        element.attrib[BINDING_NAME] = binding.name
        element.attrib[BINDING_KEYINPUT] = binding.keyInput
        element.attrib[BINDING_EVENT] = binding.events
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
    if bindingSets.has_key(name):
        currentBindingSet = name
    else:
        return "No such binding set"





# test
def testSaveBindingSet():
    print "test saveBindingSet()"
    bindings.clear()
    bindingSets.clear()

    loadBinding("keybinding_sample.xml")
    loadBindingSet("bindingset_sample.xml")

    temp = bindingSets.values()

    saveBindingSet("saveBindingSetTest.xml")
    bindings.clear()
    bindingSets.clear()

    loadBinding("keybinding_sample.xml")
    loadBindingSet("saveBindingSetTest.xml")

    for bindingSet in temp:
        for binding in bindingSet.bindings.values(): 
            if (bindingSets[bindingSet.name].bindings[binding.keyInput].__str__()
                != binding.__str__()):
                return False
    return True

def testLoadBindingSet():
    print "test loadBindingSet()"
    bindings.clear()
    bindingSets.clear()

    loadBinding("keybinding_sample.xml")
    loadBindingSet("bindingset_sample.xml")

    binding1 = Binding("simpleKey", "A", "evtouchSample")
    binding2 = Binding("ControlCombination", "Ctrl-K", "evdragSample")
    binding3 = Binding("AltCombination", "Alt-C", "esmultipleEvents")
    binding4 = Binding("Home", "HOME", "essingleEventStream")

    bindingSet1 = BindingSet("bindingSet1", {binding1.keyInput:binding1
        , binding2.keyInput:binding2, binding4.keyInput:binding4})
    if (not bindingSets.has_key(bindingSet1.name)
         or bindingSets[bindingSet1.name].__str__() != bindingSet1.__str__()):
        print "Fail 1"
        return False
    bindingSet2 = BindingSet("bindingSet2", {binding1.keyInput:binding1
        , binding2.keyInput:binding2, binding3.keyInput:binding3
        , binding4.keyInput:binding4})
    print bindingSets[bindingSet2.name]
    print bindingSet2
    if (not bindingSets.has_key(bindingSet2.name)
            or bindingSets[bindingSet2.name].__str__() != bindingSet2.__str__()):
        print "Fail 2"
        return False
    return True

def testRemoveBinding():
    print "tet remove binding"
    bindings.clear()
    bindingSets.clear()
    test = Binding("test", "Ctrl-K", "evtest")
    addBinding(test)
    removeBinding(test.name)

    if bindingSets[currentBindingSet].has_key(test.keyInput):
        print "fail! "
        return False
    print "Success!"
    return True

def testAddBinding():
    print "test add binding"
    bindings.clear()
    bindingSets.clear()
    test = Binding("test", "Ctrl-K", "evtest")
    addBinding(test)

    if bindings[test.name] != test:
        print "false on 1st test"
        return False
    if bindingSets[currentBindingSet][test.keyInput] != test:
        print "false on 1st test"
        return False

    print "success!"
    return True


def testSaveBinding():
    print "test saveBinding"
    bindings.clear()
    loadBinding("keybinding_sample.xml")
    saveBinding("saveBindingTest.xml")
    temp = bindings
    bindings.clear()
    loadBinding("saveBindingTest.xml")
    if temp != bindings:
        return False
    return True

def testLoadBinding():
    print "testLoadBinding"
    bindings.clear()
    loadBinding("keybinding_sample.xml")

    test = Binding("simpleKey", "A", "evtouchSample")
    loaded = bindings.get(test.name)
    if test.__str__() != loaded.__str__():
        print "1 fail."
        return False

    test = Binding("ControlCombination", "Ctrl-K", "evdragSample")
    loaded = bindings.get(test.name)
    if test.__str__() != loaded.__str__():
        print "2 fail."
        return False

    test = Binding("AltCombination", "Alt-C", "esmultipleEvents")
    loaded = bindings.get(test.name)
    if test.__str__() != loaded.__str__():
        print "3 fail."
        return False

    test = Binding("Home", "HOME", "essingleEventStream")
    loaded = bindings.get(test.name)
    if test.__str__() != loaded.__str__():
        print "4 fail."
        return False
    return True


def testSaveEventStream():
    eventstreams.clear()

    test = EventStream("singleEvent", [[0.0, "evtouchSample"]])
    eventstreams[test.name] = test
 
    test = EventStream("multipleEvents", [[0.0, "evkeyPressSample"], [0.5,
        "evtouchSample"], [0.5, "evdragSample"]])
    eventstreams[test.name] = test

    test = EventStream("singleEventStream", [[0.0, "essingleEvent"]])
    eventstreams[test.name] = test


    test = EventStream("multipleEventStreams", [[0.0,"essingleEvent"], [0.5,
        "esmultipleEvents"], [0.5, "essingleEventStream"]])
    eventstreams[test.name] = test

    test = EventStream("mixedEventStreams", [[0.0,"evkeyPressSample"], [0.5,
        "esmultipleEvents"]])
    eventstreams[test.name] = test
    saveEventStream("saveEventStreamTest.xml")

    temp = eventstreams
    loadEventStream("saveEventStreamTest.xml")

    if temp != eventstreams: return False
    return True



def testLoadEventStream():
    eventstreams.clear()
    loadEventStream("eventstream_sample.xml")
    test = EventStream("singleEvent", [[0.0, "evtouchSample"]])
    if eventstreams.get(test.name).__str__() != test.__str__():
        print "1 ", test, eventstreams.get(test.name)
        return False
 
    test = EventStream("multipleEvents", [[0.0, "evkeyPressSample"], [0.5,
        "evtouchSample"], [0.5, "evdragSample"]])
    loaded = eventstreams.get(test.name)
    if loaded.__str__() != test.__str__():
        print "2 ", test, loaded
        return False 

    test = EventStream("singleEventStream", [[0.0, "essingleEvent"]])
    if eventstreams.get(test.name).__str__() != test.__str__():
        print "3 ", test, eventstreams.get(test.name)
        return False


    test = EventStream("multipleEventStreams", [[0.0,"essingleEvent"], [0.5,
        "esmultipleEvents"], [0.5, "essingleEventStream"]])
    if eventstreams.get(test.name).__str__() != test.__str__():
        print "4 ", test, eventstreams.get(test.name)
        return False


    test = EventStream("mixedEventStreams", [[0.0,"evkeyPressSample"], [0.5,
        "esmultipleEvents"]])
    if eventstreams.get(test.name).__str__() != test.__str__():
        print "5 ", test, eventstreams.get(test.name)
        return False
    return True


def testSaveEvent():
    print "testSaveEvent"
    if not testLoadEvent():
        print "Fail to testLoadEvent(). Test can't be done."
        return False

    events.clear()
    test = Event("touchSample", "touch", [30,50], 0.0, "DOWN_AND_UP")
    events[test.name] = test
    test = Event("keyPressSample", "press", [], 0.0, "DOWN", "A")
    events[test.name] = test
    test = Event("dragSample", "drag", [30,50,200,50], 0.3, "")
    events[test.name] = test
    test = Event("typeSample", "type", [], 0.0, "", "abcd")
    events[test.name] = test
    test = Event("wakeSample", "wake", [], 0.0, "")
    events[test.name] = test
    test = Event("rebootSample", "reboot", [], 0.0, "")
    events[test.name] = test
    test = Event("getPropertySample", "getProp", [],0.0,"", "display.width")
    events[test.name] = test
    test = Event("shellSample", "shell", [], 0.0, "", "ls")
    events[test.name] = test
    test = Event("snapshotSample", "snapshot", [], 0.0, "", "~/snapshot.png")

    saveEvent("saveEventTest.xml")

    tmp = events
    loadEvent("saveEventTest.xml")
    if tmp != events: return False
    return True


def testLoadEvent():
    print "testLoadEvent"
    loadEvent("event_sample.xml")
    test = Event("touchSample", "touch", [30,50], 0.0, "DOWN_AND_UP")
    loaded = events.get("touchSample")
    if test.__str__() != loaded.__str__():
        print loaded, test
        print "1"
        return False

    test = Event("keyPressSample", "press", [], 0.0, "DOWN", "A")
    loaded = events.get("keyPressSample")
    if test.__str__() != loaded.__str__():
        print loaded, test
        print "2"
        return False

    test = Event("dragSample", "drag", [30,50,200,50], 0.3, "")
    loaded = events.get("dragSample")
    if test.__str__() != loaded.__str__():
        print loaded, test
        print "3"
        return False

    test = Event("typeSample", "type", [], 0.0, "", "abcd")
    loaded = events.get("typeSample")
    if test.__str__() != loaded.__str__():
        print loaded, test
        print "4"
        return False

    test = Event("wakeSample", "wake", [], 0.0, "")
    loaded = events.get("wakeSample")
    if test.__str__() != loaded.__str__():
        print loaded, test
        print "5"
        return False

    test = Event("shellSample", "shell", [], 0.0, "", "ls")
    loaded = events.get("shellSample")
    if test.__str__() != loaded.__str__():
        print loaded, test
        print "6"
        return False

    return True
 

def testAddEvent():
    print "testAddEvent"
    test = Event("test", "touch", [30, 50], 0, "DOWN_AND_UP")
    addEvent(test)
    added = events.get("test")
    if test.__str__() != added.__str__():
        print "Fail!"
        print ""
        return False
    else:
        print "Success!"
        print ""
        return True

def testEvent():
    print "test event"
    print Event("test", "touch", [30, 50], 0, "DOWN_AND_UP")
    print ""
    return True

def testEventStream():
    print "test event stream"
    print EventStream("eventstream", [0.0,"event1", 0.3, "event2", 0.8, "event3"])
    print ""
    return True

def testBinding():
    print "test binding"
    print Binding("binding", "Ctrl-K", "test")
    print ""
    return True

def testBindingSet():
    print "test bindingset"
    print BindingSet("bindingsetTest",
            {"Ctrl-N":Binding("test","Ctrl-N","evtest")})
    print ""
    return True


if __name__ == "__main__":
    success = True
    success = success and testEvent()
    success = success and testEventStream()
    success = success and testBinding()
    success = success and testBindingSet()
    success = success and testAddEvent()
    success = success and testLoadEvent()
    print ""
    success = success and testSaveEvent()
    print ""
    success = success and testLoadEventStream()
    print ""
    success = success and testSaveEventStream()
    print ""
    success = success and testLoadBinding()
    print ""
    success = success and testSaveBinding()
    print ""
    success = success and testAddBinding()
    print ""
    success = success and testRemoveBinding()
    print ""
    success = success and testLoadBindingSet()
    print ""
    success = success and testSaveBindingSet()
    print ""


#    success = success and testAddEvent()

    print "Result : ", success
