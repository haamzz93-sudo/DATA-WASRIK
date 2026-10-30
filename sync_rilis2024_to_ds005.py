"""
sync_rilis2024_to_ds005.py
Mengekstrak sample klaim medis nyata segmen PPU (Pekerja Penerima Upah) dari file
BPJS Kesehatan Rilis 2024 (202303_fkrtl.dta) dan menyelaraskannya ke DS-005 (Port 9005).
"""

import os
import json
import pandas as pd

DTA_PATH = r"D:\projek warasik\WEB DATA\Rilis2024\Data Sampel 2015-2023\Data Sampel Reguler Edisi 2024\data\202303_fkrtl.dta"
DS005_JSON = r"D:\projek warasik\WEB DATA\DS-005-klaim-mcu\data.json"

COMPANIES = [
    {"company_id": "BU-001", "name": "PT Cipta Busana Mandiri", "sector": "Tekstil & Garmen"},
    {"company_id": "BU-002", "name": "PT Sumber Maju Sentosa", "sector": "Manufaktur Presisi"},
    {"company_id": "BU-003", "name": "PT Indo Mandiri Perkasa", "sector": "Industri Kimia Dasar"},
    {"company_id": "BU-004", "name": "PT Sinar Maju Tekstil", "sector": "Tekstil & Tenun"},
    {"company_id": "BU-005", "name": "PT Delta Logistik Nusantara", "sector": "Transportasi & Pergudangan"},
    {"company_id": "BU-006", "name": "PT Global Prima Elektronik", "sector": "Perakitan Komponen Elektronik"}
]

print("Membaca data klaim FKRTL PPU dari Rilis 2024...")
reader = pd.read_stata(DTA_PATH, iterator=True)
chunk_size = 50000
ppu_records = []

# Ambil hingga 60 record klaim nyata PPU (10 klaim per badan usaha)
total_needed = 60
cols = ['PSTV01', 'FKL02', 'FKL03', 'FKL08', 'FKL10', 'FKL12', 'FKL17A', 'FKL18A', 'FKL19', 'FKL19A', 'FKL47', 'FKL48']

while len(ppu_records) < total_needed:
    try:
        chunk = reader.get_chunk(chunk_size)
    except StopIteration:
        break
    
    # Filter hanya segmen Pekerja Penerima Upah (PPU)
    ppu_chunk = chunk[chunk['FKL12'] == 'PPU'][cols]
    
    for _, row in ppu_chunk.iterrows():
        # Validasi diagnosa dan biaya terisi
        if pd.notna(row['FKL18A']) and pd.notna(row['FKL48']) and row['FKL48'] > 0:
            ppu_records.append(row)
            if len(ppu_records) >= total_needed:
                break

print(f"Berhasil mengekstrak {len(ppu_records)} record klaim nyata PPU dari dataset BPJS!")

# Bangun struktur data DS-005
formatted_records = []
for idx, r in enumerate(ppu_records):
    c_idx = idx % len(COMPANIES)
    co = COMPANIES[c_idx]
    
    claim_id = f"CLM-2023-FKRTL-{str(r['FKL02'])[-8:]}"
    cost_idr = int(r['FKL48']) if pd.notna(r['FKL48']) else 150000
    
    # Hitung perkiraan hari izin sakit berdasarkan tingkat keparahan/biaya klaim
    if cost_idr > 5000000:
        sick_days = 7
    elif cost_idr > 2000000:
        sick_days = 4
    elif cost_idr > 500000:
        sick_days = 2
    else:
        sick_days = 1
        
    formatted_records.append({
        "claim_id": claim_id,
        "company_id": co["company_id"],
        "company_name": co["name"],
        "patient_pseudo_id": f"PX-PPU-{str(r['PSTV01'])[-6:]}",
        "claim_date": str(r['FKL03'])[:10],
        "faskes_code": f"FKRTL-{str(r['FKL02'])[:4]}",
        "faskes_name": f"RS Rekanan BPJS ({r['FKL08'] if pd.notna(r['FKL08']) else 'RS Swasta'})",
        "service_level": "FKRTL",
        "icd10_code": str(r['FKL17A']),
        "diagnosis_name": str(r['FKL18A']),
        "ina_cbg_code": str(r['FKL19']),
        "ina_cbg_desc": str(r['FKL19A']),
        "provider_billed_cost": int(r['FKL47']) if pd.notna(r['FKL47']) else cost_idr,
        "claim_cost_idr": cost_idr,
        "sick_leave_days": sick_days,
        "raw_source": "BPJS Kesehatan Rilis 2024 (Data Sampel Reguler 202303_fkrtl.dta)",
        "status": "APPROVED"
    })

dataset_payload = {
    "dataset_id": "DS-005",
    "dataset_name": "Data Klaim Medis, MCU & Utilisasi Faskes (Real BPJS Kesehatan Rilis 2024)",
    "agency": "BPJS Kesehatan (Direktorat Jaminan Pelayanan Kesehatan)",
    "protocol": "Data Sampel Resmi BPJS / REST API JSON",
    "update_frequency": "Longitudinal Tahunan (Data Sampel 2015-2023 Edisi 2024)",
    "pdp_sanitization": "De-identified Patient & Pseudo-ID PPU (UU Kesehatan No. 17/2023 & UU PDP No. 27/2022)",
    "batch_version": "BPJS-RILIS-2024-REGULER",
    "total_records": len(formatted_records),
    "records": formatted_records
}

with open(DS005_JSON, "w", encoding="utf-8") as f:
    json.dump(dataset_payload, f, indent=2)

print(f"Berhasil memperbarui {DS005_JSON} dengan {len(formatted_records)} record klaim nyata!")
