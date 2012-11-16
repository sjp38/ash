#!/usr/bin/env python
# ash evaluator.

import copy
import sys
import time

import ash
import ashmon
import data
#TODO: Make monkey-dependant part unittest-able
import devmgr
import ashdi

RECORD_FILTER = ("arg", "record", "record_stop")

# Make raw expression(python string) to list(python list with strings)
def _raw_ashval(expr):
    if not expr.startswith('['):
        expr = '[' + expr + ']'
    splitted = expr.split()
    raw_py_expr = ""
    last_elem = " "
    for elem in splitted:
        last_list_start = elem.rfind('[')
        last_list_end = elem.find(']')
        if last_list_end == -1:
            last_list_end = len(elem)
        content = elem[last_list_start+1:last_list_end]
        if content != "":
            elem = "%s'%s'%s" % (elem[0:last_list_start+1],
                content, elem[last_list_end:])
        if not last_elem[-1] in ["[", "]"] or last_elem[-1] != elem[0]:
            elem = ", " + elem
        raw_py_expr += elem
        last_elem = elem
    raw_py_expr = raw_py_expr[2:]
    list = eval(raw_py_expr)
    # TODO remove below print.
    print list
    return list

def arg(number):
    if not isinstance(number, int):
        number = int(number)
    return _argstack[-2][number - 1]

_recording = False
_record_queue = []
_record_name = ""
_last_record_time = 0
_record_filter = []

# record events and make an alias stream.
# param record_filter: command types should not record.
def record(record_name, *record_filter):
    if not isinstance(record_name, str) or len(record_name) <= 0:
        now = time.localtime()
        record_name = "ash_record_%04d-%02d-%02d-%02d-%02d-%02d" % (
                now.tm_year, now.tm_mon, now.tm_mday,
                now.tm_hour, now.tm_min, now.tm_sec)
    global _record_queue
    global _record_name
    global _recording
    global _record_filter
    _record_queue = []
    _record_name = record_name
    _recording = True
    _record_filter = record_filter

def record_stop(record_name=None):
    global _record_queue
    global _record_name
    global _recording

    if isinstance(record_name, str) and len(record_name) > 0:
        _record_name = record_name
    _recording = False
    data.add_callback("", "alias", _record_name, copy.deepcopy(_record_queue))
    _record_queue = []

# just for test
def _mock_function(a, b, c):
    return "_mock_function : %s, %s, %s" % (a, b, c)

def event(mode, type_, value, *arg):
    code = data.get_callback(mode, type_, value)
    _argstack[-1] = _argstack[-1][3:]
    result = None
    for expr in code:
        result = ashval(expr, False)
    return result

def exit():
    sys.exit()

def sleep(time_):
    if not isinstance(time_, float):
        try:
            time_ = float(time_)
        except:
            "Sleep fail! can't convert argument to float"
    time.sleep(time_)

def start_ashdi():
    ashdi.start_ashdi()

# Return ash function(list) or python function object.
def _get_code(expr):
    if not isinstance(expr, list) or not isinstance(expr[0], str):
        return False
# For test, manually switch commenting...
    for module in [ash, ashmon, data, sys.modules[__name__], devmgr]:
#    for module in [ash, ashmon, data, sys.modules[__name__]]:
        if hasattr(module, expr[0]):
            f = getattr(module, expr[0])
            if hasattr(f, '__call__'):
                return f
    return data.get_callback("", "alias", expr[0])

_argstack = []

# evaluate param's elements.
# e.g, execute [[touch DOWN 100 200] [touch UP 100 200]]
def execute(exprs):
    results = []
    for expr in exprs:
        results.append(ashval(expr))
    return results

def ashval(expr, is_raw = True):
    # 1. Make raw expression(python string) to list(python list with strings)
    # 2-1. If function call, evaluate args and execute function, return value.
    # 2-2. If not function call, It's just list. return itself.
    if is_raw and isinstance(expr, str):
        expr = _raw_ashval(expr)
    result = expr

    # if this is executable, do it(eval arguments, call function)
    code = _get_code(expr)
    if not code or code == data.NO_CALLBACK:
        return result
    # push arguments to stack
    args = []
    for arg in expr[1:]:
        args.append(ashval(arg, False))
    _argstack.append(args)
    if isinstance(code, list):
        for expr in code:
            result = ashval(expr, False)
    else:
        result = code(*args)
        if (_recording and not expr[0] in RECORD_FILTER
                and not expr[0] in _record_filter):
            global _last_record_time
            global _record_queue
            interval = time.time() - _last_record_time
            if len(_record_queue) > 0 and interval > 0.3:
                _record_queue.append(["sleep", interval])
            expr = [expr[0]] + copy.deepcopy(args)
            _record_queue.append(expr)
            _last_record_time = time.time()

    del _argstack[-1]

    return result

if __name__ == "__main__":
    pass
