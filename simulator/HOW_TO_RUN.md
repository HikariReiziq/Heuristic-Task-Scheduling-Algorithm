# Panduan Eksekusi Cloud Task Scheduling Simulator (CCTSA)
**Mata Kuliah**: Strategi Optimasi Komputasi Awan (SOKA) - Kelas C  
**Dosen Pengampu**: Dr. Ir. Henning Titi Ciptaningtyas, S.Kom., M.Kom.  
**Institusi**: Departemen Teknologi Informasi, FTEIC, Institut Teknologi Sepuluh Nopember (ITS) Surabaya — 2026  
**Kelompok 4**:
1. I Dewa Made Satya Raditya (5027231051)
2. Ahmad Wildan Fawwaz (5027241001)
3. Muhammad Rakha Hananditya Rauf (5027241015)
4. Theodorus Aaron Ugraha (5027241056)
5. M. Hikari Reiziq Rakhmadinta (5027241079)

---

## 🧭 1. Ringkasan & Arsitektur Modul

Simulator ini mereproduksi dan memvalidasi algoritma heuristik penjadwalan cloud **CCTSA (Cost and Completion Time based Sufferage Algorithm)** dari paper:
> *H. Krishnaveni, Dr. D. I. George Amalarethinam, Dr. V. Sinthu Janita (IJRECE 2019)*  
> **"Cost and Completion Time based Sufferage Algorithm for Task Scheduling in Cloud Environment"**

### Algoritma yang Tersedia:
1. **CCTSA** (*Proposed Algorithm*): Dual Sufferage Metric ($SVCT$ dan $SVC$) sadar-biaya dan sadar-waktu.
2. **ETSA** (*Baseline Paper*): Sufferage berbasis waktu penyelesaian murni (Krishnaveni & Sinthu Janita, Springer 2019).
3. **Standard Sufferage**: Algoritma sufferage klasik industri (Maheswaran et al., 1999).
4. **Min-Min**: Pembanding heuristik standar komputasi terdistribusi.
5. **Round Robin (RR)**: Pembanding pemetaan sekuensial tanpa kesadaran beban.

---

## 💻 2. Persyaratan Sistem & Lingkungan Fedora Linux

Simulator dirancang menggunakan **Python 3 Standard Library** (tidak memerlukan instalasi `pip` tambahan) serta mendukung konversi grafik via Node.js:

```bash
# Verifikasi Python 3 (Tersedia default di Fedora)
python3 --version

# (Opsional) Jika ingin mengompilasi referensi Java CloudSim:
sudo dnf install -y java-21-openjdk-devel maven
```

---

## 🚀 3. Cara Menjalankan Simulator

Masuk ke direktori simulator:
```bash
cd "/home/reiziqzip/Documents/SOKA/Algoritma Heuristik/simulator"
```

### Opsi A: Jalankan Seluruh Skenario (Semua Dataset + Ekspor Grafik)
```bash
python3 run_simulation.py --scenario all
```

### Opsi B: Jalankan Skenario 1 (Validasi Tabel III: 10 Task pada 3 VM)
```bash
python3 run_simulation.py --scenario 1
```

### Opsi C: Jalankan Skenario 2 (Uji Skalabilitas Tabel IV, V, VI: 25 s.d. 200 Task)
```bash
python3 run_simulation.py --scenario 2
```

### Opsi D: Jalankan Skenario GoCJ (Google Cloud Jobs: 1.000 Task pada 50 VM)
```bash
python3 run_simulation.py --scenario gocj
```

### Opsi E: Jalankan Skenario Tugas 2A/2B (Desain Infrastruktur: 1.000 Task @ 50.000 MI pada 50 VM)
```bash
python3 run_simulation.py --scenario tugas2a
```

### Opsi F: Jalankan Skenario Maheswaran ETC (Inconsistent HiHi: 512 Task pada 16 VM)
```bash
python3 run_simulation.py --scenario maheswaran
```

### Opsi G: Jalankan Interactive Web Dashboard (Zero-Dependency) 🌐
Sangat disarankan saat **presentasi demo di hadapan dosen**:
```bash
# Jalankan web server lokal bawaan Python (Port 8080):
python3 serve_dashboard.py
# Lalu buka browser di: http://localhost:8080
```
*(Atau Anda bisa langsung mengklik ganda file `dashboard.html` di file manager untuk membukanya di browser secara instan tanpa perlu web server)*.

#### Fitur Dashboard Terintegrasi:
- **Terminal Console Interaktif (Di Tengah Layar)**:
  Dilengkapi tombol jalan cepat (`[ ▶ Run All ]`, `[ 🏢 Tugas 2A ]`, `[ 🌐 GoCJ ]`, `[ 📖 Tabel III ]`, `[ ⚡ Maheswaran ]`).
  Tombol ini terhubung ke backend `serve_dashboard.py` melalui API `/api/run?scenario=...` yang mengeksekusi simulator secara nyata (*live execution*) dan menampilkan output log warna ANSI secara langsung.
- **Profil 5 Anggota Tim**: Menampilkan foto asli dari folder `image/`, nama lengkap, dan NRP.
- **Sinkronisasi Otomatis Data `results/`**: Seluruh angka Makespan, Biaya, Utilisasi, dan DI yang tampil pada kartu KPI dan chart dibaca langsung dari file `results/simulation_summary.json`.
- **Galeri Gambar Hasil Simulasi**: Gambar plot PNG/SVG dari folder `results/` dapat dilihat dan diunduh langsung dari web.

### Opsi H: Jalankan Dashboard Streamlit (Integrasi Repositori Ronn / Theo) 🎨
Jika lingkungan Python Anda memiliki `streamlit`, `pandas`, dan `plotly`:
```bash
streamlit run app.py
```
*(File data `hasil_simulasi_cloudsim.csv` sudah otomatis ter-generate dan kompatibel 100%)*.

---

## 🧪 4. Menjalankan Unit Test Otomatis

Untuk memverifikasi kebenaran matematis matriks ETC, ECC, metrik Makespan, Cost, RU, DI, dan generator beban:
```bash
python3 test_simulator.py
```
*Output yang diharapkan:* `Ran 11 tests in 0.006s ... OK`

---

## 📊 5. Hasil Output & Visualisasi Grafik (Folder results/)

Setiap eksekusi akan otomatis memperbarui file di folder `results/`:

| Nama File | Deskripsi & Kegunaan |
| :--- | :--- |
| **`dashboard.html`** | Single-file Web Dashboard interaktif lengkap dengan terminal console dan chart interaktif. |
| **`simulation_summary.json`** | Rekapitulasi data numerik lengkap seluruh skenario dalam format JSON terstruktur. |
| **`scenario5_tugas2a_comparison.png`** | Grafik Makespan vs Utilisasi pada desain infrastruktur Tugas 2A / 2B Kelompok 4 (PNG/SVG). |
| **`scenario3_gocj_cost_makespan.png`** | Grafik Makespan vs Biaya Finansial pada beban kerja nyata Google Cloud Jobs (PNG/SVG). |
| **`scenario4_maheswaran_etc_comparison.png`**| Grafik Makespan vs Utilisasi pada benchmark heterogenitas ekstrim Maheswaran (PNG/SVG). |
| **`scenario1_cost_comparison.png`** | Grafik perbandingan Biaya Eksekusi Finansial (Rs) (Skenario 1 - Tabel III). |
| **`scenario1_makespan_comparison.png`** | Grafik perbandingan Makespan antar 5 algoritma (Skenario 1 - Tabel III). |
| **`scenario1_resource_utilization.png`** | Grafik perbandingan Utilisasi Sumber Daya (%) (Skenario 1 - Tabel III). |
| **`scenario2_scalability_cost.png`** | Kurva tren efisiensi biaya CCTSA vs ETSA pada 25–200 task. |
| **`scenario2_scalability_utilization.png`**| Kurva stabilitas utilisasi sumber daya CCTSA vs ETSA. |
| **`scenario1_comparison.csv`** | Tabel komparasi Makespan, Cost, RU, DI, dan Waiting Time (Skenario 1 - Tabel III). |
| **`scenario2_scalability.csv`** | Evaluasi skalabilitas beban 25 s.d. 200 task (Skenario 2 - Tabel IV, V, VI). |
| **`scenario3_gocj.csv`** | Data komparasi 5 algoritma pada dataset Google Cloud Jobs (1.000 task pada 50 VM). |
| **`scenario4_maheswaran.csv`** | Evaluasi matriks ETC Maheswaran JPDC 1999 (Inconsistent HiHi 512 task pada 16 VM). |
| **`scenario5_tugas2a.csv`** | Evaluasi infrastruktur SOKA Tugas 2A (1.000 task @ 50.000 MI pada 50 VM). |
| **`hasil_simulasi_cloudsim.csv`** | Log alokasi task rinci 5.000 baris kompatibel standar CloudSim. |
| **`hasil_ringkasan_algoritma.csv`** | Ringkasan skor gabungan dan ranking efisiensi algoritma. |
| **`task_allocations.csv`** | Log jejak alokasi task ke VM (start time, finish time, cost, waiting time). |

---

## 📐 6. Formulasi Matematis yang Diimplementasikan

1. **Waktu Eksekusi (Execution Time)**:
   $$\text{Execution Time}_{ij} = \left( \frac{MI_i}{MIPS_j} \right) + \left( \frac{Mb_i}{Mbps_j} \right)$$

2. **Biaya Eksekusi (Execution Cost)**:
   $$\text{Execution Cost}_{ij} = MI_i \times \text{CostRate}_j \text{ (INR)}$$

3. **Dual Sufferage CCTSA**:
   $$SVCT_i = SMICT_i - FMICT_i \quad (\text{Sufferage Waktu Selesai})$$
   $$SVC_i = FMXC_i - SMXC_i \quad (\text{Sufferage Biaya Maksimum})$$
   $$\text{Kondisi Seleksi: } (SVCT_i > FMICT_i) \quad \mathbf{AND} \quad (SVC_i < FMXC_i)$$

4. **Metrik Utilisasi Sumber Daya (Resource Utilization)**:
   $$RU = \left( \frac{\sum_{j=1}^M RT_j}{M \times \text{Makespan}} \right) \times 100\%$$

5. **Tingkat Ketidakseimbangan Beban (Degree of Imbalance - DI)**:
   $$DI = \frac{RT_{\max} - RT_{\min}}{\overline{RT}}$$

---

## ☕ 7. Struktur Referensi Java CloudSim 3.0

Untuk keperluan pelaporan akademik yang mencerminkan lingkungan NetBeans IDE pada paper (`Implementation_Window.png`), kode sumber Java murni tersedia pada direktori:
```
Algoritma Heuristik/java_reference/
├── CostCTSA.java   # Kelas utama algoritma usulan CCTSA
├── ETSA.java       # Kelas algoritma baseline ETSA
├── Sufferage.java  # Kelas algoritma Standard Sufferage
├── Details.java    # Data spesifikasi Tabel I (R1-R3) & Tabel II (T1-T10)
└── TaskTime.java   # Struktur data pemetaan task dan waktu
```

Eksekusi referensi Java (jika `java` terinstal):
```bash
cd "/home/reiziqzip/Documents/SOKA/Algoritma Heuristik/java_reference"
# Kompilasi:
javac cost/*.java 2>/dev/null || javac *.java
# Jalankan CCTSA:
java cost.CostCTSA
```

---

## 🔗 8. Relevansi Strategis Kelompok 4 (Bridge to Final Project)

Hasil implementasi Tugas 3 ini membuktikan bahwa:
1. **Trade-off Sadar-Biaya**: Memilih mesin tercepat secara membabi-buta (seperti pada ETSA/Min-Min) menghasilkan lonjakan biaya finansial yang merugikan penyewa cloud.
2. **Kesesuaian Fog-Cloud**: CCTSA membuktikan bahwa alokasi heterogen mampu mendistribusikan task tanpa membebani mesin berbiaya tinggi.
3. **Inisialisasi Metaheuristik (PSO Seeding)**: Solusi pemetaan deterministik dari CCTSA akan diintegrasikan sebagai *initial particle / seeding* untuk algoritma **Hybrid Multi-Objective PSO** pada arsitektur Fog-Cloud 3-Tier Kelompok 4 (Tugas 2B) guna mempercepat konvergensi Pareto-optimal.
