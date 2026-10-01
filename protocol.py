import struct

HEADER_SIZE = 4
IV_SIZE = 8


def build_packet(iv, ciphertext):
    body = iv + ciphertext
    return struct.pack(">I", len(body)) + body


def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def recv_packet(sock):
    header = recv_exact(sock, HEADER_SIZE)
    if header is None:
        return None
    (length,) = struct.unpack(">I", header)
    body = recv_exact(sock, length)
    if body is None:
        return None
    return header + body, body[:IV_SIZE], body[IV_SIZE:]
