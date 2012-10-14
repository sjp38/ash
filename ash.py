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

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        initCmd = "execScript " + sys.argv[1]
        ashval.ashval(initCmd)
    while (1):
        userInput = raw_input("ash>> ")
        if (userInput == ""):
            print manual.CMDS
            continue
        result = ashval.ashval(userInput)
        if result: printResult(result)
