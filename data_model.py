# Define models for data unit.

class Event:
    def __init__(self, name, evtType, xys, duration, action, arg=""):
        self.name = name
        self.evtType = evtType
        self.xys = xys  # list of int.
        self.duration = duration    # float
        self.action = action    # one of UP, DOWN, DOWN_UP
        self.arg = arg

    @staticmethod
    def clone(e):
        return Event(e.name, e.evtType, e.xys, e.duration, e.action, e.arg)

    def __str__(self):
        return "name : %s, type : %s, xys : %s, duration : %s, action : %s, arg : %s" % (
                self.name, self.evtType, self.xys, self.duration, self.action, self.arg)

class EventStream:
    def __init__(self, name, items):
        self.name = name
        # items : list of strings that start with 'ev' or 'es' and float.
        self.items = items

    @staticmethod
    def clone(es):
        return EventStream(es.name, es.items)

    def __str__(self):
        return "name : %s, items : %s" % (
                self.name, self.items)

class Binding:
    def __init__(self, name, keyInput, eventstream):
        self.name = name
        self.keyInput = keyInput # string.
        self.events = eventstream

    @staticmethod
    def clone(b):
        return Binding(b.name, b.keyInput, b.events)

    def __str__(self):
        return "name : %s, keyInput : %s, events : %s" % (
                self.name, self.keyInput, self.events)

class BindingSet:
    def __init__(self, name, bindings):
        self.name = name
        self.bindings = bindings

    @staticmethod
    def clone(bs):
        return BindingSet(bs.name, bs.bindings)

    def __str__(self):
        result = "name : %s, bindings : [" % self.name
        for key in self.bindings.keys():
            binding = self.bindings[key]
            result += "%s," % binding
        result += "]"
        return result 
