# Removes leftovers of uninitialised memory from a saved After Effects project or preset.
#
#   python -I scrub-uninit.py <in> <out>
#
# After Effects writes some fixed-size records without clearing them first, so text of whatever was in
# the process memory before can end up in the file: path fragments of the machine that saved it, and in
# one case a whole source file of an unrelated tool. The saved bytes in question are never read by a
# consumer. This tool changes exactly four kinds of record and leaves every other byte alone:
#
#   1. The footage options (`opti`) of an OpenEXR footage item (tag `oEXR`, 9750 bytes): only the first
#      47 bytes hold options (version, sizes, channel settings); bytes 47.. are the uninitialised rest.
#      A clean save of the same footage has zeros there, and that is what this writes.
#   2. IDentifier's Channel Info (`aRbp`, 148 bytes, the chosen channel's name NUL-terminated from byte
#      19): in a record that holds a run of two or more UTF-16 characters (a printable ASCII byte
#      followed by 0 at an even offset) outside the name, every such character, runs and strays; and a
#      printable byte directly in front of the name that is half of a cut-off pair. A record without
#      such a run is left alone (a stray pair in it is a pointer or float remnant).
#   3. Lumetri Color's data (`sdat`, tag `lumt`, 104 bytes): bytes 0 to 47 are the fixed fields; the rest is
#      uninitialised. In a record that holds a run of two or more UTF-16 characters there, every such
#      character is zeroed (found: path fragments and pieces of a local tool's source text). Other records are
#      left alone.
#   4. The node of time-based UUIDs (Lumetri Color's `<guid>"...-<node>"`): version 1 UUIDs end in the
#      MAC address of a network adapter of the machine that made them. The 12 hex digits are replaced by
#      zeros; the rest of the id (time, clock sequence) stays, so the ids stay distinct and well-formed.
#
# It prints one line per changed record. Check the result independently: inspect-embedded.py with
# --forbid for the local names, and a chunk-by-chunk comparison with the input (chunk-compare.py,
# docs/aep/2026-11-05-importer-samples.md).
import re
import struct
import sys

EXR_OPTIONS_KEEP = 47
CHANNEL_INFO_LEN = 148
NAME_AT = 19
LUMT_LEN = 104
LUMT_FREE_FROM = 48


def walk(d, start, end, path, out):
    """Appends (offset, end, path) of every non-LIST chunk in d[start:end]."""
    p = start
    while p + 8 <= end:
        cid = d[p:p + 4]
        size = struct.unpack('>I', d[p + 4:p + 8])[0]
        body, stop = p + 8, p + 8 + size
        if stop > end:
            raise ValueError('chunk %r at %d runs past its parent' % (cid, p))
        if cid == b'LIST':
            # most lists hold chunks; some (the text document, `btdk`) hold other data: keep those opaque
            inner = []
            try:
                walk(d, body + 4, stop, path + [d[body:body + 4]], inner)
            except ValueError:
                inner = []
            out.extend(inner)
        else:
            out.append((p, stop, path + [cid]))
        p = stop + (size & 1)


def chunks(d):
    if d[:4] != b'RIFX':
        raise ValueError('not a RIFX container')
    out = []
    walk(d, 12, min(len(d), 8 + struct.unpack('>I', d[4:8])[0]), [], out)
    return out


def channel_info_name_end(body):
    """End (exclusive, with the NUL) of the channel name of a Channel Info record, or None."""
    if len(body) != CHANNEL_INFO_LEN:
        return None
    nul = body.find(b'\0', NAME_AT)
    if nul <= NAME_AT:
        return None
    name = body[NAME_AT:nul]
    if not all(32 <= c < 127 for c in name):
        return None
    return nul + 1


def scrub_text_runs(body, lo, hi, skip=(0, 0)):
    """Zeroes the UTF-16 characters of body[lo:hi] (outside the byte range `skip`) in a record that holds a run of two or more.

    A character is a printable ASCII byte followed by 0 at an even offset. A record without such a run is
    returned unchanged (a stray pair in it is a pointer or float remnant). Returns (bytes, the zeroed offsets).
    """
    b = bytearray(body)
    pairs = [i for i in range(lo - lo % 2, min(hi, len(b)) - 1, 2)
             if i >= lo and not (skip[0] <= i < skip[1]) and not (skip[0] <= i + 1 < skip[1])
             and 0x20 <= b[i] <= 0x7e and b[i + 1] == 0]
    chars = set(pairs)
    dirty = any(i + 2 in chars for i in pairs)
    zeroed = set(pairs) if dirty else set()
    for i in zeroed:
        b[i] = 0
    return bytes(b), zeroed


def scrub_channel_info(body, name_end):
    """IDentifier's Channel Info: text runs anywhere outside the name, and a half character in front of it."""
    new, zeroed = scrub_text_runs(body, 0, len(body), (NAME_AT, name_end))
    b = bytearray(new)
    # a printable byte right in front of the name is the first half of a pair cut off by it
    if (NAME_AT - 3) in zeroed and 0x20 <= b[NAME_AT - 1] <= 0x7e:
        b[NAME_AT - 1] = 0
    return bytes(b)


def scrub_lumetri_data(body):
    """Lumetri Color's `sdat` record (`lumt`, 104 bytes): text runs in the unread bytes 48 and up."""
    return scrub_text_runs(body, LUMT_FREE_FROM, len(body))[0]


def main(src, dst):
    d = bytearray(open(src, 'rb').read())
    changed = 0
    for start, stop, path in chunks(bytes(d)):
        body = bytes(d[start + 8:stop])
        new = None
        kind = None
        if path[-1] == b'opti' and body[:4] == b'oEXR' and len(body) > EXR_OPTIONS_KEEP:
            new = body[:EXR_OPTIONS_KEEP] + bytes(len(body) - EXR_OPTIONS_KEEP)
            kind = 'EXR footage options'
        elif path[-1] == b'sdat' and body[:4] == b'lumt' and len(body) == LUMT_LEN:
            new = scrub_lumetri_data(body)
            kind = 'Lumetri data'
        elif path[-1] == b'aRbp':
            end = channel_info_name_end(body)
            if end is not None:
                new = scrub_channel_info(body, end)
                kind = 'IDentifier Channel Info'
        if new is not None and new != body:
            n = sum(1 for a, b in zip(body, new) if a != b)
            print('%-24s chunk at %-8d %5d byte(s) zeroed' % (kind, start, n))
            d[start + 8:stop] = new
            changed += 1
    uuid_v1 = re.compile(rb'(?<=")([0-9a-f]{8}-[0-9a-f]{4}-1[0-9a-f]{3}-[89ab][0-9a-f]{3}-)([0-9a-f]{12})(?=")')
    out, n = bytes(d), 0
    for m in list(uuid_v1.finditer(out)):
        if m.group(2) != b'0' * 12:
            n += 1
    out = uuid_v1.sub(lambda m: m.group(1) + b'0' * 12, out)
    if n:
        print('%-24s %d id(s) with the node zeroed' % ('time-based UUID', n))
        d = bytearray(out)
        changed += n
    assert len(d) == len(open(src, 'rb').read())
    open(dst, 'wb').write(bytes(d))
    print('records changed:', changed)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('usage: python -I scrub-uninit.py <in> <out>')
    main(sys.argv[1], sys.argv[2])
