import argparse
import socket

import config
from chat import run_chat


def main():
    parser = argparse.ArgumentParser(description="Receiver (server) chat terenkripsi DES")
    parser.add_argument("--host", default=config.HOST, help="alamat bind (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=config.PORT, help="port (default 5000)")
    parser.add_argument("--key", default=config.KEY, help="pre-shared key DES (8 karakter / 16 hex)")
    args = parser.parse_args()

    key = config.parse_key(args.key)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.host, args.port))
    server.listen(1)

    print("=" * 64)
    print("  RECEIVER (Pihak B) - Chat Terenkripsi DES-CBC")
    print("=" * 64)
    print(f"  Key DES (pre-shared, tidak dikirim): {key.hex().upper()}")
    print(f"  Menunggu koneksi di {args.host}:{args.port} ...")

    try:
        conn, addr = server.accept()
    except KeyboardInterrupt:
        print("\nDibatalkan.")
        return
    finally:
        server.close()

    print(f"  Sender terhubung dari {addr[0]}:{addr[1]}")
    run_chat(conn, key, my_name="Receiver B", peer_name="Sender A")


if __name__ == "__main__":
    main()
