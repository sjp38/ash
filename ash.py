#!/usr/bin/env monkeyrunner
# Main entry point of Ash. Run with CLI.
# Author : SeongJae Pakr <sj38.park@gmail.com>

import sys

import log
from cmd import CmdParser, CmdExecutor
import manual

TAG = "Ash"
EXIT = "exit"

def printResult(result):
    if result.__class__ == list:
        for subResult in result:
            if subResult.__class__ == list:
                printResult(subResult)
            else:
                print subResult
    else:
        print result

def parseAndExecute(userInput):
#    try:
        parsed = CmdParser.parse(userInput)
        result = CmdExecutor.execute(parsed)
        if result:
            printResult(result)
    # Errors came with exception.
#    except Exception, e:
#        log.e(TAG, "Exception.", e) 

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        initCmd = "execScript " + sys.argv[1]
        parseAndExecute(initCmd)
    while (1):
        userInput = raw_input(">>> ")
        if (userInput == ""):
            print manual.CMDS
            continue
        if (userInput == EXIT):
            break

        parseAndExecute(userInput)