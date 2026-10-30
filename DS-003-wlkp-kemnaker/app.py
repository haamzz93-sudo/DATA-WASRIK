"""
app.py - DS-003: Data WLKP (Kementerian Ketenagakerjaan RI)
Port: 9003
Agency: Kemnaker RI (SIAPkerja / Ditjen Binwasnaker & K3)
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
    title="DS-003: SIAPkerja WLKP",
    description="Portal & API Wajib Lapor Ketenagakerjaan Perusahaan Kemnaker RI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/wlkp/reports")
def get_wlkp_reports(
    nib: str = Query(None, description="Filter berdasarkan NIB"),
    company_id: str = Query(None, description="Filter ID Perusahaan")
):
    results = RAW_DATA["records"]
    if nib:
        results = [r for r in results if r["nib"] == nib]
    if company_id:
        results = [r for r in results if r["company_id"].lower() == company_id.lower()]

    return {
        "status": "success",
        "dataset_id": "DS-003",
        "agency": RAW_DATA["agency"],
        "reporting_period": RAW_DATA["reporting_period"],
        "total_records": len(results),
        "data": results
    }

@app.get("/api/v1/wlkp/reports/{identifier}")
def get_wlkp_report_by_id(identifier: str):
    for r in RAW_DATA["records"]:
        if r["company_id"].lower() == identifier.lower() or r["nib"] == identifier:
            return {"status": "success", "data": r}
    raise HTTPException(status_code=404, detail=f"Laporan WLKP untuk '{identifier}' tidak ditemukan.")

@app.get("/", response_class=HTMLResponse)
def index_portal():
    cards_html = ""
    for r in RAW_DATA["records"]:
        w = r["workforce_composition"]
        p = r["payroll_aggregates"]
        cards_html += f"""
        <div class="border border-neutral-300 p-4 hover:border-black transition">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-neutral-200 pb-3">
                <div>
                    <span class="text-xs font-mono font-bold bg-neutral-100 px-2 py-0.5 border border-neutral-300">{r['company_id']}</span>
                    <span class="text-xs font-mono text-neutral-500 ml-2">No. WLKP: {r['wlkp_registration_no']}</span>
                    <h3 class="text-base font-bold text-black mt-1">{r['company_name']}</h3>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-xs font-mono font-bold px-2 py-1 bg-black text-white">Upah Riil: Rp {p['average_real_wage']:,}</span>
                    <a href="/api/v1/wlkp/reports/{r['nib']}" target="_blank" class="text-xs font-mono px-2 py-1 border border-neutral-300 hover:bg-neutral-100">JSON &rarr;</a>
                </div>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 text-xs">
                <div>
                    <span class="text-neutral-500 block">Total Pekerja Riil</span>
                    <span class="font-mono font-bold text-neutral-900">{w['total_active_workers']} Jiwa ({w['pkwtt_permanent']} Tetap, {w['pkwt_contract']} Kontrak)</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Total Payroll Bulanan</span>
                    <span class="font-mono text-neutral-900">Rp {p['monthly_total_payroll']:,}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">K3 Certification</span>
                    <span class="font-mono text-neutral-900">{'Certified' if r['occupational_safety_k3']['p2k3_certified'] else 'Pending'}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Tgl Lapor WLKP</span>
                    <span class="font-mono text-neutral-900">{r['last_reported_date']}</span>
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
    <title>DS-003 | WLKP SIAPkerja Kemnaker RI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}</style>
</head>
<body class="bg-white text-neutral-900 min-h-screen">
    <header class="border-b border-neutral-300 bg-white sticky top-0 z-30">
        <div class="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
                <span class="text-xs font-mono font-bold px-2 py-1 bg-black text-white">DS-003</span>
                <div>
                    <h1 class="text-sm sm:text-base font-bold tracking-tight text-black">Wajib Lapor Ketenagakerjaan (WLKP SIAPkerja)</h1>
                    <p class="text-[11px] text-neutral-500">Kementerian Ketenagakerjaan RI &bull; Port 9003</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <a href="/api/v1/wlkp/reports" target="_blank" class="text-xs px-3 py-1.5 bg-black text-white font-mono hover:bg-neutral-800">REST API &rarr;</a>
            </div>
        </div>
    </header>

    <main class="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 border border-neutral-300 p-4 bg-neutral-50">
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Total Terdaftar</span>
                <span class="text-xl font-bold font-mono text-black">6 Perusahaan</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Pekerja Riil</span>
                <span class="text-xl font-bold font-mono text-black">1,200 Jiwa</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Komposisi Kontrak</span>
                <span class="text-xl font-bold font-mono text-black">295 PKWT</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Tujuan Wasrik</span>
                <span class="text-xl font-bold font-mono text-black">Audit Selisih PDUK</span>
            </div>
        </div>

        <div class="flex items-center justify-between border-b border-black pb-2">
            <h2 class="text-sm font-bold uppercase tracking-wider font-mono">Data Agregat WLKP Kemnaker</h2>
            <span class="text-xs font-mono text-neutral-500">Port: 9003</span>
        </div>

        <div class="space-y-3">
            {cards_html}
        </div>
    </main>
</body>
</html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9003)
