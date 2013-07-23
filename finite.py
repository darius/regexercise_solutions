def search(re, chars):
    """Given a regular expression and an iterator of chars, return True
    if re matches some substring of ''.join(chars); but only consume
    chars up to the end of the match."""
    states = set()
    for ch in chars:
        states.add(re)
        states = set(sum((delta(ch, state) for state in states), []))
        if empty in states:
            return True
    return False

def delta(ch, re):
    tag, r, s = re
    if tag == 'empty':
        return []
    elif tag == 'literal':
        return [empty] if r == ch else []
    elif tag == 'chain':
        return [chain(after, s) for after in delta(ch, r)]
    elif tag == 'either':
        return delta(ch, r) + delta(ch, s)
    else:
        assert False

# Regular expression constructors; the re above is built by these.
empty = ('empty', None, None)
def literal(char): return ('literal', char, None)
def chain(r, s):   return s if r is empty else ('chain', r, s)
def either(r, s):  return ('either', r, s)