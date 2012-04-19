# Moduel for data module test.

from data import *

trigger_test = Trigger("modeA", "keyboard", "Ctrl-Shift-K")
cmd_for_test = Command("press", ["DOWN", 100, 200]) 
reference_for_test = Ref("referenceTestName", trigger_test, cmd_for_test)

compare1 = Ref("command", Trigger("modeA", "key", "Shift-K_DOWN"), Command("type", ["abcd"]))
compare2 = Ref("listWithSingleCommand", Trigger("modeB", "key", "Shift-K_DOWN"), [Command("touch", ["DOWN", 300, 400])])
compare3 = Ref("listWithCmdAndList", Trigger("modeB", "key", "Ctrl-Shift-L_DOWN"), [Command("shell(ls -al)", []), [Command("drag", [100, 200, 150, 210])]])
compare4 = Ref("refForRef", Trigger(DEFAULT_TRIGGER_MODE, "key", "D_UP"), Ref("command", None, None))
compare5 = Ref("complicated", None, [Ref("listWithCmdAndList", None, None), Command("snapshot", ["abc.png"])])

def testReference():
    print "testReference!!"
    print reference_for_test
    print ""

def testTrigger():
    print "testTrigger!!!"
    trigger = Trigger("modeA", "keyboard", "Ctrl-Shift-K")
    print trigger
    print ""

def testLoad():
    print "\ntestLoad!!!"
    loadFrom("test_xmls/data_sample.xml")

    original = getRef(compare1.name)
    print "compare\n ", compare1, "\nand\n", original, "\n"
    if compare1.__str__() != original.__str__(): return True

    original = getRef(compare2.name)
    print "compare\n ", compare2, "\nand\n", original, "\n"
    if compare2.__str__() != original.__str__(): return True

    original = getRef(compare3.name)
    print "compare\n", compare3, "\nand\n", original, "\n"
    if compare3.__str__() != original.__str__(): return True

    original = getRef(compare4.name)
    print "compare\n  ", compare4, "\nand\n", original, "\n"
    if compare4.__str__() != original.__str__(): return True

    original = getRef(compare5.name)
    print "compare\n ", compare5, "\nand\n", original, "\n"
    if compare5.__str__() != original.__str__(): return True

def testSave():
    print "\ntestSave!!!\n"
    references.clear()
    triggers.clear()
    addReference(compare1)
    addReference(compare2)
    addReference(compare3)
    addReference(compare4)
    addReference(compare5)
    bak = references.values()
    bak.sort()
    bak_triggers = triggers.values()
    bak_triggers.sort()
    saveTo("test_xmls/data_save_test.xml")
    references.clear()
    triggers.clear()

    loadFrom("test_xmls/data_save_test.xml")
    now = references.values()
    now.sort()
    now_triggers = triggers.values()
    now_triggers.sort()

    print "now : ", now, "\n"
    for i in range(len(bak)):
        print "compare\n%s\nand\n%s\n" % (bak[i], now[i])
        if bak[i].__str__() != now[i].__str__():
            return True
    for i in range(len(bak_triggers)):
        print "compare\n%s\nand\n%s\n" % (bak_triggers[i], now_triggers[i])
        if bak_triggers[i].__str__() != now_triggers[i].__str__():
            return True

def testAddReference():
    print "testAddReference!!!"
    references.clear()
    triggers.clear()
    trigger = Trigger("triggerTestMode", "type", "value")
    ref = Ref("test", trigger, Command("shell(ls -al)", []))
    addReference(ref)
    if not addReference(ref):
        print "No warning although add same reference twice!"
        return True
    ref2 = Ref("test2", trigger, Command("touch", ["DOWN", "100", "100"]))
    if not addReference(ref2):
        print "No warning although add same trigger twice!"
        return True

    searched = triggers[trigger.mode][trigger.key].trigger
    if searched.__str__() != trigger.__str__():
        print "trigger not registered!"
        print "compared\n%s\n%s\n" % (searched, trigger)
        return True
    return False

def testRemoveReference():
    print "testRemoveReference!!!"
    references.clear()
    triggers.clear()

    if not removeReference("test"):
        print "No warning although removed not registered reference!"
        return True

    addReference(reference_for_test)
    removeReference(reference_for_test.name)
    if len(references) > 0:
        print "reference not removed!!!"
        return True

def testSetTrigger():
    print "testSetTrigger!!!"
    references.clear()
    triggers.clear()

    if not setTrigger(reference_for_test, trigger_test):
        print "No warning although set trigger to unexist reference!"
        return True
    addReference(reference_for_test)
    trigger2 = Trigger("modeB", "typeTest", "valueTest")
    setTrigger(reference_for_test, trigger2)
    if len(triggers[reference_for_test.trigger.mode]) > 0:
        print "Old trigger not deleted!"
        return True
    nowTrigger = triggers["modeB"][trigger2.key].trigger
    if nowTrigger.__str__() != trigger2.__str__():
        print "Trigger not set correctly!"
        print "compared\n%s\n%s" % (nowTrigger, trigger2)
        return True

    reference_for_test.name = "abcd"
    if triggers[trigger2.mode][trigger2.key].name == reference_for_test.name:
        print "No copy protection for reference!"
        return True

    trigger2.trig_type = "copyTest"
    if triggers[trigger2.mode][trigger2.key].trigger.trig_type == trigger2.trig_type:
        print "No copy protection for trigger!"
        return True

def testGetRef():
    references.clear()
    triggers.clear()

    addReference(reference_for_test)
    get = getRef(reference_for_test.name)
    get.name = "testGetRef"
    get2 = getRef(reference_for_test.name)
    if get.name == get2.name:
        print "No copy protection for reference!"
        return True


def testModule():
    if testTrigger(): return True
    if testReference(): return True
    if testLoad(): return True
    if testSave(): return True
    if testAddReference(): return True
    if testRemoveReference(): return True
    if testSetTrigger(): return True
    if testGetRef(): return True

if __name__ == "__main__":
    if testModule():
        print "Data test FAIL!!!"
    else:
        print "Data test success!!!"
