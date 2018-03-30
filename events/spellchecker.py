# Adapted from https://www.norvig.com/spell-correct.html
import inflect
p = inflect.engine()

def edits1(word):
    """All edits that are one edit away from `word`."""
    end_letters = 's'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1] + [word]
    inserts = [w + c for w in transposes for c in end_letters]
    purals = [p.plural(w) for w in transposes]
    return set(transposes + inserts + purals)


def edits2(word):
    """All edits that are two edits away from `word`."""
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def typos(word):
    """All close typos related to `word`"""
    return edits1(word)
