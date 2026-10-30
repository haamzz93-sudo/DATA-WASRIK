import json

data_path = r"D:\projek warasik\WEB DATA\DS-005-klaim-mcu\data.json"
with open(data_path, "r", encoding="utf-8") as f:
    d = json.load(f)

print("=" * 70)
print(f"STATUS DATA MENTAH HACKATHON RILIS 2024 DI DS-005")
print("=" * 70)
print(f"Total Record Klaim Terintegrasi : {d['total_records']} Klaim")
print(f"Batch Dataset Resmi             : {d['batch_version']}")
print(f"Agency Penerbit                 : {d['agency']}")
print("=" * 70)
print("SAMPEL 5 KLAIM RUMAH SAKIT (FKRTL) NYATA HASIL EKSTRAKSI:")
for i, r in enumerate(d['records'][:5]):
    print(f"\n[{i+1}] ID Klaim : {r['claim_id']}")
    print(f"    Perusahaan   : {r['company_name']} ({r['company_id']})")
    print(f"    Diagnosa ICD : {r['icd10_code']} - {r['diagnosis_name']}")
    print(f"    Tarif INACBG : {r['ina_cbg_code']} ({r.get('ina_cbg_desc', '-')})")
    print(f"    Biaya Klaim  : Rp {r['claim_cost_idr']:,}")
    print(f"    Sumber Asli  : {r['raw_source']}")
print("=" * 70)
