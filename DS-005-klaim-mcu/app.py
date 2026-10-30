"""
app.py - DS-005: Data Klaim Medis, MCU & Utilisasi Faskes
Port: 9005
Agency: BPJS Kesehatan (Data Sampel Resmi Rilis 2024 FKRTL PPU)
Theme: Clean Monochrome (Hitam-Putih, Anti-AI Slop, 100% Responsive)
"""

import os
import json
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "data.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    RAW_DATA = json.load(f)

app = FastAPI(
    title="DS-005: BPJS Kesehatan Medical Claims",
    description="Portal & API Klaim Medis & Morbiditas Kerja JKN Edisi 2024",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/claims")
def get_claims(
    company_id: str = Query(None, description="Filter ID Badan Usaha"),
    icd10: str = Query(None, description="Filter kode ICD-10")
):
    results = RAW_DATA["records"]
    if company_id:
        results = [r for r in results if r["company_id"].lower() == company_id.lower()]
    if icd10:
        results = [r for r in results if icd10.lower() in r["icd10_code"].lower()]

    return {
        "status": "success",
        "dataset_id": "DS-005",
        "agency": RAW_DATA["agency"],
        "batch_version": RAW_DATA["batch_version"],
        "total_records": len(results),
        "data": results
    }

@app.get("/api/v1/claims/{claim_id}")
def get_claim_by_id(claim_id: str):
    for r in RAW_DATA["records"]:
        if r["claim_id"].lower() == claim_id.lower():
            return {"status": "success", "data": r}
    raise HTTPException(status_code=404, detail=f"Klaim ID '{claim_id}' tidak ditemukan.")

@app.get("/", response_class=HTMLResponse)
def index_portal():
    # Tampilkan 20 klaim pertama di portal web agar performa ringan
    cards_html = ""
    for r in RAW_DATA["records"][:20]:
        cards_html += f"""
        <div class="border border-neutral-300 p-4 hover:border-black transition">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-neutral-200 pb-3">
                <div>
                    <span class="text-xs font-mono font-bold bg-neutral-100 px-2 py-0.5 border border-neutral-300">{r['claim_id']}</span>
                    <span class="text-xs font-mono text-neutral-500 ml-2">Tgl Klaim: {r['claim_date']}</span>
                    <h3 class="text-base font-bold text-black mt-1">{r['company_name']} ({r['company_id']})</h3>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-xs font-mono font-bold px-2 py-1 bg-black text-white">Biaya: Rp {r['claim_cost_idr']:,}</span>
                    <a href="/api/v1/claims/{r['claim_id']}" target="_blank" class="text-xs font-mono px-2 py-1 border border-neutral-300 hover:bg-neutral-100">JSON &rarr;</a>
                </div>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 text-xs">
                <div>
                    <span class="text-neutral-500 block">Diagnosa ICD-10</span>
                    <span class="font-mono font-bold text-neutral-900">{r['icd10_code']}</span>
                    <span class="text-neutral-600 block truncate" title="{r['diagnosis_name']}">{r['diagnosis_name']}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">INA-CBGs</span>
                    <span class="font-mono font-bold text-neutral-900">{r['ina_cbg_code']}</span>
                    <span class="text-neutral-600 block truncate">{r.get('ina_cbg_desc', '-')}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Tingkat Layanan</span>
                    <span class="font-mono text-neutral-900">{r['service_level']} &bull; {r['faskes_name']}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Patient Pseudo-ID</span>
                    <span class="font-mono text-neutral-900">{r['patient_pseudo_id']}</span>
                </div>
            </div>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DS-005 | Klaim Medis Real BPJS Rilis 2024</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}</style>
</head>
<body class="bg-white text-neutral-900 min-h-screen">
    <header class="border-b border-neutral-300 bg-white sticky top-0 z-30">
        <div class="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
                <span class="text-xs font-mono font-bold px-2 py-1 bg-black text-white">DS-005</span>
                <div>
                    <h1 class="text-sm sm:text-base font-bold tracking-tight text-black">Data Klaim Medis &amp; Morbiditas JKN</h1>
                    <p class="text-[11px] text-neutral-500">BPJS Kesehatan Real Data Sampel Edisi 2024 &bull; Port 9005</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <a href="/api/v1/claims" target="_blank" class="text-xs px-3 py-1.5 bg-black text-white font-mono hover:bg-neutral-800">Semua JSON (60 Data) &rarr;</a>
            </div>
        </div>
    </header>

    <main class="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 border border-neutral-300 p-4 bg-neutral-50">
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Total Klaim Real</span>
                <span class="text-xl font-bold font-mono text-black">{RAW_DATA['total_records']} Transaksi</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Dataset Sumber</span>
                <span class="text-xl font-bold font-mono text-black">Rilis 2024</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Segmen</span>
                <span class="text-xl font-bold font-mono text-black">PPU (Pekerja)</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Tarif Acuan</span>
                <span class="text-xl font-bold font-mono text-black">INA-CBGs Riil</span>
            </div>
        </div>

        <div class="flex items-center justify-between border-b border-black pb-2">
            <h2 class="text-sm font-bold uppercase tracking-wider font-mono">Transaksi Klaim Rumah Sakit (FKRTL)</h2>
            <span class="text-xs font-mono text-neutral-500">Port: 9005</span>
        </div>

        <div class="space-y-3">
            {cards_html}
        </div>
    </main>
</body>
</html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9005)
