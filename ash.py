#!/usr/bin/env monkeyrunner
#!/usr/bin/env python

"""Main entry point of Ash. Run with CLI."""

__author__ = "SeongJae Park"
__email__ = "sj38.park@gmail.com"
__copyright__ = "Copyright (c) 2011-2013, SeongJae Park"
__license__ = "GPLv3"

#from java.lang import System

import socket
import sys

#if System.getProperty("os.name").startswith("Windows"):
#    import os
#    srcFileDir = os.path.dirname(os.path.abspath(__file__))
#    os.chdir(srcFileDir)
#    sys.path = [srcFileDir] + sys.path

import ashval
import log

TAG = "Ash"

def print_result(result, depth=0):
    if result.__class__ == list:
        for sub_result in result:
            if sub_result.__class__ == list:
                print_result(sub_result, depth + 1)
            elif sub_result: print depth * '\t' + '%s' % sub_result
    else:
        print result

def _get_expression():
    user_expr = raw_input("ash$ ")
    if user_expr == '' or user_expr.startswith('#'):
        return ''
    while user_expr[-1] == '\\':
        user_expr = user_expr[0:-1]
        user_expr += raw_input("   ")
    return user_expr

# Let's do ashval using only this.
def input(expr):
    return ashval.ashval(expr)

def exec_script(file_path):
    f = open(file_path, "r")
    lines = f.readlines()
    f.close()

    expr = ''
    for line in lines:
        if line[-1] == '\n':
            line = line[0:-1]
        if line == '' or line[0] == '#':
            continue
        expr += line
        if expr[-1] == '\\':
            expr = expr[0:-1]
        elif expr != '':
            result = input(expr)
            if result:
                print_result(result)
            expr = ''

def _get_and_process_user_input():
    user_input = _get_expression()
    if (user_input == ""):
        # TODO: print help message.
        return
    result = ashval.ashval(user_input)

    if result: print_result(result)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        init_cmd = "exec_script " + sys.argv[1]
        ashval.ashval(init_cmd)
    while (1):
        _get_and_process_user_input()
