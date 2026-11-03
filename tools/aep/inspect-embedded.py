"""Independent inspection of saved .aep / .aepx / .ffx files for embedded colour profiles and private strings.

    python -I inspect-embedded.py <dir-or-file>... [--forbid TEXT]... [--expect N]

Directories are searched recursively (.aep, .aepx, .ffx). `--expect N` fails unless exactly N files
were inspected, so a scan that skips a directory cannot pass quietly.

It does not trust any cleanup tool: it looks at the final bytes, in four representations.
  raw      every ICC header ("acsp" at offset 36 of a profile) in the bytes of the file
  base64   every long base64 run, decoded, searched the same way
  hex      every long hex run (the .aepx `bdata="..."` attributes), decoded, searched the same way
  strings  vendor strings of well-known profiles and every --forbid text, searched in the raw bytes
           and in every decoded run, as ASCII, UTF-16 (LE and BE), hex text and base64 text
           (all three base64 alignments, case-insensitive for the text itself)

A file is CLEAN when every profile found is a description-only stub made by `stubicc.rs`: exactly a
128-byte header with only the fixed fields set, one `desc` tag, a `desc` text of printable ASCII and
nothing else (no colour data, no curves, no trailing bytes). A profile with any other structure is
reported CHECK, whatever its size.
"""
import base64
import binascii
import os
import re
import sys

VENDOR = ["Hewlett", "Hewlett-Packard", "Adobe RGB", "Apple Computer"]
# The stub keeps only the profile name, e.g. "sRGB IEC61966-2.1".


def be32(d, at):
    return int.from_bytes(d[at:at + 4], "big") if len(d) >= at + 4 else None


def stub_problem(p):
    """None when `p` is exactly a description-only stub, else a short reason."""
    if len(p) < 148 or be32(p, 0) != len(p):
        return "size field does not match the profile"
    if p[4:8] != b"\0\0\0\0" or be32(p, 8) != 0x02400000:
        return "unexpected CMM or version"
    if p[12:24] != b"mntrRGB XYZ ":
        return "unexpected class, colour space or PCS"
    if any(p[24:36]) or p[36:40] != b"acsp" or any(p[40:128]):
        return "header fields other than the fixed ones are set"
    if be32(p, 128) != 1 or p[132:136] != b"desc" or be32(p, 136) != 144 or be32(p, 140) != len(p) - 144:
        return "not exactly one desc tag covering the rest of the profile"
    body = p[144:]
    if body[:8] != b"desc\0\0\0\0":
        return "tag is not a desc text"
    n = be32(body, 8)
    if n is None or n < 1 or len(body) != 12 + n + 78:
        return "desc text length does not match the profile"
    text, nul, rest = body[12:12 + n - 1], body[12 + n - 1], body[12 + n:]
    if nul != 0 or any(rest) or not text or not all(32 <= c < 127 for c in text):
        return "desc is not printable ASCII followed only by zero bytes"
    return None


def description(p):
    """The `desc` text of a stub that passed [`stub_problem`]."""
    n = be32(p, 152) or 1
    return p[156:156 + n - 1].decode("ascii", "replace")


def icc_candidates(d):
    """(offset, profile bytes) for each "acsp" at offset 36 of something that may be a profile."""
    out = []
    i = d.find(b"acsp")
    while i != -1:
        if i >= 36:
            start = i - 36
            size = be32(d, start) or 0
            end = start + size if 128 <= size <= len(d) - start else len(d)
            out.append((start, d[start:end]))
        i = d.find(b"acsp", i + 1)
    return out


def variants(text):
    """Byte patterns that carry `text`: (case_insensitive, pattern) pairs, see the module doc."""
    raw = text.encode("utf-8")
    ci = [raw, text.encode("utf-16-le"), text.encode("utf-16-be")]
    ci += [binascii.hexlify(b) for b in list(ci)]
    ci += [binascii.hexlify(b.upper()) for b in [raw]]
    cs = []
    for form in {text, text.lower(), text.upper(), text.title()}:
        data = form.encode("utf-8")
        for shift in range(3):
            enc = base64.b64encode(bytes(shift) + data)
            # only the characters made of the text's own bits: not the one shared with the bytes before
            # it, nor the one shared with the bytes after it
            part = enc[(8 * shift + 5) // 6:(8 * (shift + len(data))) // 6]
            if len(part) >= 4:
                cs.append(part)
    return [(True, p.lower()) for p in ci], cs


def find_strings(buf, texts):
    """The `texts` that occur in `buf` in any form."""
    low = buf.lower()
    hits = []
    for t in texts:
        ci, cs = variants(t)
        if any(p in low for _, p in ci) or any(p in buf for p in cs):
            hits.append(t)
    return hits


def runs(d):
    """Decoded base64 and hex runs of `d`: (label, bytes)."""
    out = []
    for m in re.finditer(rb"[A-Za-z0-9+/]{200,}={0,2}", d):
        try:
            out.append(("base64@%d" % m.start(), base64.b64decode(m.group() + b"=" * (-len(m.group()) % 4))))
        except binascii.Error:
            pass
    for m in re.finditer(rb"[0-9a-fA-F]{400,}", d):
        h = m.group()
        try:
            out.append(("hex@%d" % m.start(), binascii.unhexlify(h[: len(h) // 2 * 2])))
        except binascii.Error:
            pass
    return out


def scan(d, where, depth, texts, profiles, strings):
    for off, p in icc_candidates(d):
        profiles.append((where, off, p))
    for t in find_strings(d, texts):
        strings.append("%s (%s)" % (t, where))
    if depth > 0:
        for label, b in runs(d):
            scan(b, label if where == "raw" else where + ">" + label, depth - 1, texts, profiles, strings)


def inspect(path, forbid):
    d = open(path, "rb").read()
    profiles, strings = [], []
    scan(d, "raw", 2, VENDOR + list(forbid), profiles, strings)
    problems = []
    for where, off, p in profiles:
        why = stub_problem(p)
        if why:
            problems.append("%s+%d: %s (%d bytes)" % (where, off, why, len(p)))
    ok = not problems and not strings
    descs = sorted({description(p) for _, _, p in profiles if not stub_problem(p)})
    print("%-32s %s  profiles=%d stubs=%s%s%s" % (
        os.path.basename(path), "CLEAN" if ok else "CHECK", len(profiles), descs,
        (" problems=%s" % problems) if problems else "",
        (" strings=%s" % strings) if strings else "",
    ))
    return ok


def collect(args):
    forbid, files, expect = [], [], None
    args = list(args)
    while args:
        a = args.pop(0)
        if a == "--forbid":
            forbid.append(args.pop(0))
        elif a == "--expect":
            expect = int(args.pop(0))
        elif os.path.isdir(a):
            for root, _, names in os.walk(a):
                files += sorted(os.path.join(root, f) for f in names if f.endswith((".aep", ".aepx", ".ffx")))
        else:
            files.append(a)
    return forbid, sorted(files), expect


def main(argv):
    forbid, files, expect = collect(argv)
    results = [inspect(f, forbid) for f in files]
    print("inspected %d file(s)" % len(files))
    if expect is not None and len(files) != expect:
        print("EXPECTED %d file(s)" % expect)
        return 1
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
