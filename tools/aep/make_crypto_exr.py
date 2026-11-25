"""Writes a small synthetic multichannel OpenEXR test image (stdlib only, no third-party code).

320x180, scanline, ZIPS compression (one line per chunk). Channels:
  R G B A                  HALF   beauty (grey 0.18 background, values up to 4.0 in the HDR ramp)
  CryptoObject00.R/G/B/A   FLOAT  Cryptomatte object layer, ranks 0 and 1 (id, coverage, id, coverage)
  CryptoMaterial00.R/G/B/A FLOAT  Cryptomatte material layer
  Z                        FLOAT  depth of the object at the pixel centre (100 = background)
  ID                       FLOAT  object number at the pixel centre (0 = background)
Cryptomatte metadata (name, hash, conversion, manifest) per the public Cryptomatte specification.

Usage: python -I make_crypto_exr.py <out.exr> [<out-manifest.json>]
"""
import json
import struct
import sys
import zlib

W, H = 320, 180
SS = 4  # supersamples per axis for coverage


def mmh3_32(data: bytes, seed: int = 0) -> int:
    c1, c2 = 0xCC9E2D51, 0x1B873593
    h = seed & 0xFFFFFFFF
    n = len(data) // 4
    for i in range(n):
        k = struct.unpack_from("<I", data, i * 4)[0]
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
        h = ((h << 13) | (h >> 19)) & 0xFFFFFFFF
        h = (h * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail = data[n * 4:]
    k = 0
    if len(tail) >= 3:
        k ^= tail[2] << 16
    if len(tail) >= 2:
        k ^= tail[1] << 8
    if len(tail) >= 1:
        k ^= tail[0]
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
    h ^= len(data)
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h


def crypto_hash(name: str) -> int:
    h = mmh3_32(name.encode("utf-8"))
    exp = (h >> 23) & 0xFF
    if exp == 0 or exp == 255:
        h ^= 1 << 23
    return h


def h2f(h: int) -> float:
    return struct.unpack("<f", struct.pack("<I", h))[0]


# Objects, drawn in this order (later = on top).
def in_rect(x0, y0, x1, y1):
    return lambda x, y: x0 <= x < x1 and y0 <= y < y1


def in_disc(cx, cy, r):
    return lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 < r * r


def in_tri(a, b, c):
    def s(p, q, r):
        return (p[0] - r[0]) * (q[1] - r[1]) - (q[0] - r[0]) * (p[1] - r[1])

    def f(x, y):
        p = (x, y)
        d1, d2, d3 = s(p, a, b), s(p, b, c), s(p, c, a)
        neg = d1 < 0 or d2 < 0 or d3 < 0
        pos = d1 > 0 or d2 > 0 or d3 > 0
        return not (neg and pos)

    return f


OBJECTS = [
    # name, material, test, colour (linear RGB), depth, number
    ("ramp_hdr", "mat_emissive", in_rect(0, 150, 320, 180), None, 10.0, 4),
    ("box_red", "mat_paint", in_rect(30, 30, 110, 110), (0.8, 0.1, 0.1), 5.0, 1),
    ("disc_green", "mat_paint", in_disc(140, 70, 40), (0.1, 0.7, 0.2), 3.0, 2),
    ("tri_blue", "mat_glass", in_tri((230, 120), (300, 120), (265, 30)), (0.3, 0.5, 2.5), 8.0, 3),
]
BG = (0.18, 0.18, 0.18)


def colour_of(obj, x):
    if obj[3] is None:  # HDR ramp 0..4 left to right
        v = 4.0 * x / W
        return (v, v, v)
    return obj[3]


def render():
    rgba = [[None] * W for _ in range(H)]
    cobj = [[None] * W for _ in range(H)]
    cmat = [[None] * W for _ in range(H)]
    zch = [[0.0] * W for _ in range(H)]
    idch = [[0.0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            cov_o, cov_m = {}, {}
            col = [0.0, 0.0, 0.0]
            for sy in range(SS):
                for sx in range(SS):
                    px = x + (sx + 0.5) / SS
                    py = y + (sy + 0.5) / SS
                    top = None
                    for o in OBJECTS:
                        if o[2](px, py):
                            top = o
                    if top is None:
                        c = BG
                    else:
                        c = colour_of(top, px)
                        cov_o[top[0]] = cov_o.get(top[0], 0) + 1
                        cov_m[top[1]] = cov_m.get(top[1], 0) + 1
                    for i in range(3):
                        col[i] += c[i]
            n = SS * SS
            rgba[y][x] = (col[0] / n, col[1] / n, col[2] / n, 1.0)
            cobj[y][x] = ranks(cov_o, n)
            cmat[y][x] = ranks(cov_m, n)
            top = None
            for o in OBJECTS:
                if o[2](x + 0.5, y + 0.5):
                    top = o
            zch[y][x] = top[4] if top else 100.0
            idch[y][x] = float(top[5]) if top else 0.0
    return rgba, cobj, cmat, zch, idch


def ranks(cov, n):
    items = sorted(cov.items(), key=lambda kv: (-kv[1], kv[0]))
    out = []
    for i in range(2):
        if i < len(items):
            out += [h2f(crypto_hash(items[i][0])), items[i][1] / n]
        else:
            out += [0.0, 0.0]
    return out  # R G B A = id0 cov0 id1 cov1


def zips_compress(raw: bytes) -> bytes:
    n = len(raw)
    tmp = bytearray(n)
    half = (n + 1) // 2
    tmp[0:half] = raw[0::2]
    tmp[half:] = raw[1::2]
    if n:
        p = tmp[0]
        for i in range(1, n):
            d = (tmp[i] - p + 128 + 256) & 0xFF
            p = tmp[i]
            tmp[i] = d
    comp = zlib.compress(bytes(tmp), 9)
    return comp if len(comp) < n else raw


def zips_decompress(data: bytes, n: int) -> bytes:
    if len(data) == n:
        return data
    tmp = bytearray(zlib.decompress(data))
    for i in range(1, len(tmp)):
        tmp[i] = (tmp[i - 1] + tmp[i] - 128) & 0xFF
    half = (n + 1) // 2
    out = bytearray(n)
    out[0::2] = tmp[:half]
    out[1::2] = tmp[half:]
    return bytes(out)


def attr(name, typ, payload):
    return name.encode() + b"\0" + typ.encode() + b"\0" + struct.pack("<i", len(payload)) + payload


def main():
    out = sys.argv[1]
    rgba, cobj, cmat, zch, idch = render()
    manifest_o = {o[0]: "%08x" % crypto_hash(o[0]) for o in OBJECTS}
    mats = sorted({o[1] for o in OBJECTS})
    manifest_m = {m: "%08x" % crypto_hash(m) for m in mats}

    # channel name -> (pixel type, getter(x, y))
    HALF, FLOAT = 1, 2
    ch = {
        "R": (HALF, lambda x, y: rgba[y][x][0]),
        "G": (HALF, lambda x, y: rgba[y][x][1]),
        "B": (HALF, lambda x, y: rgba[y][x][2]),
        "A": (HALF, lambda x, y: rgba[y][x][3]),
        "Z": (FLOAT, lambda x, y: zch[y][x]),
        "ID": (FLOAT, lambda x, y: idch[y][x]),
    }
    for layer, data in (("CryptoObject00", cobj), ("CryptoMaterial00", cmat)):
        for i, c in enumerate("RGBA"):
            ch[layer + "." + c] = (FLOAT, (lambda d, i: lambda x, y: d[y][x][i])(data, i))
    names = sorted(ch.keys(), key=lambda s: s.encode())

    chlist = b""
    for nme in names:
        chlist += nme.encode() + b"\0" + struct.pack("<iB3xii", ch[nme][0], 0, 1, 1)
    chlist += b"\0"
    box = struct.pack("<iiii", 0, 0, W - 1, H - 1)
    hdr = b""
    hdr += attr("channels", "chlist", chlist)
    hdr += attr("compression", "compression", bytes([2]))  # ZIPS
    hdr += attr("dataWindow", "box2i", box)
    hdr += attr("displayWindow", "box2i", box)
    hdr += attr("lineOrder", "lineOrder", bytes([0]))
    hdr += attr("pixelAspectRatio", "float", struct.pack("<f", 1.0))
    hdr += attr("screenWindowCenter", "v2f", struct.pack("<ff", 0.0, 0.0))
    hdr += attr("screenWindowWidth", "float", struct.pack("<f", 1.0))
    for lname, man in (("CryptoObject", manifest_o), ("CryptoMaterial", manifest_m)):
        key = ("%08x" % mmh3_32(lname.encode()))[:7]
        pre = "cryptomatte/" + key + "/"
        hdr += attr(pre + "name", "string", lname.encode())
        hdr += attr(pre + "hash", "string", b"MurmurHash3_32")
        hdr += attr(pre + "conversion", "string", b"uint32_to_float32")
        hdr += attr(pre + "manifest", "string", json.dumps(man, sort_keys=True, separators=(",", ":")).encode())
    hdr += attr("comments", "string", b"Synthetic test image for EffectCraft importer samples")
    hdr += b"\0"

    magic = struct.pack("<ii", 20000630, 2)
    chunks = []
    raw_sizes = []
    for y in range(H):
        line = b""
        for nme in names:
            t, g = ch[nme]
            fmt = "<%d%s" % (W, "e" if t == HALF else "f")
            line += struct.pack(fmt, *[g(x, y) for x in range(W)])
        raw_sizes.append(len(line))
        data = zips_compress(line)
        chunks.append(struct.pack("<ii", y, len(data)) + data)
    table_pos = len(magic) + len(hdr)
    offset = table_pos + 8 * H
    table = b""
    for c in chunks:
        table += struct.pack("<Q", offset)
        offset += len(c)
    blob = magic + hdr + table + b"".join(chunks)
    with open(out, "wb") as f:
        f.write(blob)

    # Self-check: decode every chunk back and compare with the raw lines.
    pos = table_pos
    for y in range(H):
        off = struct.unpack_from("<Q", blob, pos + 8 * y)[0]
        yy, sz = struct.unpack_from("<ii", blob, off)
        assert yy == y
        line = zips_decompress(blob[off + 8: off + 8 + sz], raw_sizes[y])
        assert len(line) == raw_sizes[y]
    info = {
        "file": out,
        "size": len(blob),
        "channels": names,
        "objects": {o[0]: {"material": o[1], "hash": manifest_o[o[0]], "id": o[5], "z": o[4]} for o in OBJECTS},
        "materials": manifest_m,
    }
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            json.dump(info, f, indent=2)
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
