"""Regression tests of inspect-embedded.py on small synthetic inputs:  python -I tools/aep/test_inspect_embedded.py"""
import base64
import binascii
import importlib.util
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("inspect_embedded", os.path.join(HERE, "inspect-embedded.py"))
ie = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ie)


def stub(desc="sRGB IEC61966-2.1"):
    """What stubicc.rs writes: header, one desc tag, nothing else."""
    body = b"desc\0\0\0\0" + (len(desc) + 1).to_bytes(4, "big") + desc.encode() + b"\0" + bytes(78)
    p = bytearray(128)
    p[8:12] = (0x02400000).to_bytes(4, "big")
    p[12:24] = b"mntrRGB XYZ "
    p[36:40] = b"acsp"
    p += (1).to_bytes(4, "big") + b"desc" + (144).to_bytes(4, "big") + len(body).to_bytes(4, "big") + body
    p[:4] = len(p).to_bytes(4, "big")
    return bytes(p)


def with_tag(tag, payload):
    """A profile of one tag that is not a desc text (a curve), as a 'clean' stub would be faked."""
    p = bytearray(128)
    p[8:12] = (0x02400000).to_bytes(4, "big")
    p[12:24] = b"mntrRGB XYZ "
    p[36:40] = b"acsp"
    p += (1).to_bytes(4, "big") + tag + (144).to_bytes(4, "big") + len(payload).to_bytes(4, "big") + payload
    p[:4] = len(p).to_bytes(4, "big")
    return bytes(p)


def run(data, forbid=()):
    profiles, strings = [], []
    ie.scan(data, "raw", 2, ie.VENDOR + list(forbid), profiles, strings)
    return profiles, strings


class StubStructure(unittest.TestCase):
    def test_the_real_stub_is_accepted(self):
        self.assertIsNone(ie.stub_problem(stub()))
        self.assertEqual(ie.description(stub("Rec.709 Gamma 2.4")), "Rec.709 Gamma 2.4")

    def test_a_curve_tag_payload_is_not_a_stub(self):
        curve = b"curv" + bytes(4) + (256).to_bytes(4, "big") + bytes(512)
        p = with_tag(b"rTRC", curve)
        self.assertLess(len(p), 1000)
        self.assertIsNotNone(ie.stub_problem(p))
        self.assertIsNotNone(ie.stub_problem(with_tag(b"desc", curve)))

    def test_trailing_bytes_header_fields_and_a_wrong_size_are_not_a_stub(self):
        self.assertIsNotNone(ie.stub_problem(stub() + b"\0"))
        bad = bytearray(stub())
        bad[60] = 1  # a header field outside the fixed ones
        self.assertIsNotNone(ie.stub_problem(bytes(bad)))
        bad = bytearray(stub())
        bad[-1] = 7  # colour-looking data in the zero tail
        self.assertIsNotNone(ie.stub_problem(bytes(bad)))
        short = bytearray(stub())
        short[:4] = (len(short) - 1).to_bytes(4, "big")
        self.assertIsNotNone(ie.stub_problem(bytes(short)))

    def test_a_stub_is_found_raw_in_base64_and_in_hex(self):
        d = b"x" * 10 + stub() + b"y" * 10
        self.assertEqual(len(run(d)[0]), 1)
        self.assertEqual(len(run(b'{"colorProfileData":"' + base64.b64encode(stub()) + b'"}')[0]), 1)
        self.assertEqual(len(run(b'<x bdata="' + binascii.hexlify(stub()) + b'"/>')[0]), 1)
        self.assertEqual(len(run(base64.b64encode(binascii.hexlify(stub())))[0]), 1, "hex inside base64")


class Markers(unittest.TestCase):
    TEXT = "Hewlett-Packard"

    def assertFound(self, data, text=None):
        self.assertIn(text or self.TEXT, [s.split(" (")[0] for s in run(data, [text] if text else [])[1]], data[:60])

    def test_every_representation_is_found(self):
        t = self.TEXT
        self.assertFound(b"..." + t.encode() + b"...")
        self.assertFound(b"..." + t.lower().encode() + b"...")
        self.assertFound(t.encode("utf-16-le"))
        self.assertFound(t.encode("utf-16-be"))
        self.assertFound(binascii.hexlify(t.encode()))
        self.assertFound(binascii.hexlify(t.encode()).upper())
        self.assertFound(binascii.hexlify(t.encode("utf-16-be")))

    def test_base64_in_every_alignment(self):
        t = self.TEXT.encode()
        for shift in range(3):
            self.assertFound(base64.b64encode(bytes([65] * shift) + t + b"tail"))
        self.assertFound(b'{"a":"' + base64.b64encode(b"prefix, " + t) + b'"}')

    def test_nested_and_long_runs_are_decoded(self):
        t = self.TEXT.encode()
        payload = bytes(300) + t + bytes(300)
        self.assertFound(b"<x bdata=\"" + binascii.hexlify(payload) + b"\"/>")
        self.assertFound(b'{"v":"' + base64.b64encode(payload) + b'"}')
        self.assertFound(base64.b64encode(binascii.hexlify(payload)))

    def test_a_forbidden_text_is_found_the_same_way(self):
        self.assertFound(base64.b64encode(b"C:/Users/jdoe/x"), "jdoe")
        self.assertFound(binascii.hexlify("jdoe".encode("utf-16-be")), "jdoe")
        self.assertEqual(run(b"nothing here", ["jdoe"])[1], [])

    def test_clean_bytes_have_no_hits(self):
        self.assertEqual(run(os.urandom(4000) if False else bytes(range(256)) * 16)[1], [])


class Traversal(unittest.TestCase):
    def test_directories_are_searched_recursively_and_expect_counts(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "inputs"))
            for rel in ["a.aep", "inputs/p.ffx", "inputs/ignored.txt"]:
                open(os.path.join(d, rel), "wb").write(stub())
            _, files, _ = ie.collect([d])
            self.assertEqual([os.path.basename(f) for f in files], ["a.aep", "p.ffx"])
            self.assertEqual(ie.main([d, "--expect", "2"]), 0)
            self.assertEqual(ie.main([d, "--expect", "3"]), 1)

    def test_a_forbidden_text_or_a_curve_profile_fails_the_run(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "ok.aep"), "wb").write(stub())
            self.assertEqual(ie.main([d]), 0)
            open(os.path.join(d, "bad.aep"), "wb").write(with_tag(b"rTRC", b"curv" + bytes(300)))
            self.assertEqual(ie.main([d]), 1)
            os.remove(os.path.join(d, "bad.aep"))
            open(os.path.join(d, "name.aep"), "wb").write(stub() + base64.b64encode(b"jdoe-laptop"))
            self.assertEqual(ie.main([d, "--forbid", "jdoe"]), 1)


if __name__ == "__main__":
    unittest.main()
