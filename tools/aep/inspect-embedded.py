"""Independent inspection of saved .aep / .aepx files for embedded colour profiles and private strings.

    python -I inspect-embedded.py <dir-or-file>... [--forbid TEXT]...

It does not trust any cleanup tool: it looks at the final bytes, in four representations.
  raw      every ICC header ("acsp" at offset 36 of a profile) in the bytes of the file
  base64   every long base64 run, decoded, searched for an ICC header
  hex      every long hex run (the .aepx `bdata="..."` attributes), decoded, searched the same way
  strings  vendor strings of well-known profiles (a stub keeps only the profile name, e.g. "sRGB IEC61966-2.1"), and every --forbid text (case-insensitive)
For each profile found it prints the size and its `desc` text. A file is reported CLEAN when every
profile found is a description-only stub (128-byte header, one tag, no colour data).
"""
import base64
import binascii
import re
import sys

VENDOR = [b"Hewlett", b"Hewlett-Packard", b"Adobe RGB", b"Apple Computer", b"Copyright (c)"]


def be32(d, at):
    return int.from_bytes(d[at:at + 4], "big") if len(d) >= at + 4 else None


def icc_at(d, start):
    """(size, tag count, description) of a profile whose header starts at `start`, or None."""
    if d[start + 36:start + 40] != b"acsp":
        return None
    size = be32(d, start) or 0
    count = be32(d, start + 128) or 0
    desc = ""
    for i in range(min(count, 64)):
        e = start + 132 + 12 * i
        if d[e:e + 4] == b"desc":
            off, ln = be32(d, e + 4), be32(d, e + 8)
            body = d[start + off:start + off + ln]
            if body[:4] == b"desc":
                desc = body[12:12 + (be32(body, 8) or 0)].split(b"\0")[0].decode("latin-1")
            elif body[:4] == b"mluc":
                n, at = be32(body, 20), be32(body, 24)
                desc = body[at:at + n].decode("utf-16-be", "replace")
    return size, count, desc


def find_profiles(d, where):
    out = []
    i = d.find(b"acsp")
    while i != -1:
        if i >= 36:
            p = icc_at(d, i - 36)
            if p:
                out.append((where, i - 36) + p)
        i = d.find(b"acsp", i + 1)
    return out


def inspect(path, forbid):
    d = open(path, "rb").read()
    found = find_profiles(d, "raw")
    for m in re.finditer(rb"[A-Za-z0-9+/]{200,}={0,2}", d):
        try:
            b = base64.b64decode(m.group() + b"=" * (-len(m.group()) % 4))
        except binascii.Error:
            continue
        found += find_profiles(b, "base64@%d" % m.start())
    for m in re.finditer(rb"[0-9a-fA-F]{400,}", d):
        h = m.group()
        try:
            b = binascii.unhexlify(h[: len(h) // 2 * 2])
        except binascii.Error:
            continue
        found += find_profiles(b, "hex@%d" % m.start())
    low = d.lower()
    strings = [v.decode() for v in VENDOR if v.lower() in low]
    # the same strings inside decoded base64 / hex runs
    for m in re.finditer(rb"[A-Za-z0-9+/]{200,}={0,2}", d):
        try:
            b = base64.b64decode(m.group() + b"=" * (-len(m.group()) % 4)).lower()
        except binascii.Error:
            continue
        strings += ["%s (base64)" % v.decode() for v in VENDOR if v.lower() in b]
    bad = [t for t in forbid if t.lower().encode() in low or t.lower().encode("utf-16-le") in low]
    stubs = all(p[2] <= 600 and p[3] == 1 for p in found)
    print("%-28s %s  profiles=%d %s%s%s" % (
        path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1],
        "CLEAN" if stubs and not strings and not bad else "CHECK",
        len(found),
        ["%s %dB tags=%d desc=%r" % (p[0], p[2], p[3], p[4]) for p in found],
        (" vendor-strings=%s" % strings) if strings else "",
        (" forbidden=%s" % bad) if bad else "",
    ))
    return stubs and not strings and not bad


if __name__ == "__main__":
    import os
    args, forbid, files = sys.argv[1:], [], []
    while args:
        a = args.pop(0)
        if a == "--forbid":
            forbid.append(args.pop(0))
        elif os.path.isdir(a):
            files += sorted(os.path.join(a, f) for f in os.listdir(a) if f.endswith((".aep", ".aepx", ".ffx")))
        else:
            files.append(a)
    ok = all([inspect(f, forbid) for f in files])
    sys.exit(0 if ok else 1)
