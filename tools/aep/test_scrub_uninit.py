"""Regression tests of scrub-uninit.py on small synthetic projects:  python -I tools/aep/test_scrub_uninit.py"""
import importlib.util
import os
import struct
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("scrub_uninit", os.path.join(HERE, "scrub-uninit.py"))
su = importlib.util.module_from_spec(spec)
spec.loader.exec_module(su)


def chunk(cid, body):
    out = cid + struct.pack(">I", len(body)) + body
    return out + (b"\0" if len(body) & 1 else b"")


def lst(kind, *kids):
    body = kind + b"".join(kids)
    return b"LIST" + struct.pack(">I", len(body)) + body + (b"\0" if len(body) & 1 else b"")


def project(*kids):
    body = b"Egg!" + b"".join(kids)
    return b"RIFX" + struct.pack(">I", len(body)) + body


def utf16(text):
    return text.encode("utf-16-le")


def channel_info(name, before=b"", after=b""):
    """148 bytes: `before` at byte 0.., the NUL-terminated name at 19, `after` right behind it."""
    b = bytearray(148)
    b[0:len(before)] = before
    b[19:19 + len(name)] = name
    b[20 + len(name):20 + len(name) + len(after)] = after
    return bytes(b)


def run(data):
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "in"), os.path.join(d, "out")
        open(a, "wb").write(data)
        su.main(a, b)
        return open(b, "rb").read()


class ScrubUninit(unittest.TestCase):
    def test_exr_options_keep_the_first_47_bytes_and_lose_the_rest(self):
        opti = b"oEXR\0\1\0\0\x26\x16\1\0\0\0\2\0\1\0\x0e" + bytes(28) + b"\x10" * 3
        junk = bytearray(9750)
        junk[:len(opti)] = opti
        junk[126:126 + 20] = b"text of another tool"
        out = run(project(lst(b"Item", chunk(b"opti", bytes(junk)))))
        body = out[out.index(b"opti") + 8:][:9750]
        self.assertEqual(body[:47], bytes(junk[:47]))
        self.assertEqual(body[47:], bytes(9750 - 47))
        self.assertEqual(len(out), len(project(lst(b"Item", chunk(b"opti", bytes(junk))))))

    def test_a_solid_s_options_are_not_touched(self):
        solid = b"Soli" + bytes(6) + b"\xaa" * 40 + bytes(232)
        data = project(lst(b"Item", chunk(b"opti", solid)))
        self.assertEqual(run(data), data)

    def test_channel_info_loses_path_fragments_but_keeps_the_name(self):
        bs = chr(92)
        rec = channel_info(b"Object ID", utf16(bs + "dir"), b"\0" + utf16("fake" + bs + "folder" + bs) + b"\1\0\0\0")
        # a half character right in front of the name, as a cut-off pair
        rec = bytearray(rec)
        rec[8:8 + 10] = utf16("ab" + bs + "cd")
        rec[18] = ord("e")
        out = run(project(lst(b"Item", chunk(b"aRbp", bytes(rec)))))
        body = out[out.index(b"aRbp") + 8:][:148]
        self.assertEqual(body[19:28], b"Object ID")
        self.assertNotIn(b"d\0i\0r\0", body)
        self.assertNotIn(b"f\0a\0k\0", body)
        self.assertEqual(body[18], 0)
        self.assertEqual(su.channel_info_name_end(body), 29)

    def test_lumetri_data_loses_text_runs_in_its_unread_bytes_only(self):
        head = b"lumt" + b"\0\0\0\3" + b"\xff" * 16 + bytes(4) + b"\xff" * 4 + bytes(12) + b"\xff" * 4
        self.assertEqual(len(head), 48)
        text = utf16("path = E:/Dir")
        rec = head + text + bytes(104 - 48 - len(text))
        out = run(project(lst(b"Item", chunk(b"sdat", rec))))
        body = out[out.index(b"sdat") + 8:][:104]
        self.assertEqual(body[:48], head)
        self.assertEqual(body[48:], bytes(56))
        # a record with two 0.5 doubles and a pointer-like value has no text and is left alone
        clean = head + bytes(8) + b"\0\0\0\0\0\0\xe0\x3f" + bytes(16) + b"\0\0\0\0\0\0\xe0\x3f" + b"\xd0\x10\x57\x19\xfb\x7f\0\0"
        clean = clean + bytes(104 - len(clean))
        data = project(lst(b"Item", chunk(b"sdat", clean)))
        self.assertEqual(run(data), data)
        # other sdat records are not touched
        other = project(lst(b"Item", chunk(b"sdat", b"abcd" + utf16("path = text and more") + bytes(60))))
        self.assertEqual(run(other), other)

    def test_a_record_without_a_run_is_left_alone(self):
        rec = channel_info(b"Object ID", b"\1\0\0\0\x0f\0\0\0", b"\x2e\0" + bytes(10) + b"\x5f\0")
        data = project(lst(b"Item", chunk(b"aRbp", rec)))
        self.assertEqual(run(data), data)

    def test_other_aRbp_sizes_are_not_touched(self):
        data = project(lst(b"Item", chunk(b"aRbp", utf16("some other arbitrary data") + bytes(30))))
        self.assertEqual(run(data), data)

    def test_time_based_ids_lose_the_node_only(self):
        v1 = b'<guid>"cbbb21b4-d933-11f1-aae0-0a002700000c"</guid>'
        v4 = b'<guid>"cbbb21b4-d933-41f1-aae0-0a002700000c"</guid>'
        out = run(project(lst(b"Item", chunk(b"aRbp", v1 + v4 + b"\0"))))
        self.assertIn(b'"cbbb21b4-d933-11f1-aae0-000000000000"', out)
        self.assertIn(b'"cbbb21b4-d933-41f1-aae0-0a002700000c"', out)

    def test_opaque_lists_do_not_stop_the_scan(self):
        # a list whose body is not a chunk sequence (the text document): its bytes are left as they are
        odd = b"LIST" + struct.pack(">I", 16) + b"btdk" + b"\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x01"
        opti = b"oEXR" + b"\1" * 100 + bytes(9750 - 104)
        out = run(project(odd, lst(b"Item", chunk(b"opti", opti))))
        self.assertIn(odd, out)
        self.assertNotIn(b"\1" * 100, out)


if __name__ == "__main__":
    unittest.main()
