#!/usr/bin/env python
# ash evaluator.

import sys

import data
import devmgr

# TODO: remove below map. Let's use file for default operator maps, too.
DEFAULT_OPERATOR_MAPS = {
        "listDevices": lambda args: "listDevices %s" % args,
        "testFunction:": lambda args: "c. args : %s" % args,
        "touch": lambda args: "touch. args : %s" % args,
        "c": lambda args: "c. args : %s" % args,
        "c": lambda args: "c. args : %s" % args
        }

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

# just for test
def _mock_function(a, b, c):
    return "_mock_function : %s, %s, %s" % (a, b, c)

def exit():
    sys.exit()

# Return ash function(list) or python function object.
def _get_code(expr):
    if not isinstance(expr[0], str):
        return False
    for module in [data, sys.modules[__name__], devmgr]:
    #for module in [data, sys.modules[__name__]]:
        if hasattr(module, expr[0]):
            f = getattr(module, expr[0])
            if hasattr(f, '__call__'):
                return f
    return data.get_callback("", "alias", expr[0])

_argstack = []

def ashval(expr, is_raw = True):
#    print "ashval! %s %s" % (expr, is_raw)
    # 1. Make raw expression(python string) to list(python list with strings)
    # 2-1. If function call, evaluate args and execute function, return value.
    # 2-2. If not function call, It's just list. return itself.
    if is_raw and isinstance(expr, str):
        expr = _raw_ashval(expr)
    result = expr

    # if this is executable, do it(eval arguments, call function)
    # call function means... eval or calling real bottom layer function.
    # if this is function call, do it(eval arguments, start function)
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
    del _argstack[-1]

    return result

if __name__ == "__main__":
    pass
