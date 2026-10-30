# 🌐 WasrikAgent AI 2.0 - Standalone External Data Services (DS-001 s/d DS-006)

Repositori ini berisi **6 Web Service & REST API Mandiri** untuk menyimulasikan ekosistem data eksternal lintas-kementerian/lembaga yang diintegrasikan oleh **WasrikAgent AI 2.0** (BPJS Kesehatan Healthkathon 2026 - Kategori 3: Efisiensi Risiko Pemberi Kerja).

Setiap service memiliki:
1. Folder independen dengan file dataset JSON bawaan (`data.json`).
2. Web Dashboard interaktif modern berbasis Tailwind CSS (Dark Mode).
3. REST API performa tinggi berbasis FastAPI & Uvicorn.
4. OpenAPI / Swagger Documentation interaktif pada `/docs`.
5. Sanitasi perlindungan data pribadi sesuai amanat **UU Perlindungan Data Pribadi (UU PDP No. 27/2022)** dan **PP No. 86 Tahun 2013**.

---

## 📋 Matriks Pemetaan Dataset & Port

| ID Data | Nama Dataset & Instansi | Protokol & Format | Frekuensi Update | Port | Endpoint REST Utama | Ketentuan Sanitasi UU PDP |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **DS-001** | **Master Badan Usaha**<br>*(BPJS Kesehatan & TK)* | REST API / JSON | Bulanan | `9001` | `GET /api/v1/employers`<br>`GET /api/v1/employers/{nib}` | NIB Public, Nama disamarkan dalam Sandbox mode |
| **DS-002** | **Data Upah Terlaporkan**<br>*(BPJS Ketenagakerjaan / SIPP)* | Encrypted CSV & REST API | Bulanan | `9002` | `GET /api/v1/wages`<br>`GET /api/v1/wages/export/csv` | **NIK SHA-256 Salted Hashing Wajib** (`salt_wasrik_2026`) |
| **DS-003** | **Data WLKP**<br>*(SIAPkerja Kemnaker RI)* | API Gateway / REST API | Triwulanan | `9003` | `GET /api/v1/wlkp/reports`<br>`GET /api/v1/wlkp/summary` | **Agregat Data Non-PII** (Komposisi PKWTT/PKWT & Total Payroll) |
| **DS-004** | **Data Iuran & Piutang**<br>*(BPJS Kesehatan Finansial)* | Database View / JSON | Real-Time / Harian | `9004` | `GET /api/v1/billing`<br>`GET /api/v1/billing/arrears` | **Data Finansial Enterprise** (VA, Tagihan 4%+1%, Denda) |
| **DS-005** | **Data Klaim Medis & MCU**<br>*(BPJS Kesehatan Healthkathon)* | Sample Batch / REST API | Tahunan / Batch | `9005` | `GET /api/v1/claims`<br>`GET /api/v1/claims/company/{id}` | **Anonymized Patient Pseudo-ID** & ICD-10 Morbiditas Kerja |
| **DS-006** | **Master Sanksi TMP2T**<br>*(BKPM OSS & DPMPTSP)* | Webhooks / REST API | Event-Driven / Real-Time | `9006` | `GET /api/v1/sanctions`<br>`POST /api/v1/sanctions/issue` | **Public Corporate Sanction Record** (PP 86/2013 jo. UU 24/2011) |

---

## 🏢 Grounding Entitas Badan Usaha (Cross-Validation Alignment)

Keenam dataset secara konsisten memuat 6 Badan Usaha terdaftar yang merefleksikan skenario audit Wasrik:

1. **`BU-001` - PT Cipta Busana Mandiri** (NIB: `0123456789012`):
   - SIPP Upah: Rp 2.800.000 (120 pekerja) vs WLKP Kemnaker: Rp 4.500.000 (165 pekerja).
   - **Temuan Wasrik**: Indikasi Anomali PDUK (45 pekerja kontrak belum didaftarkan) & Selisih Upah Riil.
2. **`BU-002` - PT Sumber Maju Sentosa** (NIB: `9876543210987`):
   - SIPP Upah: Rp 5.300.000 (320 pekerja) vs WLKP Kemnaker: Rp 8.500.000 (465 pekerja).
   - **Temuan Wasrik**: Selisih PDUK 145 pekerja, status Sanksi Aktif Teguran I (PP 86/2013).
3. **`BU-003` - PT Indo Mandiri Perkasa** (NIB: `1122334455667`):
   - SIPP Upah: Rp 4.500.000 (200 pekerja) vs WLKP Kemnaker: Rp 6.200.000 (280 pekerja).
   - **Temuan Wasrik**: Selisih PDUK 80 pekerja, klaim penyakit akibat kerja (dermatitis kontak).
4. **`BU-004` - PT Sinar Maju Tekstil** (NIB: `5566778899001`):
   - SIPP: 85 pekerja vs WLKP: 85 pekerja (100% Cocok).
   - **Temuan Wasrik**: Badan Usaha Patuh (Good Governance).
5. **`BU-005` - PT Delta Logistik Nusantara** (NIB: `3344556677889`):
   - Data Iuran: Tunggakan pembayaran 2 bulan (Rp 45.760.000 + denda Rp 915.200).
   - **Temuan Wasrik**: Surat Peringatan SP-2 terbit, risiko penonaktifan kartu peserta JKN.
6. **`BU-006` - PT Global Prima Elektronik** (NIB: `7788990011223`):
   - Data Iuran: Nunggak 4 bulan (Rp 81.200.000).
   - **Temuan Wasrik**: Sanksi Akhir TMP2T (Tidak Mendapat Pelayanan Publik Tertentu) aktif di BKPM OSS (Blokir PBG, Izin Usaha, Ekspor-Impor, dan Tender Pengadaan Barang/Jasa Pemerintah).

---

## 🚀 Panduan Menjalankan

### Cara 1: Menggunakan Master Script `run_all.py` (Disarankan)

```bash
cd "D:\projek warasik\WEB DATA"

# 1. Menjalankan semua 6 web service sekaligus di background
python run_all.py start

# 2. Mengecek status port dan endpoint
python run_all.py status

# 3. Menghentikan semua 6 web service
python run_all.py stop
```

### Cara 2: Menjalankan Per Service Secara Mandiri

Buka terminal pada masing-masing direktori service:
```bash
# Menjalankan DS-001 (Port 9001)
cd "D:\projek warasik\WEB DATA\DS-001-master-bu"
python app.py

# Menjalankan DS-002 (Port 9002)
cd "D:\projek warasik\WEB DATA\DS-002-upah-bpjstk"
python app.py

# Menjalankan DS-003 (Port 9003)
cd "D:\projek warasik\WEB DATA\DS-003-wlkp-kemnaker"
python app.py

# Menjalankan DS-004 (Port 9004)
cd "D:\projek warasik\WEB DATA\DS-004-iuran-bpjskes"
python app.py

# Menjalankan DS-005 (Port 9005)
cd "D:\projek warasik\WEB DATA\DS-005-klaim-mcu"
python app.py

# Menjalankan DS-006 (Port 9006)
cd "D:\projek warasik\WEB DATA\DS-006-sanksi-oss-bkpm"
python app.py
```

---

## 🔗 Akses URL Dashboard & API

Setelah dijalankan, buka browser Anda pada alamat berikut:

1. **DS-001 (Master Badan Usaha)**:
   - Portal Web: [http://localhost:9001/](http://localhost:9001/)
   - Swagger Docs: [http://localhost:9001/docs](http://localhost:9001/docs)
   - REST API: [http://localhost:9001/api/v1/employers](http://localhost:9001/api/v1/employers)

2. **DS-002 (Upah SIPP BPJS TK)**:
   - Portal Web: [http://localhost:9002/](http://localhost:9002/)
   - Swagger Docs: [http://localhost:9002/docs](http://localhost:9002/docs)
   - REST API: [http://localhost:9002/api/v1/wages](http://localhost:9002/api/v1/wages)
   - Export CSV: [http://localhost:9002/api/v1/wages/export/csv](http://localhost:9002/api/v1/wages/export/csv)

3. **DS-003 (WLKP SIAPkerja Kemnaker)**:
   - Portal Web: [http://localhost:9003/](http://localhost:9003/)
   - Swagger Docs: [http://localhost:9003/docs](http://localhost:9003/docs)
   - REST API: [http://localhost:9003/api/v1/wlkp/reports](http://localhost:9003/api/v1/wlkp/reports)
   - Rekap Agregat: [http://localhost:9003/api/v1/wlkp/summary](http://localhost:9003/api/v1/wlkp/summary)

4. **DS-004 (Iuran & Piutang BPJS Kesehatan)**:
   - Portal Web: [http://localhost:9004/](http://localhost:9004/)
   - Swagger Docs: [http://localhost:9004/docs](http://localhost:9004/docs)
   - REST API: [http://localhost:9004/api/v1/billing](http://localhost:9004/api/v1/billing)
   - Daftar Tunggakan: [http://localhost:9004/api/v1/billing/arrears](http://localhost:9004/api/v1/billing/arrears)

5. **DS-005 (Klaim Medis & MCU Healthkathon)**:
   - Portal Web: [http://localhost:9005/](http://localhost:9005/)
   - Swagger Docs: [http://localhost:9005/docs](http://localhost:9005/docs)
   - REST API: [http://localhost:9005/api/v1/claims](http://localhost:9005/api/v1/claims)
   - Perusahaan Tertentu: [http://localhost:9005/api/v1/claims/company/BU-001](http://localhost:9005/api/v1/claims/company/BU-001)

6. **DS-006 (Sanksi TMP2T BKPM OSS)**:
   - Portal Web: [http://localhost:9006/](http://localhost:9006/)
   - Swagger Docs: [http://localhost:9006/docs](http://localhost:9006/docs)
   - REST API: [http://localhost:9006/api/v1/sanctions](http://localhost:9006/api/v1/sanctions)
   - Badan Usaha TMP2T Aktif: [http://localhost:9006/api/v1/sanctions/tmp2t/active](http://localhost:9006/api/v1/sanctions/tmp2t/active)

---

## 🤖 Integrasi dengan WasrikAgent AI 2.0

WasrikAgent AI dapat melakukan *federated pull ingestion* secara real-time melalui agent tool / function calling:

```python
import httpx

# 1. Menarik data upah resmi dari SIPP BPJS TK (Port 9002)
sipp_data = httpx.get("http://localhost:9002/api/v1/wages/BU-001").json()
upah_sipp = sipp_data["data"]["average_reported_wage"]

# 2. Menarik data upah & pekerja riil dari WLKP Kemnaker (Port 9003)
wlkp_data = httpx.get("http://localhost:9003/api/v1/wlkp/reports/BU-001").json()
upah_riil = wlkp_data["data"]["payroll_aggregates"]["average_real_wage"]
pekerja_riil = wlkp_data["data"]["workforce_composition"]["total_active_workers"]

# 3. Menghitung gap kepatuhan & risiko kerugian JKN
selisih_upah = upah_riil - upah_sipp
gap_pekerja = pekerja_riil - sipp_data["data"]["total_reported_workers"]

print(f"Potensi Selisih Upah: Rp {selisih_upah:,} | Selisih PDUK: {gap_pekerja} Pekerja")
```
