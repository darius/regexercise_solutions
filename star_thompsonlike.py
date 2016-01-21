# Let's refactor star.py into an almost-Thompson algorithm. The idea:
# represent a regex with tree nodes augmented with a 'chain' link that
# can be cyclic. The nodes plus the chains form the Thompson NFA
# graph, but a node can be labeled with 'star' (as well as Thompson's
# 'literal' and 'either' nodes), and we derive the action code from
# star.py's nullable() and after(). A sub-regex is represented by a
# *pair* of a regex node and the node to follow it: this represents
# the regex *between* the start and the follow. So you can ask
# after(ch, start, follow) as the equivalent of after(ch, re) in
# star.py, etc.

# The point: stepping without allocating new regexes and yet without
# Thompson's infinite looping. Thompson's code is even simpler, but
# less correct for our purposes:
#   * It gets caught in an infinite loop for expressions like /A**/.
#   * It keeps a list of states instead of a set; the list may blow up
#     exponentially.
#   * There's no accepts() function; instead it reports when it runs
#     into the accept node in after(). So matches get reported upon
#     scanning the next character *after* the match.

# I think I've done a lousy job explaining how we got here; it'll have
# to do for now.

def search(re, chars):
    return run(re(accept), chars)

def run(start, chars):
    if accepts(start):
        return True
    states = set([start])
    for ch in chars:
        states = set(sum((after(ch, state, accept) for state in states), []))
        if any(map(accepts, states)):
            return True
    return False

def accepts(start):
    if start == accept:    return True
    tag, r, s = nodes[start]
    if   tag == 'literal': return False
    elif tag == 'either':  return accepts(r) or accepts(s)
    elif tag == 'star':    return accepts(s)
    else: assert False

def after(ch, start, end):
    if start == end:       return []
    tag, r, s = nodes[start]
    if   tag == 'literal': return [s] if r == ch else []
    elif tag == 'either':  return after(ch, r, end) + after(ch, s, end)
    elif tag == 'star':    return after(ch, r, start) + after(ch, s, end)
    else: assert False

# Since the compiled graph has loops in it, we can't represent it as
# a tree of tuples anymore. Instead a node is an index into the nodes
# array, each element of which is a tuple like we had before.
accept = -1  # A sentinel node that's never accessed.
nodes = []

def add(node):
    nodes.append(node)
    return len(nodes) - 1

def literal(ch):  return lambda k: add(('literal', ch, k))
def chain(r, s):  return lambda k: r(s(k))
def either(r, s): return lambda k: add(('either', r(k), s(k)))
def star(r):
    def rstar(k):
        j = add(None)
        nodes[j] = ('star', r(j), k)
        return j
    return rstar
