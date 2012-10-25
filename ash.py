#!/usr/bin/env monkeyrunner
#!/usr/bin/env python
# Main entry point of Ash. Run with CLI.
# Author : SeongJae Park <sj38.park@gmail.com>
# License : GPL v3

#from java.lang import System

import sys
import ashval

#if System.getProperty("os.name").startswith("Windows"):
#    import os
#    srcFileDir = os.path.dirname(os.path.abspath(__file__))
#    os.chdir(srcFileDir)
#    sys.path = [srcFileDir] + sys.path

import log
import manual

TAG = "Ash"

def printResult(result, depth=0):
    if result.__class__ == list:
        for subResult in result:
            if subResult.__class__ == list:
                printResult(subResult, depth + 1)
            elif subResult: print depth * '\t' + '%s' % subResult
    else:
        print result

def get_expression():
    user_expr = raw_input("ash >>>")
    while user_expr[-1] == '\\':
        user_expr = user_expr[0:-1]
        user_expr += raw_input("   ")
    return user_expr

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        initCmd = "execScript " + sys.argv[1]
        ashval.ashval(initCmd)
    while (1):
        user_input = get_expression()
        if (user_input == ""):
            print manual.CMDS
            continue
        result = ashval.ashval(user_input)
        if result: printResult(result)
