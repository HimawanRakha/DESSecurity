import argparse
import socket

import config
from chat import run_chat


def main():
    parser = argparse.ArgumentParser(description="Sender (client) chat terenkripsi DES")
    parser.add_argument("--host", default=config.HOST, help="IP receiver (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=config.PORT, help="port (default 5000)")
    parser.add_argument("--key", default=config.KEY, help="pre-shared key DES (8 karakter / 16 hex)")
    args = parser.parse_args()

    key = config.parse_key(args.key)

    print("=" * 64)
    print("  SENDER (Pihak A) - Chat Terenkripsi DES-CBC")
    print("=" * 64)
    print(f"  Key DES (pre-shared, tidak dikirim): {key.hex().upper()}")
    print(f"  Menghubungkan ke {args.host}:{args.port} ...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((args.host, args.port))
    except OSError as e:
        print(f"  [!] Gagal terhubung: {e}")
        print("      Pastikan receiver.py sudah dijalankan lebih dulu.")
        return

    run_chat(sock, key, my_name="Sender A", peer_name="Receiver B")


if __name__ == "__main__":
    main()
