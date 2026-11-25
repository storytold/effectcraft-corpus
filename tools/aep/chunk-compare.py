# Chunk-by-chunk comparison of two saved After Effects projects, to show that a cleanup changed only
# what it was meant to change.
#
#   python -I chunk-compare.py <before> <after> [--max N]
#
# It parses both files into their chunks (tools/aep/scrub-uninit.py has the parser), requires the same
# chunk sequence (ids and nesting), and lists every chunk whose bytes differ: its id, its offset, and for
# a same-size chunk how many bytes differ and where. It also compares the bytes after the last chunk
# (the XMP packet). Exit status 0 when the structure matches, 1 otherwise.
import importlib.util
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('scrub_uninit', os.path.join(here, 'scrub-uninit.py'))
su = importlib.util.module_from_spec(spec)
spec.loader.exec_module(su)


def load(path):
    d = open(path, 'rb').read()
    return d, su.chunks(d)


def main(argv):
    limit = 40
    if '--max' in argv:
        i = argv.index('--max')
        limit = int(argv[i + 1])
        del argv[i:i + 2]
    if len(argv) != 2:
        sys.exit('usage: python -I chunk-compare.py <before> <after> [--max N]')
    da, ca = load(argv[0])
    db, cb = load(argv[1])
    ok = len(ca) == len(cb)
    if not ok:
        print('CHUNK COUNT DIFFERS: %d vs %d' % (len(ca), len(cb)))
    counts, lines = {}, []
    for (sa, ea, pa), (sb, eb, pb) in zip(ca, cb):
        if pa != pb:
            print('STRUCTURE DIFFERS at %d / %d: %r vs %r' % (sa, sb, pa[-1], pb[-1]))
            ok = False
            break
        ba, bb = da[sa + 8:ea], db[sb + 8:eb]
        if ba == bb:
            continue
        key = pa[-1].decode('latin1')
        if len(ba) == len(bb):
            diff = [i for i in range(len(ba)) if ba[i] != bb[i]]
            lines.append('%s at %d: %d byte(s) differ, offsets %d..%d' % (key, sa, len(diff), diff[0], diff[-1]))
            counts[key + ' (same size)'] = counts.get(key + ' (same size)', 0) + 1
        else:
            lines.append('%s at %d: size %d -> %d' % (key, sa, len(ba), len(bb)))
            counts[key + ' (resized)'] = counts.get(key + ' (resized)', 0) + 1
    ta = da[ca[-1][1]:] if ca else b''
    tb = db[cb[-1][1]:] if cb else b''
    print('changed chunks:', counts if counts else 'none')
    for line in lines[:limit]:
        print('  ' + line)
    if len(lines) > limit:
        print('  ... %d more' % (len(lines) - limit))
    print('bytes after the last chunk: %d before, %d after, %s' % (len(ta), len(tb), 'identical' if ta == tb else 'DIFFERENT'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
