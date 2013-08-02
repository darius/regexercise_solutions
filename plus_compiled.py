# This seems to me the most direct and obvious change to plus.py:
# where plus.py computed Antimirov derivatives of the current states
# with respect to the current input character, this code precomputes
# all of the derivatives that can ever come up, building a table of
# them. Now the only allocating done at match time will be in
# collecting the states into a set; but this set could be represented
# by a fixed-size bit vector (which we don't bother doing here).

# But it's not the shortest and simplest code we could write: that'd
# be Thompson's algorithm. See plus_thompsonlike.py.

def search(re, chars):
    """Given a regular expression and an iterator of chars, return True
    if re matches some substring of ''.join(chars); but only consume
    chars up to the end of the match."""
    nfa = prepare(re)
    states = set()
    for ch in chars:
        states.add(re)
        states = set().union(*[nfa[state].get(ch, set()) for state in states])
        if empty in states:
            return True
    return False

def prepare(re):
    "Return an NFA for matching re, where the states are regular expressions."
    result, agenda = {}, set([re])
    while agenda:
        state = agenda.pop()
        if state not in result:
            result[state] = moves(state)
            agenda.update(*result[state].values())
    return result

def moves(re):
    """Return a dict from char to set of regular expressions: re's 
    transitions as a state in an NFA."""
    tag, r, s = re
    if tag == 'empty':     return {}
    elif tag == 'literal': return {r: set([empty])}
    elif tag == 'chain':   return chaining(r, s)
    elif tag == 'either':  return union(moves(r), moves(s))
    elif tag == 'plus':    return union(moves(r), chaining(r, re))
    else: assert False

def chaining(r, s):
    "Return the moves for chain(r, s)."
    return dict((ch, set(chain(r_rest, s) for r_rest in res))
                for ch, res in moves(r).items())

def union(moves1, moves2):
    "Return a moves dict incorporating all moves from both arguments."
    result = dict(moves1)
    for ch, res in moves2.items():
        result[ch] = result.get(ch, set()) | res
    return result

# Regular-expression constructors; the re above is built by these.
empty = ('empty', None, None)
def literal(char): return ('literal', char, None)
def chain(r, s):   return s if r is empty else ('chain', r, s)
def either(r, s):  return ('either', r, s)
def plus(r):       return ('plus', r, None)
