# Moduel for data module test.

from data_model import *
from data import *
import data

def testSaveBindingSet():
    print "test saveBindingSet()"
    bindings.clear()
    bindingSets.clear()

    loadBinding("test_xmls/keybinding_sample.xml")
    loadBindingSet("test_xmls/bindingset_sample.xml")

    temp = bindingSets.values()

    saveBindingSet("test_xmls/saveBindingSetTest.xml")
    bindings.clear()
    bindingSets.clear()

    loadBinding("test_xmls/keybinding_sample.xml")
    loadBindingSet("test_xmls/saveBindingSetTest.xml")

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

    loadBinding("test_xmls/keybinding_sample.xml")
    loadBindingSet("test_xmls/bindingset_sample.xml")

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

    if bindingSets[data.currentBindingSet].bindings.has_key(test.keyInput):
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
    if bindingSets[data.currentBindingSet].bindings[test.keyInput] != test:
        print "false on 1st test"
        return False

    print "success!"
    return True


def testSaveBinding():
    print "test saveBinding"
    bindings.clear()
    loadBinding("test_xmls/keybinding_sample.xml")
    saveBinding("test_xmls/saveBindingTest.xml")
    temp = bindings
    bindings.clear()
    loadBinding("test_xmls/saveBindingTest.xml")
    if temp != bindings:
        return False
    return True

def testLoadBinding():
    print "testLoadBinding"
    bindings.clear()
    loadBinding("test_xmls/keybinding_sample.xml")

    test = Binding("simpleKey", "A", "evtouchSample")
    loaded = bindings.get(test.name)
    print test
    print loaded
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
    saveEventStream("test_xmls/saveEventStreamTest.xml")

    temp = eventstreams
    loadEventStream("test_xmls/saveEventStreamTest.xml")

    if temp != eventstreams: return False
    return True



def testLoadEventStream():
    eventstreams.clear()
    loadEventStream("test_xmls/eventstream_sample.xml")
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

    saveEvent("test_xmls/saveEventTest.xml")

    tmp = events
    loadEvent("test_xmls/saveEventTest.xml")
    if tmp != events: return False
    return True


def testLoadEvent():
    print "testLoadEvent"
    loadEvent("test_xmls/event_sample.xml")
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
