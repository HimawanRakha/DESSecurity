import os
import unittest

import des


class TestDESBlock(unittest.TestCase):
    VECTORS = [
        ("133457799BBCDFF1", "0123456789ABCDEF", "85E813540F0AB405"),
        ("0E329232EA6D0D73", "8787878787878787", "0000000000000000"),
        ("0101010101010101", "8000000000000000", "95F8A5E5DD31D900"),
        ("0101010101010101", "4000000000000000", "DD7F121CA5015619"),
        ("8001010101010101", "0000000000000000", "95A8D72813DAA94D"),
    ]

    def test_encrypt_known_vectors(self):
        for key, pt, ct in self.VECTORS:
            subkeys = des.generate_subkeys(bytes.fromhex(key))
            result = des.encrypt_block(bytes.fromhex(pt), subkeys)
            self.assertEqual(result.hex().upper(), ct, f"key={key} pt={pt}")

    def test_decrypt_known_vectors(self):
        for key, pt, ct in self.VECTORS:
            subkeys = des.generate_subkeys(bytes.fromhex(key))
            result = des.decrypt_block(bytes.fromhex(ct), subkeys)
            self.assertEqual(result.hex().upper(), pt, f"key={key} ct={ct}")


class TestPadding(unittest.TestCase):
    def test_pad_unpad(self):
        for n in range(0, 20):
            data = b"A" * n
            padded = des.pad(data)
            self.assertEqual(len(padded) % 8, 0)
            self.assertEqual(des.unpad(padded), data)

    def test_full_block_gets_extra_padding(self):
        self.assertEqual(des.pad(b"12345678"), b"12345678" + bytes([8] * 8))

    def test_invalid_padding(self):
        with self.assertRaises(ValueError):
            des.unpad(b"1234567\x05")


class TestCBC(unittest.TestCase):
    KEY = b"KIDES123"

    def test_roundtrip(self):
        for msg in [b"", b"Halo", b"Keamanan Informasi - DES CBC",
                    "Pesan UTF-8: café ✓".encode("utf-8"), os.urandom(100)]:
            iv = os.urandom(8)
            ct = des.cbc_encrypt(msg, self.KEY, iv)
            self.assertEqual(len(ct) % 8, 0)
            self.assertEqual(des.cbc_decrypt(ct, self.KEY, iv), msg)

    def test_same_plaintext_different_iv(self):
        msg = b"pesan yang sama"
        ct1 = des.cbc_encrypt(msg, self.KEY, os.urandom(8))
        ct2 = des.cbc_encrypt(msg, self.KEY, os.urandom(8))
        self.assertNotEqual(ct1, ct2)

    def test_wrong_key_fails(self):
        msg = b"rahasia negara!!"
        iv = os.urandom(8)
        ct = des.cbc_encrypt(msg, self.KEY, iv)
        try:
            result = des.cbc_decrypt(ct, b"KUNCISLH", iv)
        except ValueError:
            return
        self.assertNotEqual(result, msg)


if __name__ == "__main__":
    unittest.main(verbosity=2)
