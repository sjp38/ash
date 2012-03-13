
def log(tag, symbol, text, e):
    print "[%s][%s] %s" % (tag, symbol, text), e

# For error
def e(tag, text, e=BaseException()):
    log(tag, "E", text, e)

# For warning
def w(tag, text, e=BaseException()):
    log(tag, "W", text, e)

# For debugging
def d(tag, text, e=BaseException()):
    log(tag, "D", text, e)

# For inform
def i(tag, text, e=BaseException()):
    log(tag, "I", text, e)

# For verbose inform
def v(tag, text, e=BaseException()):
    log(tag, "V", text, e)
