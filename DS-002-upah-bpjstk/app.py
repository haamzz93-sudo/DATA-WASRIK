"""
app.py - DS-002: Data Upah Terlaporkan (BPJS Ketenagakerjaan / SIPP)
Port: 9002
Agency: BPJS Ketenagakerjaan (Sistem Informasi Pelaporan Peserta)
Theme: Clean Monochrome (Hitam-Putih, Anti-AI Slop, 100% Responsive)
"""

import os
import io
import csv
import json
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "data.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    RAW_DATA = json.load(f)

app = FastAPI(
    title="DS-002: SIPP Upah Terlaporkan",
    description="Portal & API Data Upah Terlaporkan BPJS Ketenagakerjaan",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/wages")
def get_wages(
    company_id: str = Query(None, description="Filter ID Badan Usaha"),
    nib: str = Query(None, description="Filter NIB")
):
    results = RAW_DATA["records"]
    if company_id:
        results = [r for r in results if r["company_id"].lower() == company_id.lower()]
    if nib:
        results = [r for r in results if r["nib"] == nib]
    
    return {
        "status": "success",
        "dataset_id": "DS-002",
        "agency": RAW_DATA["agency"],
        "pdp_sanitization": RAW_DATA["pdp_sanitization"],
        "total_records": len(results),
        "data": results
    }

@app.get("/api/v1/wages/{identifier}")
def get_wage_by_id(identifier: str):
    for r in RAW_DATA["records"]:
        if r["company_id"].lower() == identifier.lower() or r["nib"] == identifier:
            return {"status": "success", "data": r}
    raise HTTPException(status_code=404, detail=f"Data upah untuk '{identifier}' tidak ditemukan.")

@app.get("/api/v1/wages/export/csv")
def export_wages_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "company_id", "nib", "company_name", "period", "average_reported_wage",
        "total_reported_workers", "worker_masked", "nik_salted_sha256", "reported_total_wage"
    ])
    for r in RAW_DATA["records"]:
        w = r["reported_sample_worker"]
        writer.writerow([
            r["company_id"], r["nib"], r["company_name"], w["period"],
            r["average_reported_wage"], r["total_reported_workers"],
            w["worker_name_masked"], w["nik_salted_sha256"], w["reported_total_wage"]
        ])
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sipp_wages_export.csv"}
    )

@app.get("/", response_class=HTMLResponse)
def index_portal():
    cards_html = ""
    for r in RAW_DATA["records"]:
        w = r["reported_sample_worker"]
        cards_html += f"""
        <div class="border border-neutral-300 p-4 hover:border-black transition">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-neutral-200 pb-3">
                <div>
                    <span class="text-xs font-mono font-bold bg-neutral-100 px-2 py-0.5 border border-neutral-300">{r['company_id']}</span>
                    <span class="text-xs font-mono text-neutral-500 ml-2">NIB: {r['nib']}</span>
                    <h3 class="text-base font-bold text-black mt-1">{r['company_name']}</h3>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-xs font-mono font-bold px-2 py-1 bg-black text-white">Rp {r['average_reported_wage']:,} / bln</span>
                    <a href="/api/v1/wages/{r['company_id']}" target="_blank" class="text-xs font-mono px-2 py-1 border border-neutral-300 hover:bg-neutral-100">JSON &rarr;</a>
                </div>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 text-xs">
                <div>
                    <span class="text-neutral-500 block">Pekerja SIPP</span>
                    <span class="font-mono font-bold text-neutral-900">{r['total_reported_workers']} Jiwa</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Tgl Pengajuan</span>
                    <span class="font-mono text-neutral-900">{r['submission_date']}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Sample Worker (Masked)</span>
                    <span class="font-mono text-neutral-900">{w['worker_name_masked']} ({w['job_title']})</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Salted NIK Hash</span>
                    <span class="font-mono text-[10px] text-neutral-600 truncate block" title="{w['nik_salted_sha256']}">{w['nik_salted_sha256'][:16]}...</span>
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
    <title>DS-002 | SIPP BPJS Ketenagakerjaan</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}</style>
</head>
<body class="bg-white text-neutral-900 min-h-screen">
    <header class="border-b border-neutral-300 bg-white sticky top-0 z-30">
        <div class="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
                <span class="text-xs font-mono font-bold px-2 py-1 bg-black text-white">DS-002</span>
                <div>
                    <h1 class="text-sm sm:text-base font-bold tracking-tight text-black">Data Upah Terlaporkan (SIPP Online)</h1>
                    <p class="text-[11px] text-neutral-500">BPJS Ketenagakerjaan &bull; Port 9002</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <a href="/api/v1/wages/export/csv" target="_blank" class="text-xs px-3 py-1.5 border border-neutral-300 hover:border-black font-mono">Export CSV</a>
                <a href="/api/v1/wages" target="_blank" class="text-xs px-3 py-1.5 bg-black text-white font-mono hover:bg-neutral-800">REST API &rarr;</a>
            </div>
        </div>
    </header>

    <main class="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 border border-neutral-300 p-4 bg-neutral-50">
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Entitas Lapor</span>
                <span class="text-xl font-bold font-mono text-black">6 Perusahaan</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Format</span>
                <span class="text-xl font-bold font-mono text-black">CSV &amp; REST</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Hashing</span>
                <span class="text-xl font-bold font-mono text-black">SHA-256 Salted</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Fungsi Wasrik</span>
                <span class="text-xl font-bold font-mono text-black">Deteksi Underreporting</span>
            </div>
        </div>

        <div class="flex items-center justify-between border-b border-black pb-2">
            <h2 class="text-sm font-bold uppercase tracking-wider font-mono">Log Pelaporan Upah SIPP</h2>
            <span class="text-xs font-mono text-neutral-500">Port: 9002</span>
        </div>

        <div class="space-y-3">
            {cards_html}
        </div>
    </main>
</body>
</html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9002)
