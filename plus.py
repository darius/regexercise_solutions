def search(re, chars):
    """Given a regular expression and an iterator of chars, return True if
    re matches some prefix of ''.join(chars); but only consume chars
    up to the end of the match."""
    states = set([re])
    for ch in chars:
        states = set(flatten(after(ch, state) for state in states))
        if empty in states:
            return True
    return False

def flatten(lists): return sum(lists, [])

def after(ch, re):
    """Imagine all strings starting with ch that re matches; return a list
    of regexes that among them match the remainders of those strings. (For
    example, say ch is 'c', and re matches 'x', 'ca', 'cat', and 'cow', and
    [q,r,s] is the result: that'd mean q|r|s must match 'a', 'at', and 'ow'.)
    This is called the Antimirov derivative."""
    tag, r, s = re
    if   tag == 'empty':   return []
    elif tag == 'literal': return [empty] if r == ch else []
    elif tag == 'chain':   return [chain(r_rest, s) for r_rest in after(ch, r)]
    elif tag == 'either':  return after(ch, r) + after(ch, s)
    elif tag == 'plus':    return flatten([r_rest, chain(r_rest, re)]
                                          for r_rest in after(ch, r))
    else: assert False

# Regular-expression constructors; the re above is built by these.
empty = ('empty', None, None)
def literal(char): return ('literal', char, None)
def chain(r, s):   return s if r is empty else ('chain', r, s)
def either(r, s):  return ('either', r, s)
def plus(r):       return ('plus', r, None)
