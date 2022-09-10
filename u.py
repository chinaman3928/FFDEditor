def firstToAppear(search: "container", oneOf: list) -> "first":
    for elem in oneOf:
        if elem in search:
            return elem
    return None


def formatStr(string: str) -> str:
    return string.replace('\n', '').replace('\b', '')


def strRange(s: str, *args, **kargs) -> bool:
    try:
        return int(s) in range(*args, **kargs)
    except ValueError:
        return False


def splits(s: str|list, *preds, lasts = None, exactly = None, delim = None) -> bool:
    """Number of splits must always be >= len(preds),
    and == len(preds) if not lasts,
    and > len(preds) if lasts."""
    if type(s) is str:
        s = s.split() if delim is None else s.split(delim)
    if exactly is not None and len(s) != exactly:
        return False
    if len(s) < len(preds):
        return False
    if len(s) > len(preds) and lasts is None:
        return False
    if len(s) == len(preds) and lasts is not None:
        return False
    if any( not p(spl) for p, spl in zip(preds, s) ):
        return False
    return all( lasts(s[i]) for i in range(len(preds), len(s)) )


def repeatedDictKey(d: dict, key: str) -> str:
    """if ABC is in d, then goes ABC(2) —> ABC(3) —> etc"""
    if key not in d: return key
    n = 2
    key = key + f'({n})'
    while key in d:
        n += 1
        key = key[:-3] + f'({n})'
    return key


def yieldInChunks(iterable, n, filler = None):
    iterable = iter(iterable)
    try:
        while True:
            ret = []
            for _ in range(n):
                ret.append(next(iterable))
            yield ret
    except StopIteration:
        if ret:
            ret += [filler for _ in range(n - len(ret))]
            yield ret


def zipAllTheWay(*iterables, filler = None):
    skip = [False for _ in range(len(iterables))]
    left = len(iterables)
    iterables = [iter(iterable) for iterable in iterables]
    while True:
        ret = []
        for i, iterable in enumerate(iterables):
            if skip[i]:
                ret.append(filler)
            else:
                try:
                    ret.append(next(iterable))
                except StopIteration:
                    ret.append(filler)
                    skip[i] = True
                    left -= 1
        if not left: return
        yield ret


def btos(bytes) -> str:
    return bytes.decode('utf-8').replace('\b', '').replace('\n', '')


def full(byteStr) -> bytes:
    return len(byteStr).to_bytes(2, "little") + byteStr


def sToFull(s: str, lenSize = 2) -> bytes:
    return len(s).to_bytes(lenSize, "little") + s.encode('utf-8')


def bToFull(b: bytes, lenSize = 2) -> bytes:
    return len(b).to_bytes(lenSize, "little") + b


def padLst(lst, what, n) -> list:
    """Mutates passed list."""
    lst += [what for _ in range(n - len(lst))]
    return lst


def downColumns(seq, cols, apply=None, filler=None) -> list:
    d, m = divmod(len(seq), cols)
    heights = [d+1 for _ in range(m)] + [d for _ in range(cols - m - 1)]
    for r in range(d+1 if m else d):
        i = r
        row = [seq[i]]
        for h in heights:
            i += h
            row.append( (seq[i] if apply is None else apply(seq[i])) if i < len(seq) else None)
        yield row


def strIsInt(s) -> bool:
    """Negatives possible."""
    return s and (s.isdecimal() or s[0] == '-' and s[1:].isdecimal())


def prefixRemoved(s: str, prefixes) -> str:
    """Removes exactly one (first occurence) or zero."""
    for prefix in prefixes:
        if s.startswith(prefix):
            return s[len(prefix):]
    return s


def avg(seq):
    return sum(seq) / len(seq)


def get(seq, key):
    """Returns first value that satisfies key, else None."""
    for elem in seq:
        if key(elem):
            return elem


def irange(*args):
    if len(args) == 1: return range(args[0] + 1)
    elif len(args) == 2: return range(args[0], args[1] + 1)
    elif len(args) == 3: return range(args[0], args[1] + 1, args[2])
    raise TypeError(f"irange() got an invalid {len(args)} arguments.")