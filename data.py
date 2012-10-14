#!/usr/bin/env python
# Module for data.
# Author : SeongJae Park <sj38.park@gmail.com>
# Licensed under the terms of the GNU GPL License version 3


from xml.etree.ElementTree import Element, fromstring, tostring
import copy

import log

TAG = "Ash_data"

_CALLBACKS = "callbacks"
_CALLBACK = "callback"
_LIST = "list"
_ELEMENT = "el"

# If queried event not exist in current mode, see this mode.
DEFAULT_EVENT_MODE = "__default__"

NO_CALLBACK = "No such condition callback"

#CallBack has calling condition and code.
#Calling condition is event. Event has mode, type, value.
#Alias is just a event that type is alias.
#{mode:{type:{value:code(list of ash exprs)}}}
_callbacks = {}

_current_event_mode = DEFAULT_EVENT_MODE


def _xml_from_list(list_):
    root = Element(_LIST)
    for elem in list_:
        if isinstance(elem, list):
            root.append(_xml_from_list(elem))
        else:
            xml_elem = Element(_ELEMENT)
            xml_elem.text = elem
            root.append(xml_elem)
    return root

def _indent(elem, level=0):
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def save_to_file(file_path):
    root = Element(_CALLBACKS)
    modes = _callbacks.items()
    modes.sort()
    for mode in modes:
        types = mode[1].items()
        types.sort()
        for type_ in types:
            values = type_[1].items()
            values.sort()
            for value_ in values:
                callback = Element(_CALLBACK)
                callback.append(_xml_from_list([mode[0], type_[0], value_[0]]))
                callback.append(_xml_from_list(value_[1]))
                root.append(callback)
    _indent(root)
    f = open(file_path, "w")
    f.write(tostring(root, "UTF-8"))
    f.close()

def load_from_file(file_path):
    f = open(file_path, "r")
    tree = fromstring(f.read())
    f.close()

    elements = tree.findall(_CALLBACK)
    for element in elements:
        callback = _callback_from_xml(element)
        add_callback(callback[0][0], callback[0][1], callback[0][2],
                callback[1])

# Overwrite if calling condition conflict.
def add_callback(mode, type_, value, codes):
    if mode == "" or mode == "default":
        mode = DEFAULT_EVENT_MODE
    if not _callbacks.has_key(mode):
        _callbacks[mode] = {}
    if not _callbacks[mode].has_key(type_):
        _callbacks[mode][type_] = {}
    _callbacks[mode][type_][value] = codes
    if not codes:
        del _callbacks[mode][type_][value]

def get_callback(mode, type_, value):
    if mode == "" or mode == "default":
        mode = _current_event_mode
    try:
        return _callbacks[mode][type_][value]
    except KeyError:
        try:
            return _callbacks[DEFAULT_EVENT_MODE][type_][value]
        except KeyError:
            return NO_CALLBACK

def clear():
    _callbacks.clear()
    _current_event_mode = DEFAULT_EVENT_MODE

# Depth is for...
# mode : 0, type : 1, value : 2, code : 3
def show(depth=0):
    result = []
    modes = _callbacks.items()
    modes.sort()
    subresult_mode = []
    result.append(subresult_mode)
    for mode in modes:
        subresult_mode.append(mode[0])
        if depth <= 0:
            continue
        types = mode[1].items()
        types.sort()
        subresult_type = []
        subresult_mode.append(subresult_type)
        for type_ in types:
            subresult_type.append(type_[0])
            if depth <= 1:
                continue
            values = type_[1].items()
            values.sort()
            subresult_value = []
            subresult_type.append(subresult_value)
            for value_ in values:
                subresult_value.append(value_[0])
                if depth <= 2:
                    continue
                subresult_value.append(copy.deepcopy(value_[1]))
    return result

# Set event mode
def set_mode(mode):
    global _current_event_mode
    if mode:
        _current_event_mode = mode

def get_mode():
    return _current_event_mode

def _list_from_xml(root):
    result = []
    for element in root:
        if element.tag == _ELEMENT:
            result.append(element.text)
        elif element.tag == _LIST:
            result.append(_list_from_xml(element))
    return result

# callback consists of 2 list.
def _callback_from_xml(root):
    callback = []
    elements = root.findall(_LIST)
    for element in elements:
        callback.append(_list_from_xml(element))
    return callback

