"""
app.py - DS-004: Data Iuran & Piutang (BPJS Kesehatan)
Port: 9004
Agency: BPJS Kesehatan (Kedeputian Bidang Keuangan & Penagihan)
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
    title="DS-004: BPJS Kesehatan Billing & Arrears",
    description="Portal & API Billing, Penagihan Iuran & Piutang Badan Usaha",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/billing")
def get_billing_data(
    has_arrears: bool = Query(None, description="Filter perusahaan yang memiliki tunggakan iuran"),
    nib: str = Query(None, description="Filter NIB")
):
    results = RAW_DATA["records"]
    if has_arrears is not None:
        if has_arrears:
            results = [r for r in results if r["arrears_months"] > 0]
        else:
            results = [r for r in results if r["arrears_months"] == 0]
    if nib:
        results = [r for r in results if r["nib"] == nib]

    return {
        "status": "success",
        "dataset_id": "DS-004",
        "agency": RAW_DATA["agency"],
        "ledger_date": RAW_DATA["ledger_date"],
        "total_records": len(results),
        "data": results
    }

@app.get("/api/v1/billing/arrears")
def get_arrears():
    results = [r for r in RAW_DATA["records"] if r["arrears_months"] > 0]
    total_arrears = sum(r["arrears_principal"] + r["late_fee_fine"] for r in results)
    return {
        "status": "success",
        "count_delinquent_companies": len(results),
        "total_arrears_plus_fines": total_arrears,
        "delinquent_records": results
    }

@app.get("/api/v1/billing/{identifier}")
def get_billing_by_id(identifier: str):
    for r in RAW_DATA["records"]:
        if r["company_id"].lower() == identifier.lower() or r["nib"] == identifier or r["virtual_account"] == identifier:
            return {"status": "success", "data": r}
    raise HTTPException(status_code=404, detail=f"Billing record untuk '{identifier}' tidak ditemukan.")

@app.get("/", response_class=HTMLResponse)
def index_portal():
    cards_html = ""
    for r in RAW_DATA["records"]:
        is_tunggak = r["arrears_months"] > 0
        status_badge = "bg-black text-white" if is_tunggak else "border border-neutral-300 text-neutral-800"
        cards_html += f"""
        <div class="border border-neutral-300 p-4 hover:border-black transition">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-neutral-200 pb-3">
                <div>
                    <span class="text-xs font-mono font-bold bg-neutral-100 px-2 py-0.5 border border-neutral-300">{r['company_id']}</span>
                    <span class="text-xs font-mono text-neutral-500 ml-2">VA: {r['virtual_account']}</span>
                    <h3 class="text-base font-bold text-black mt-1">{r['company_name']}</h3>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-xs font-mono px-2 py-1 {status_badge}">{r['billing_status']}</span>
                    <a href="/api/v1/billing/{r['company_id']}" target="_blank" class="text-xs font-mono px-2 py-1 border border-neutral-300 hover:bg-neutral-100">JSON &rarr;</a>
                </div>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 text-xs">
                <div>
                    <span class="text-neutral-500 block">Tagihan Iuran Bulanan</span>
                    <span class="font-mono font-bold text-neutral-900">Rp {r['monthly_billed_amount']:,}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Tunggakan Pokok</span>
                    <span class="font-mono font-bold text-neutral-900">{'Rp ' + f"{r['arrears_principal']:,}" if is_tunggak else 'Rp 0 (Nihil)'}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Denda Keterlambatan</span>
                    <span class="font-mono text-neutral-900">Rp {r['late_fee_fine']:,}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Pembayaran Terakhir</span>
                    <span class="font-mono text-neutral-900">{r['last_payment_date']}</span>
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
    <title>DS-004 | Iuran &amp; Piutang BPJS Kesehatan</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}</style>
</head>
<body class="bg-white text-neutral-900 min-h-screen">
    <header class="border-b border-neutral-300 bg-white sticky top-0 z-30">
        <div class="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
                <span class="text-xs font-mono font-bold px-2 py-1 bg-black text-white">DS-004</span>
                <div>
                    <h1 class="text-sm sm:text-base font-bold tracking-tight text-black">Portal Iuran, Penagihan &amp; Piutang</h1>
                    <p class="text-[11px] text-neutral-500">BPJS Kesehatan Kedeputian Keuangan &bull; Port 9004</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <a href="/api/v1/billing/arrears" target="_blank" class="text-xs px-3 py-1.5 border border-neutral-300 hover:border-black font-mono">Daftar Tunggakan</a>
                <a href="/api/v1/billing" target="_blank" class="text-xs px-3 py-1.5 bg-black text-white font-mono hover:bg-neutral-800">REST API &rarr;</a>
            </div>
        </div>
    </header>

    <main class="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 border border-neutral-300 p-4 bg-neutral-50">
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Total Entitas</span>
                <span class="text-xl font-bold font-mono text-black">6 Entitas</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Tunggakan Pokok</span>
                <span class="text-xl font-bold font-mono text-black">Rp 126.96 M</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Badan Usaha Menunggak</span>
                <span class="text-xl font-bold font-mono text-black">2 Entitas</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Ledger Date</span>
                <span class="text-xl font-bold font-mono text-black">{RAW_DATA['ledger_date']}</span>
            </div>
        </div>

        <div class="flex items-center justify-between border-b border-black pb-2">
            <h2 class="text-sm font-bold uppercase tracking-wider font-mono">Buku Piutang &amp; Histori Pembayaran Iuran</h2>
            <span class="text-xs font-mono text-neutral-500">Port: 9004</span>
        </div>

        <div class="space-y-3">
            {cards_html}
        </div>
    </main>
</body>
</html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9004)
