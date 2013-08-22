# Based on star.py.

def search(re, chars):
    """Given a regular expression and an iterator of chars, return True if
    re matches some prefix of ''.join(chars); but only consume chars
    up to the end of the match."""
    if nullable(re):
        return True
    states = set([re])
    for ch in chars:
        states = set(sum((after(ch, state) for state in states), []))
        if any(map(nullable, states)):
            return True
    return False

def nullable(re):
    "Does re match the empty string?"
    tag, r, s = re
    if tag == 'empty':     return True
    elif tag == 'literal': return False
    elif tag == 'chain':   return nullable(r) and nullable(s)
    elif tag == 'both':    return nullable(r) and nullable(s)
    elif tag == 'either':  return nullable(r) or nullable(s)
    elif tag == 'star':    return True
    elif tag == 'not':     return not nullable(r)
    else: assert False

def after(ch, re):
    """Imagine all strings starting with ch that re matches; return a list
    of regexes that among them match the remainders of those strings. (For
    example, if ch is 'c', and re matches 'x', 'ca', 'cat', and 'cow', and
    [q,r,s] is the result: that means q|r|s must match 'a', 'at', and 'ow'.)
    This is called the Antimirov derivative."""
    tag, r, s = re
    if tag == 'empty':     return []
    elif tag == 'literal': return [empty] if r == ch else []
    elif tag == 'chain':
        dr_s = [chain(r_rest, s) for r_rest in after(ch, r)]
        return dr_s + after(ch, s) if nullable(r) else dr_s
    elif tag == 'either':  return after(ch, r) + after(ch, s)
    elif tag == 'both':    return merge(after(ch, r), after(ch, s))
    elif tag == 'star':    return [chain(r_rest, re) for r_rest in after(ch, r)]
    elif tag == 'not':
        # dr = r1 | ... | rn
        # ~dr = ~(r1 | ... | rn)
        #     = [not_(reduce(either, after(ch, r), fail))]
        # except we don't have a 'fail', so:
        #     = [not_(reduce(either, dr))] if dr else [star(anyone)]
        return [not_(reduce(either, after(ch, r), fail))]
    else: assert False

def merge(rs, ss): return [both(r, s) for r in rs for s in ss]

# Regular-expression constructors; the re above is built by these.
empty = ('empty', None, None)
def literal(char): return ('literal', char, None)
def chain(r, s):   return s if r is empty else ('chain', r, s)
def either(r, s):  return ('either', r, s)
def plus(r):       return chain(r, star(r))
def star(r):       return ('star', r, None)
def not_(r):       return ('not', r, None)
def both(r, s):    return r if r == s else ('both', r, s)
# TODO: other simplifications on both(r, s)?

anyone = literal('?') # XXX

def chains(*rs): return reduce(chain, rs)

comment = chains(literal('/'),
                 literal('*'),
                 not_(chains(star(anyone), literal('*'), literal('/'), star(anyone))),
                 literal('*'),
                 literal('/'))