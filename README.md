# Tugas Individu KI — Komunikasi Dua Arah Terenkripsi DES

Simulasi transmisi ciphertext antara **Sender (A)** dan **Receiver (B)** melalui jaringan TCP.
Algoritma **DES diimplementasikan manual** (tanpa library enkripsi), menggunakan mode **CBC**
dan padding **PKCS#7**. Key sudah diketahui kedua pihak (*pre-shared*) dan **tidak pernah dikirim**.

## Pemenuhan Ketentuan Tugas

| No | Ketentuan | Penerapan |
|----|-----------|-----------|
| 1 | Komunikasi dua arah | Setelah terhubung, A dan B **sama-sama bisa mengirim dan menerima** (thread penerima di tiap sisi). |
| 2 | Key tidak dikirim | Key disimpan di `config.py` di kedua sisi. Paket hanya berisi `panjang + IV + ciphertext`. |
| 3 | Ada transmisi antar dua pihak | `sender.py` dan `receiver.py` adalah **dua program/proses terpisah** yang berkomunikasi lewat socket TCP (localhost, 2 laptop, atau VM). |
| 4 | Bahasa bebas | Python 3 (hanya library standar: `socket`, `threading`, `struct`, `argparse`). |
| 5 | Tanpa library enkripsi | Seluruh DES (IP, FP, E, P, PC-1, PC-2, S-Box, key schedule, 16 ronde Feistel), CBC, dan padding ditulis manual di `des.py`. |

## Struktur File

```
des.py        Implementasi DES manual + mode CBC + padding PKCS#7
config.py     Pre-shared key & alamat default (dipakai kedua pihak)
protocol.py   Format paket TCP (length-prefix + IV + ciphertext)
chat.py       Logika chat dua arah (enkripsi saat kirim, dekripsi saat terima)
receiver.py   Pihak B — server TCP
sender.py     Pihak A — client TCP
test_des.py   Uji DES dengan test vector standar (Grabbe & NIST SP 800-17)
```

## Cara Menjalankan

Kebutuhan: **Python 3.8+** (tidak perlu `pip install` apa pun).

### 1. Uji implementasi DES

```bash
python test_des.py
```

Semua test harus `OK`. Salah satu vektor uji: key `133457799BBCDFF1`, plaintext
`0123456789ABCDEF` → ciphertext `85E813540F0AB405`.

### 2. Satu laptop (localhost)

Buka **dua terminal** di folder project.

Terminal 1 — Receiver (jalankan lebih dulu):
```bash
python receiver.py
```

Terminal 2 — Sender:
```bash
python sender.py
```

Ketik pesan lalu Enter di salah satu terminal. Ketik `/exit` untuk keluar.

### 3. Dua laptop (satu jaringan WiFi/LAN)

1. Di laptop Receiver, cari IP dengan `ipconfig` (lihat *IPv4 Address*, contoh `192.168.1.10`).
2. Jalankan Receiver agar menerima koneksi dari luar (izinkan jika muncul prompt Windows Firewall):
   ```bash
   python receiver.py --host 0.0.0.0
   ```
3. Di laptop Sender:
   ```bash
   python sender.py --host 192.168.1.10
   ```

Opsi lain: `--port 6000` untuk ganti port, `--key XXXXXXXX` untuk ganti key (8 karakter atau 16 digit hex).

## Contoh Tampilan

Sisi Sender saat mengirim:
```
[20:04:04] [KIRIM ke Receiver B]
  Plaintext                : Halo B, ini pesan rahasia dari A!
  Plaintext (hex)          : 48616C6F20422C20 696E692070657361 6E20726168617369 6120646172692041 21
  Setelah padding (hex)    : 48616C6F20422C20 696E692070657361 6E20726168617369 6120646172692041 2107070707070707
  IV (hex)                 : C4175D2209052568
  Ciphertext (hex)         : 748A4CA33C88F256 C737EB8EFE7A52C6 BDEA0F77A7970690 27BB193658B7A5D9 B34A2C651E834598
  Paket dikirim (52 byte): 00 00 00 30 c4 17 5d 22 09 05 25 68 74 8a 4c a3 ...
```

Sisi Receiver saat menerima:
```
[20:04:04] [TERIMA dari Sender A]
  Paket mentah (52 byte) : 00 00 00 30 c4 17 5d 22 09 05 25 68 74 8a 4c a3 ...
  IV (hex)                 : C4175D2209052568
  Ciphertext (hex)         : 748A4CA33C88F256 C737EB8EFE7A52C6 BDEA0F77A7970690 27BB193658B7A5D9 B34A2C651E834598
  Hasil dekripsi           : Halo B, ini pesan rahasia dari A!
```

## Format Paket

```
+------------------+-------------+----------------------------+
| Panjang (4 byte) | IV (8 byte) | Ciphertext (kelipatan 8 B) |
+------------------+-------------+----------------------------+
```

- **Panjang**: big-endian, jumlah byte IV + ciphertext (misal `00 00 00 30` = 48 byte).
- **IV**: acak untuk tiap pesan. IV boleh terlihat (bukan rahasia) — fungsinya membuat pesan yang sama menghasilkan ciphertext berbeda.
- **Key tidak ada di dalam paket.**

## Capture di Wireshark (Nilai Tambah)

### Persiapan
Install Wireshark dari https://www.wireshark.org. Saat instalasi, pastikan **Npcap** ikut terinstal
dan centang opsi **"Support loopback traffic"** (wajib untuk demo di 1 laptop, karena trafik
localhost di Windows tidak melewati adapter WiFi/LAN).

### Langkah Demo
1. Buka Wireshark, pilih interface:
   - 1 laptop: **Adapter for loopback traffic capture**
   - 2 laptop: interface **Wi-Fi** / **Ethernet** yang dipakai
2. Isi display filter, lalu mulai capture:
   ```
   tcp.port == 5000 && tcp.len > 0
   ```
   (`tcp.len > 0` menyembunyikan paket handshake/ACK sehingga hanya paket berisi data yang tampil.)
3. Jalankan `receiver.py`, lalu `sender.py`, dan kirim beberapa pesan dari **kedua arah**.
4. Klik salah satu paket → lihat panel bawah (bytes). Payload TCP-nya **sama persis** dengan
   baris `Paket dikirim` / `Paket mentah` di terminal.
5. Klik kanan paket → **Follow → TCP Stream**. Terlihat isi percakapan hanya berupa karakter acak
   (ciphertext), **tidak ada plaintext maupun key**. Ubah *Show data as* ke **Hex Dump** untuk
   mencocokkan dengan hex di terminal. Warna merah/biru membedakan arah A→B dan B→A.

### Screenshot yang disarankan untuk laporan
- Terminal Sender & Receiver berdampingan (bukti komunikasi dua arah).
- Wireshark: daftar paket + panel hex payload, dengan hex yang sama terlihat di terminal.
- Wireshark: jendela *Follow TCP Stream* (bukti isi transmisi terenkripsi).
- (Bonus) Receiver dengan key salah → dekripsi gagal.

### Demo key salah (bonus)
```bash
python receiver.py --key KUNCISLH
```
```bash
python sender.py
```
Receiver akan menampilkan `[X] Dekripsi GAGAL` — membuktikan ciphertext hanya bisa dibuka
oleh pihak yang memegang key yang sama.

## Ringkasan Algoritma DES (di `des.py`)

1. **Key schedule** — key 64 bit → PC-1 (56 bit) → dibagi C & D (28 bit) → left shift per ronde →
   PC-2 → 16 subkey 48 bit.
2. **Enkripsi blok 64 bit** — Initial Permutation → 16 ronde Feistel
   (`L_i = R_{i-1}`, `R_i = L_{i-1} XOR f(R_{i-1}, K_i)`) → tukar L/R → Final Permutation.
3. **Fungsi f** — Expansion E (32→48 bit) → XOR subkey → 8 S-Box (48→32 bit) → Permutasi P.
4. **Dekripsi** — proses yang sama dengan urutan subkey dibalik (K16 … K1).
5. **CBC** — `C_i = E_K(P_i XOR C_{i-1})` dengan `C_0 = IV`; dekripsi `P_i = D_K(C_i) XOR C_{i-1}`.
6. **PKCS#7** — menambah `n` byte bernilai `n` agar panjang data kelipatan 8.

> Catatan: DES (key efektif 56 bit) sudah tidak dianggap aman untuk sistem nyata dan telah
> digantikan AES. Project ini dibuat untuk tujuan pembelajaran.
