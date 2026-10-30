"""
app.py - DS-006: Master Sanksi TMP2T (PTSP / BKPM OSS)
Port: 9006
Agency: BKPM (OSS) & BPJS Kesehatan
Theme: Clean Monochrome (Hitam-Putih, Anti-AI Slop, 100% Responsive)
"""

import os
import json
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "data.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    RAW_DATA = json.load(f)

app = FastAPI(
    title="DS-006: OSS BKPM Sanksi TMP2T",
    description="Portal Penegakan Sanksi Administratif PP 86/2013 Terintegrasi OSS BKPM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IssueSanctionRequest(BaseModel):
    company_id: str
    nib: str
    sanction_level: str
    violation_type: str
    issuing_authority: str
    restricted_services: Optional[List[str]] = []

@app.get("/api/v1/sanctions")
def get_sanctions(
    nib: str = Query(None, description="Filter berdasarkan NIB"),
    has_active_sanction: bool = Query(None, description="Filter apakah ada sanksi aktif")
):
    results = RAW_DATA["records"]
    if nib:
        results = [r for r in results if r["nib"] == nib]
    if has_active_sanction is not None:
        if has_active_sanction:
            results = [r for r in results if r["active_sanction"] is not None]
        else:
            results = [r for r in results if r["active_sanction"] is None]

    return {
        "status": "success",
        "dataset_id": "DS-006",
        "agency": RAW_DATA["agency"],
        "legal_basis": RAW_DATA["legal_basis"],
        "total_records": len(results),
        "data": results
    }

@app.get("/api/v1/sanctions/{identifier}")
def get_sanction_by_id(identifier: str):
    for r in RAW_DATA["records"]:
        if r["company_id"].lower() == identifier.lower() or r["nib"] == identifier:
            return {"status": "success", "data": r}
    raise HTTPException(status_code=404, detail=f"Sanksi untuk '{identifier}' tidak ditemukan.")

@app.post("/api/v1/sanctions/issue")
def issue_sanction(req: IssueSanctionRequest):
    for r in RAW_DATA["records"]:
        if r["company_id"].lower() == req.company_id.lower() or r["nib"] == req.nib:
            r["sanction_status"] = f"AKTIF_{req.sanction_level}"
            r["sanction_level"] = req.sanction_level
            r["active_sanction"] = {
                "decree_number": f"SK-WASRIK/2026/PP86/{req.company_id}",
                "issued_date": "2026-10-30",
                "grace_period_days": 30 if "TEGURAN" in req.sanction_level else 0,
                "due_date": "2026-11-29" if "TEGURAN" in req.sanction_level else "Immediate Block",
                "issuing_authority": req.issuing_authority,
                "violation_type": req.violation_type,
                "restricted_services": req.restricted_services,
                "oss_status": "BLOCKED_SERVICE_ACCESS" if req.sanction_level == "TMP2T" else "MONITORING_FLAG"
            }
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(RAW_DATA, f, indent=2)
            return {"status": "success", "data": r}
    raise HTTPException(status_code=404, detail=f"Perusahaan '{req.company_id}' tidak ditemukan.")

@app.get("/", response_class=HTMLResponse)
def index_portal():
    cards_html = ""
    for r in RAW_DATA["records"]:
        s = r["active_sanction"]
        status_badge = "bg-black text-white" if s else "border border-neutral-300 text-neutral-800"
        
        detail_text = ""
        if s:
            detail_text = f"<span class='text-black font-bold'>{s['decree_number']}</span> &bull; {s['violation_type']} (Batas: {s['due_date']})"
        else:
            detail_text = "<span class='text-neutral-500'>Bebas Sanksi / Tertib Administrasi</span>"

        cards_html += f"""
        <div class="border border-neutral-300 p-4 hover:border-black transition">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-neutral-200 pb-3">
                <div>
                    <span class="text-xs font-mono font-bold bg-neutral-100 px-2 py-0.5 border border-neutral-300">{r['company_id']}</span>
                    <span class="text-xs font-mono text-neutral-500 ml-2">NIB: {r['nib']}</span>
                    <h3 class="text-base font-bold text-black mt-1">{r['company_name']}</h3>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-xs font-mono px-2 py-1 {status_badge}">{r['sanction_status']}</span>
                    <a href="/api/v1/sanctions/{r['nib']}" target="_blank" class="text-xs font-mono px-2 py-1 border border-neutral-300 hover:bg-neutral-100">JSON &rarr;</a>
                </div>
            </div>
            <div class="pt-3 text-xs">
                <span class="text-neutral-500 block">Status Putusan &amp; Pelanggaran</span>
                <p class="font-mono mt-0.5">{detail_text}</p>
                <p class="text-neutral-500 mt-1">Rekomendasi Hukum: {r['legal_recommendation']}</p>
            </div>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DS-006 | Portal Sanksi TMP2T PP 86/2013</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}</style>
</head>
<body class="bg-white text-neutral-900 min-h-screen">
    <header class="border-b border-neutral-300 bg-white sticky top-0 z-30">
        <div class="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
                <span class="text-xs font-mono font-bold px-2 py-1 bg-black text-white">DS-006</span>
                <div>
                    <h1 class="text-sm sm:text-base font-bold tracking-tight text-black">Portal Sanksi TMP2T PP 86/2013</h1>
                    <p class="text-[11px] text-neutral-500">BKPM OSS &amp; DPMPTSP &bull; Port 9006</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <a href="/api/v1/sanctions" target="_blank" class="text-xs px-3 py-1.5 bg-black text-white font-mono hover:bg-neutral-800">REST API &rarr;</a>
            </div>
        </div>
    </header>

    <main class="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 border border-neutral-300 p-4 bg-neutral-50">
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Dasar Hukum</span>
                <span class="text-xl font-bold font-mono text-black">PP 86 / 2013</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Blokir OSS Aktif</span>
                <span class="text-xl font-bold font-mono text-black">1 BU (BU-006)</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Teguran I</span>
                <span class="text-xl font-bold font-mono text-black">1 BU (BU-002)</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase font-mono">Integrasi API</span>
                <span class="text-xl font-bold font-mono text-black">Webhooks Ready</span>
            </div>
        </div>

        <div class="flex items-center justify-between border-b border-black pb-2">
            <h2 class="text-sm font-bold uppercase tracking-wider font-mono">Registrasi Penegakan Sanksi Administratif</h2>
            <span class="text-xs font-mono text-neutral-500">Port: 9006</span>
        </div>

        <div class="space-y-3">
            {cards_html}
        </div>
    </main>
</body>
</html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9006)
