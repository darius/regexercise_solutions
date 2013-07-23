def search(strings, chars):
    """Given a sequence of strings and an iterator of chars, return True
    if any of the strings would be a substring of ''.join(chars); but
    only consume chars up to the end of the match."""
    if not all(strings):
        return True
    tails = []
    for ch in chars:
        tails = [tail[1:] for tail in strings + tails if tail[0] == ch]
        if not all(tails):
            return True
    return False
