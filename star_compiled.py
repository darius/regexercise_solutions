# This seems to me the most direct and obvious change to star.py:
# where star.py computed Antimirov derivatives of the current states
# with respect to the current input character, this code precomputes
# all of the derivatives that can possibly come up, building a table
# of them. Now the only allocating done at match time will be in
# collecting the states into a set; but this set could be represented
# by a fixed-size bit vector (which we don't bother doing here).

# But it's not the shortest and simplest code we could write: that'd
# be Thompson's algorithm. See star_thompsonlike.py.

def search(re, chars):
    """Given a regular expression and an iterator of chars, return True
    if re matches some substring of ''.join(chars); but only consume
    chars up to the end of the match."""
    nfa = prepare(re)
    if nullable(re):
        return True
    states = set()
    for ch in chars:
        states.add(re)
        states = set().union(*[nfa[state].get(ch, ()) for state in states])
        if any(map(nullable, states)):
            return True
    return False

def prepare(re):
    """Return an NFA for matching re, where the states are regular
    expressions. It's a dict mapping each state to a dict mapping
    from each char to its set of successor states."""
    nfa, agenda = {}, set([re])
    while agenda:
        state = agenda.pop()
        if state not in nfa:
            nfa[state] = succs = {}
            for ch, state2 in moves(state):
                succs.setdefault(ch, set()).add(state2)
                agenda.add(state2)
    return nfa

def moves(re):
    "Return a tuple of all of re's transitions as a state in an NFA."
    tag, r, s = re
    if tag == 'empty':     return ()
    elif tag == 'literal': return ((r, empty),)
    elif tag == 'chain':
        dr_s = chaining(r, s)
        return dr_s + moves(s) if nullable(r) else dr_s
    elif tag == 'either':  return moves(r) + moves(s)
    elif tag == 'star':    return chaining(r, re)
    else: assert False

def chaining(r, s):
    "Return the moves for chain(r, s) that eat a character in r."
    return tuple((ch, chain(r_rest, s)) for ch, r_rest in moves(r))

def nullable(re):
    "Does re match the empty string?"
    tag, r, s = re
    if tag == 'empty':     return True
    elif tag == 'literal': return False
    elif tag == 'chain':   return nullable(r) and nullable(s)
    elif tag == 'either':  return nullable(r) or nullable(s)
    elif tag == 'star':    return True
    else: assert False

# Regular-expression constructors; the re above is built by these.
empty = ('empty', None, None)
def literal(char): return ('literal', char, None)
def chain(r, s):   return s if r is empty else ('chain', r, s)
def either(r, s):  return ('either', r, s)
def plus(r):       return chain(r, star(r))
def star(r):       return ('star', r, None)
