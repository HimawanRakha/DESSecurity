import os
import threading
from datetime import datetime

import des
from protocol import build_packet, recv_packet

print_lock = threading.Lock()
LINE = "-" * 64


def hex_blocks(data):
    h = data.hex().upper()
    return " ".join(h[i:i + 16] for i in range(0, len(h), 16))


def hex_bytes(data):
    return " ".join(f"{b:02x}" for b in data)


def now():
    return datetime.now().strftime("%H:%M:%S")


def log(lines, prompt):
    with print_lock:
        print("\r" + "\n".join(lines))
        print(prompt, end="", flush=True)


def receive_loop(sock, key, peer_name, prompt, stop_event):
    while not stop_event.is_set():
        try:
            packet = recv_packet(sock)
        except OSError:
            packet = None

        if packet is None:
            if not stop_event.is_set():
                log([LINE, f"[!] Koneksi ditutup oleh {peer_name}. Tekan Enter untuk keluar."], "")
            stop_event.set()
            break

        raw, iv, ciphertext = packet
        lines = [
            LINE,
            f"[{now()}] [TERIMA dari {peer_name}]",
            f"  Paket mentah ({len(raw)} byte) : {hex_bytes(raw)}",
            f"  IV (hex)                 : {iv.hex().upper()}",
            f"  Ciphertext (hex)         : {hex_blocks(ciphertext)}",
        ]
        try:
            plaintext = des.cbc_decrypt(ciphertext, key, iv)
            lines.append(f"  Hasil dekripsi           : {plaintext.decode('utf-8', errors='replace')}")
        except ValueError as e:
            lines.append(f"  [X] Dekripsi GAGAL       : {e} (key berbeda?)")
        lines.append(LINE)
        log(lines, prompt)


def run_chat(sock, key, my_name, peer_name):
    prompt = f"[{my_name}] > "
    stop_event = threading.Event()

    print(LINE)
    print(f"Terhubung dengan {peer_name}. Ketik pesan lalu Enter.")
    print("Ketik /exit untuk keluar.")
    print(LINE)

    receiver = threading.Thread(
        target=receive_loop,
        args=(sock, key, peer_name, prompt, stop_event),
        daemon=True,
    )
    receiver.start()

    try:
        while not stop_event.is_set():
            with print_lock:
                print(prompt, end="", flush=True)
            text = input()
            if stop_event.is_set():
                break
            if text.strip() == "":
                continue
            if text.strip() == "/exit":
                break

            plaintext = text.encode("utf-8")
            iv = os.urandom(8)
            ciphertext = des.cbc_encrypt(plaintext, key, iv)
            packet = build_packet(iv, ciphertext)
            sock.sendall(packet)

            log([
                LINE,
                f"[{now()}] [KIRIM ke {peer_name}]",
                f"  Plaintext                : {text}",
                f"  Plaintext (hex)          : {hex_blocks(plaintext)}",
                f"  Setelah padding (hex)    : {hex_blocks(des.pad(plaintext))}",
                f"  IV (hex)                 : {iv.hex().upper()}",
                f"  Ciphertext (hex)         : {hex_blocks(ciphertext)}",
                f"  Paket dikirim ({len(packet)} byte): {hex_bytes(packet)}",
                LINE,
            ], "")
    except (KeyboardInterrupt, EOFError):
        pass
    except OSError as e:
        print(f"\n[!] Gagal mengirim: {e}")
    finally:
        stop_event.set()
        try:
            sock.close()
        except OSError:
            pass
        print("\nKoneksi ditutup.")
