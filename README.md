# Coral Island Auto Fishing Bot

Skrip otomasi pemancingan untuk permainan **Coral Island** yang memungkinkan Anda melakukan pemancingan secara otomatis.

## Demo Video

[![Demo Video](https://img.youtube.com/vi/VnfF0kdlxws/maxresdefault.jpg)](https://www.youtube.com/embed/VnfF0kdlxws?si=juma4heQRZQj2xkB)

## Fitur

- Deteksi otomatis bar pancing menggunakan template gambar.
- Mode klik cepat dan lambat berdasarkan kondisi permainan.
- Logging untuk memantau aktivitas skrip.
- Pengaturan mudah melalui parameter.

## Prasyarat

- Python 3.7 atau lebih baru
- Pip

## Instalasi

1. **Clone repositori ini:**

    ```bash
    git clone https://github.com/Gh05t666nero/Coral-Island-Auto-Fishing
    cd Coral-Island-Auto-Fishing
    ```

2. **Buat dan aktifkan virtual environment (opsional tetapi direkomendasikan):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Untuk Linux/Mac
    venv\Scripts\activate     # Untuk Windows
    ```

3. **Install dependensi:**

    ```bash
    pip install -r requirements.txt
    ```

## Penggunaan

1. **Pastikan semua template gambar berada di direktori `assets/`.**

2. **Jalankan skrip:**

    ```bash
    python src/main.py --debug
    ```

    - Tambahkan `--debug` untuk mengaktifkan mode debug yang memberikan logging lebih rinci.

3. **Kontrol Skrip:**

    - Tekan `q` pada keyboard untuk menghentikan skrip dengan aman.

## Kontribusi

Kontribusi sangat kami hargai! Silakan ikuti langkah berikut:

1. Fork repositori ini.
2. Buat branch fitur baru (`git checkout -b fitur/baru`).
3. Commit perubahan Anda (`git commit -m 'Tambah fitur baru'`).
4. Push ke branch (`git push origin fitur/baru`).
5. Buat Pull Request.

## Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

## Kontak

Untuk pertanyaan lebih lanjut, silakan hubungi [kontak@fauzan.biz.id](mailto:kontak@fauzan.biz.id).
