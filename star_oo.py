# Another form for the ideas from star_thompsonlike.py

def search(re, s): return run(prepare(re), s)

def run(start_states, s):
    if accepting_state in start_states:
        return True
    states = set()
    for c in s:
        states.update(start_states)
        states = set.union(*[state(c) for state in states])
        if accepting_state in states:
            return True
    return False

def accepting_state(c): return set()
def expecting_state(char, k): return lambda c: k(None) if c == char else set()

def state_node(state): return lambda end: set([state])
def alt_node(k1, k2):  return lambda end: walk(k1, end) | walk(k2, end)
def loop_node(k, make_k):
    def loop(end): return walk(k, end) | walk(looping, loop)
    looping = make_k(loop)
    return loop
def walk(k, end): return set() if k is end else k(end)

def prepare(re):
    return re(state_node(accepting_state))(None)

def empty(k):         return k
def chain(re1, re2):  return lambda k: re1(re2(k))
def literal(char):    return lambda k: state_node(expecting_state(char, k))
def either(re1, re2): return lambda k: alt_node(re1(k), re2(k))
def star(re):         return lambda k: loop_node(k, re)
def plus(re):         return chain(re, star(re))
