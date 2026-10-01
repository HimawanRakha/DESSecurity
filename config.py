KEY = "KIDES123"

HOST = "127.0.0.1"
PORT = 5000


def parse_key(text):
    if len(text) == 16:
        try:
            return bytes.fromhex(text)
        except ValueError:
            pass
    key = text.encode("utf-8")
    if len(key) != 8:
        raise ValueError("Key harus 8 karakter ASCII atau 16 digit hex")
    return key
