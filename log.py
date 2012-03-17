
def log(tag, symbol, text, e):
    print "[%s][%s] %s" % (tag, symbol, text), e

# For error
def e(tag, text, e=BaseException()):
    log(tag, "Error", text, e)

# For warning
def w(tag, text, e=BaseException()):
    log(tag, "Warning", text, e)

# For debugging
def d(tag, text, e=BaseException()):
    log(tag, "Debug", text, e)

# For inform
def i(tag, text, e=BaseException()):
    log(tag, "Information", text, e)

# For verbose inform
def v(tag, text, e=BaseException()):
    log(tag, "Verbose", text, e)
