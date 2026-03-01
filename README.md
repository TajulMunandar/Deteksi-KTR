# 🚬 Monitoring Pelanggaran Merokok - Web App

Aplikasi web sederhana untuk monitoring pelanggaran merokok berbasis peta menggunakan Leaflet.js dan OpenStreetMap.

## 🌟 Fitur Utama

### A. Form Input Data
- ✅ Nama lokasi (text input)
- ✅ Kategori pelanggaran (dropdown):
  - Patuh
  - Pelanggaran Ringan (ada puntung rokok)
  - Pelanggaran Berat (orang merokok)
- ✅ Upload foto
- ✅ Latitude & Longitude (otomatis dari klik map)
- ✅ Tombol "Simpan Data"

### B. Peta Interaktif
- ✅ Tampilan peta penuh (full width)
- ✅ Klik peta → otomatis isi latitude & longitude
- ✅ Setelah disimpan → marker muncul di lokasi

### C. Warna Marker
- 🟢 Hijau → Patuh
- 🟡 Kuning → Pelanggaran Ringan
- 🔴 Merah → Pelanggaran Berat

### D. Popup Marker
- Nama lokasi
- Kategori
- Foto (preview)
- Koordinat
- Tombol hapus

### E. Fitur Tambahan
- ✅ Statistik jumlah pelanggaran
- ✅ Filter berdasarkan kategori
- ✅ Heatmap layer untuk pelanggaran berat
- ✅ Fungsi hapus marker individual
- ✅ Fungsi clear all data
- ✅ Validasi form sebelum simpan
- ✅ Data tersimpan di localStorage (tidak hilang saat refresh)

## 🛠️ Teknologi

- **HTML5** - Struktur halaman
- **CSS3** - Styling modern minimalis & responsive
- **Vanilla JavaScript** - Logika aplikasi
- **Leaflet.js** - Library peta (gratis)
- **OpenStreetMap** - Tile provider (gratis)
- **Python** - HTTP Server untuk menjalankan aplikasi

## 📁 Struktur File

```
Citra KTR Map/
├── index.html      # Halaman utama
├── style.css       # Styling CSS
├── script.js       # Logika JavaScript
├── server.py       # Python HTTP Server
├── README.md       # Dokumentasi ini
└── run.bat         # Jalankan di Windows
```

## 🚀 Cara Menjalankan

### Cara 1: Menggunakan Python (Disarankan)

1. Pastikan Python sudah terinstall
2. Buka terminal/command prompt
3. Jalankan perintah:
   ```bash
   python server.py
   ```
4. Browser akan otomatis terbuka

### Cara 2: Menggunakan run.bat (Windows)

1. Klik dua kali file `run.bat`
2. Browser akan otomatis terbuka

### Cara 3: Manual

1. Buka terminal di folder ini
2. Jalankan:
   ```bash
   python -m http.server 8000
   ```
3. Buka browser: http://localhost:8000

## 📱 Responsivitas

- **Desktop**: Form di kiri, peta di kanan
- **Mobile**: Form dan peta bertumpuk vertikal

## 💾 Penyimpanan Data

Data disimpan di `localStorage` browser, sehingga:
- Data tidak hilang saat halaman di-refresh
- Data tersimpan per browser yang digunakan

## 🎨 Desain

- Modern minimalis
- Warna: Biru utama (#2563eb)
- Responsive design
- Clean UI dengan ikon Font Awesome

## 📝 Cara Penggunaan

1. **Input Data**:
   - Isi nama lokasi
   - Pilih kategori pelanggaran
   - Upload foto (opsional)
   - Klik pada peta untuk memilih lokasi
   - Klik "Simpan Data"

2. **Melihat Marker**:
   - Marker akan muncul di peta sesuai lokasi
   - Klik marker untuk melihat detail

3. **Filter**:
   - Klik tombol filter untuk menampilkan kategori tertentu

4. **Heatmap**:
   - Aktifkan toggle heatmap untuk melihat konsentrasi pelanggaran berat

5. **Hapus Data**:
   - Klik tombol hapus pada popup marker
   - Atau klik "Hapus Semua Data" untuk menghapus semua

## 🔧 Troubleshooting

### Peta tidak muncul?
- Pastikan koneksi internet aktif
- Pastikan port 8000 tidak digunakan aplikasi lain

### Foto tidak tersimpan?
- localStorage memiliki batas ukuran
- Coba gunakan foto dengan ukuran lebih kecil

### Marker tidak muncul?
- Periksa apakah JavaScript diizinkan
- Cek console browser untuk error

## 📄 Lisensi

Open Source - Gratis untuk digunakan

---

Dibuat dengan ❤️ untuk monitoring pelanggaran merokok
