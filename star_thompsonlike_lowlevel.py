# Now we refactor star_thompsonlike.py into lower-level code. Instead
# of a set, the states are a list, together with a boolean array
# ('occupied') saying for each state whether it's on the list.  We
# represent the set with this combo of datastructures to make it
# efficient both to enumerate the states in the set and to deduplicate
# them.

# The other change is to precompute the accepts() function to make it
# just an array access at match time.

def search(re, chars):
    return run(re(accept), chars)

def run(start, chars):
    if accepts[start]:
        return True
    states = [start]
    occupied = [False] * len(nodes)
    for ch in chars:
        next_states = []
        for state in states:
            after(ch, state, accept, next_states, occupied)
        states = next_states
        for state in states:
            if accepts[state]:
                return True
            occupied[state] = False
    return False

def after(ch, start, end, next_states, occupied):
    while start != end:
        tag, r, s = nodes[start]
        if tag == 'literal':
            if r == ch and not occupied[s]:
                next_states.append(s)
                occupied[s] = True
            break
        elif tag == 'either':
            after(ch, r, end, next_states, occupied)
            start = s
        elif tag == 'star':
            after(ch, r, start, next_states, occupied)
            start = s
        else: assert False

accept  = 0  # A sentinel node that's never accessed.
nodes   = [None]
accepts = [True]

def add(node, accepting):
    nodes.append(node)
    accepts.append(accepting)
    return len(nodes) - 1

def literal(ch):  return lambda k: add(('literal', ch, k), False)
def chain(r, s):  return lambda k: r(s(k))

def either(r, s):
    def r_or_s(k):
        rk, sk = r(k), s(k)
        return add(('either', rk, sk), accepts[rk] or accepts[sk])
    return r_or_s

def star(r):
    def rstar(k):
        j = add(None, accepts[k])
        nodes[j] = ('star', r(j), k)
        return j
    return rstar
