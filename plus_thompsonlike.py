# Let's refactor plus.py into an almost-Thompson algorithm. The idea:
# represent a regex with tree nodes augmented with a 'chain' link that
# can be cyclic. The nodes plus the chains form the Thompson NFA
# graph, and we derive the action code from plus.py's after().

# (Lousy job explaining this; it'll have to do for now.)

def search(re, chars):
    return run(re(accept), chars)

def run(start, chars):
    states = set()
    for ch in chars:
        states.add(start)
        states = set(sum((after(ch, state) for state in states), []))
        if any(map(accepts, states)):
            return True
    return False

def accepts(state):
    while True:
        if state == accept: return True
        tag, r, s = nodes[state]
        if tag != 'either': return False
        state = r

def after(ch, start):
    if start == accept:   return []
    tag, r, s = nodes[start]
    if tag == 'literal':  return [s] if r == ch else []
    elif tag == 'either': return after(ch, r) + after(ch, s)
    else: assert False

# Since the compiled graph has loops in it, we can't represent it as
# a tree of tuples anymore. Instead a node is an index into the nodes
# array, each element of which is a tuple like we had before.
accept = -1  # A sentinel node that's never accessed.
nodes = []

def add(tag, r, s):
    nodes.append((tag, r, s))
    return len(nodes) - 1

def literal(ch):  return lambda k: add('literal', ch, k)
def chain(r, s):  return lambda k: r(s(k))
def either(r, s): return lambda k: add('either', r(k), s(k))
def plus(r):
    def rplus(k):
        choice = add('either', k, None)
        node = r(choice)
        nodes[choice] = ('either', k, node)
        return node
    return rplus
