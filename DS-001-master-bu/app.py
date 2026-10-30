"""
app.py - DS-001: Master Badan Usaha API Service
Port: 9001
Agency: BPJS Kesehatan & BPJS Ketenagakerjaan
Theme: Strict Engineering Monokrom (Tanpa Emoji, Tanpa AI Slop, Font Monospace Bersih)
"""

import os
import json
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "data.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    RAW_DATA = json.load(f)

app = FastAPI(
    title="DS-001: Master Badan Usaha JKN",
    description="Portal Registrasi & Master Data Badan Usaha JKN (BPJS Kesehatan / BPJS TK)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_employer_html(item: dict) -> str:
    is_patuh = item.get("compliance_status") == "PATUH"
    badge_class = "bg-black text-white" if is_patuh else "border border-black text-black font-bold"
    json_pretty = json.dumps({"status": "success", "data": item}, indent=2)
    nib = item.get("nib")
    
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{item.get('company_name')} | DS-001 API Detail</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }}</style>
</head>
<body class="bg-white text-neutral-900 min-h-screen">
    <header class="border-b border-neutral-300 bg-white sticky top-0 z-30">
        <div class="max-w-4xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center gap-3">
                <a href="/" class="text-xs font-bold px-2.5 py-1 bg-black text-white hover:bg-neutral-800">[&larr; PORTAL]</a>
                <span class="text-xs text-neutral-500">ENDPOINT /api/v1/employers/{nib}</span>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="copyApiUrl()" id="btn-copy-url" class="text-xs px-3 py-1 bg-black text-white hover:bg-neutral-800">
                    [SALIN API URL]
                </button>
                <button onclick="copyRawJson()" id="btn-copy-json" class="text-xs px-3 py-1 border border-neutral-300 hover:border-black">
                    [SALIN JSON]
                </button>
                <a href="?format=json" class="text-xs px-2 py-1 text-neutral-500 hover:text-black">[RAW]</a>
            </div>
        </div>
    </header>

    <main class="max-w-4xl mx-auto p-4 sm:p-6 space-y-6">
        <div class="border border-neutral-300 p-5 bg-neutral-50">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-neutral-200 pb-4">
                <div>
                    <span class="text-xs font-bold px-2 py-0.5 bg-neutral-200 border border-neutral-300">{item.get('id')}</span>
                    <span class="text-xs text-neutral-500 ml-2">NIB: {item.get('nib')}</span>
                    <h1 class="text-lg font-bold text-black mt-1 font-sans">{item.get('company_name')}</h1>
                    <p class="text-xs text-neutral-500 mt-0.5 font-sans">{item.get('address')} &bull; {item.get('branch_office')}</p>
                </div>
                <div>
                    <span class="text-xs px-3 py-1 {badge_class}">{item.get('compliance_status')}</span>
                </div>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 text-xs font-sans">
                <div>
                    <span class="text-neutral-500 block">Sektor Usaha</span>
                    <span class="font-bold text-black">{item.get('sector')}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Skala Bisnis</span>
                    <span class="font-bold text-black">{item.get('scale')}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block font-mono">Peserta BPJS</span>
                    <span class="font-mono font-bold text-black">{item.get('bpjs_registered_employees')} / {item.get('total_active_employees')}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block font-mono">Skor Kepatuhan</span>
                    <span class="font-mono font-bold text-black">{item.get('compliance_score')} / 100</span>
                </div>
            </div>
        </div>

        <div class="space-y-2">
            <div class="flex items-center justify-between">
                <span class="text-xs font-bold uppercase tracking-wider text-neutral-700">PAYLOAD RESPONSE:</span>
                <span class="text-xs text-neutral-500">CONTENT-TYPE: application/json</span>
            </div>
            <textarea id="raw-json-data" class="hidden">{json_pretty}</textarea>
            <pre class="bg-neutral-900 text-neutral-100 p-4 rounded-none text-xs overflow-x-auto leading-relaxed border border-black">{json_pretty}</pre>
        </div>
    </main>

    <script>
        function copyApiUrl() {{
            const url = window.location.origin + '/api/v1/employers/{nib}?format=json';
            navigator.clipboard.writeText(url).then(() => {{
                const btn = document.getElementById('btn-copy-url');
                const orig = btn.innerText;
                btn.innerText = '[URL TERSALIN]';
                setTimeout(() => btn.innerText = orig, 1500);
            }});
        }}
        function copyRawJson() {{
            const text = document.getElementById('raw-json-data').value;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById('btn-copy-json');
                const orig = btn.innerText;
                btn.innerText = '[JSON TERSALIN]';
                setTimeout(() => btn.innerText = orig, 1500);
            }});
        }}
    </script>
</body>
</html>"""

@app.get("/api/v1/employers")
def get_employers(
    request: Request,
    search: str = Query(None, description="Cari nama atau NIB"),
    scale: str = Query(None, description="Filter skala usaha"),
    status: str = Query(None, description="Filter status kepatuhan"),
    sandbox: bool = Query(False, description="Aktifkan sanitasi privasi"),
    format: str = Query(None, description="Paksa format: 'json' atau 'html'")
):
    results = RAW_DATA["records"]
    if search:
        s = search.lower()
        results = [r for r in results if s in r["company_name"].lower() or s in r["nib"]]
    if scale:
        results = [r for r in results if r["scale"].lower() == scale.lower()]
    if status:
        results = [r for r in results if r["compliance_status"].lower() == status.lower()]
    
    output = []
    for r in results:
        item = r.copy()
        if sandbox:
            item["company_name"] = item.pop("company_name_masked", item["company_name"])
        output.append(item)

    payload = {
        "status": "success",
        "dataset_id": "DS-001",
        "agency": "BPJS Kesehatan & BPJS Ketenagakerjaan",
        "total_records": len(output),
        "data": output
    }
    
    accept = request.headers.get("accept", "")
    if format == "html" or ("text/html" in accept and format != "json"):
        json_pretty = json.dumps(payload, indent=2)
        return HTMLResponse(f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8"><title>DS-001 API Stream Explorer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}</style>
</head>
<body class="bg-white text-neutral-900 p-6 max-w-5xl mx-auto space-y-4">
    <div class="flex items-center justify-between border-b border-black pb-3">
        <div>
            <h1 class="font-bold text-sm">DS-001: MASTER BADAN USAHA STREAM</h1>
            <p class="text-xs text-neutral-500">TOTAL: {len(output)} RECORDS</p>
        </div>
        <div class="flex gap-2">
            <button onclick="navigator.clipboard.writeText(window.location.origin + '/api/v1/employers?format=json'); this.innerText='[URL TERSALIN]'; setTimeout(()=>this.innerText='[SALIN URL]', 1500);" class="text-xs px-3 py-1 bg-black text-white">[SALIN URL]</button>
            <button onclick="navigator.clipboard.writeText(document.getElementById('raw-json').value); this.innerText='[JSON TERSALIN]'; setTimeout(()=>this.innerText='[SALIN JSON]', 1500);" class="text-xs px-3 py-1 border border-neutral-300">[SALIN JSON]</button>
        </div>
    </div>
    <textarea id="raw-json" class="hidden">{json_pretty}</textarea>
    <pre class="bg-neutral-950 text-neutral-100 p-4 text-xs overflow-x-auto leading-relaxed border border-black">{json_pretty}</pre>
</body></html>""")

    return JSONResponse(content=payload)

@app.get("/api/v1/employers/{nib}")
def get_employer_by_nib(nib: str, request: Request, sandbox: bool = Query(False), format: str = Query(None)):
    matched = None
    for r in RAW_DATA["records"]:
        if r["nib"] == nib or r["id"].lower() == nib.lower():
            matched = r.copy()
            if sandbox:
                matched["company_name"] = matched.pop("company_name_masked", matched["company_name"])
            break
            
    if not matched:
        raise HTTPException(status_code=404, detail=f"Badan Usaha dengan NIB/ID '{nib}' tidak ditemukan.")

    accept = request.headers.get("accept", "")
    if format == "html" or ("text/html" in accept and format != "json"):
        return HTMLResponse(format_employer_html(matched))

    return JSONResponse(content={"status": "success", "data": matched})

@app.get("/", response_class=HTMLResponse)
def index_portal():
    cards_html = ""
    for r in RAW_DATA["records"]:
        is_patuh = r["compliance_status"] == "PATUH"
        badge_class = "border-black bg-black text-white" if is_patuh else "border-black bg-white text-black font-bold"
        cards_html += f"""
        <div class="border border-neutral-300 p-4 rounded-none hover:border-black transition">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-neutral-200 pb-3">
                <div>
                    <span class="text-xs font-bold tracking-wider bg-neutral-100 px-2 py-0.5 border border-neutral-300">{r['id']}</span>
                    <span class="text-xs text-neutral-500 ml-2">NIB: {r['nib']}</span>
                    <h3 class="text-base font-bold text-black mt-1 font-sans">{r['company_name']}</h3>
                </div>
                <div class="flex flex-wrap items-center gap-2">
                    <span class="text-xs px-2.5 py-1 border {badge_class}">{r['compliance_status']}</span>
                    <button onclick="copyToClipboard(window.location.origin + '/api/v1/employers/{r['nib']}?format=json', this, '[SALIN API]')" class="text-xs px-2.5 py-1 bg-black text-white hover:bg-neutral-800">
                        [SALIN API]
                    </button>
                    <button onclick="fetchAndCopyJson('{r['nib']}', this)" class="text-xs px-2.5 py-1 border border-neutral-300 hover:border-black">
                        [SALIN JSON]
                    </button>
                    <a href="/api/v1/employers/{r['nib']}" target="_blank" class="text-xs px-2 py-1 text-neutral-500 hover:text-black">
                        DETAIL &rarr;
                    </a>
                </div>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 text-xs font-sans">
                <div>
                    <span class="text-neutral-500 block">Sektor Usaha</span>
                    <span class="font-medium text-neutral-900">{r['sector']}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block">Skala Usaha</span>
                    <span class="font-medium text-neutral-900">{r['scale']}</span>
                </div>
                <div>
                    <span class="text-neutral-500 block font-mono">Kepesertaan BPJS</span>
                    <span class="font-mono font-bold text-neutral-900">{r['bpjs_registered_employees']} / {r['total_active_employees']} Jiwa</span>
                </div>
                <div>
                    <span class="text-neutral-500 block font-mono">Privasi UU PDP</span>
                    <span class="font-mono text-neutral-900">Sandbox Masked</span>
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
    <title>DS-001 | Master Badan Usaha JKN</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}</style>
</head>
<body class="bg-white text-neutral-900 min-h-screen">
    <header class="border-b border-neutral-300 bg-white sticky top-0 z-30">
        <div class="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
                <span class="text-xs font-bold px-2 py-1 bg-black text-white">DS-001</span>
                <div>
                    <h1 class="text-sm sm:text-base font-bold tracking-tight text-black font-sans">Master Badan Usaha JKN</h1>
                    <p class="text-[11px] text-neutral-500">BPJS Kesehatan &amp; BPJS Ketenagakerjaan &bull; Port 9001</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="copyToClipboard(window.location.origin + '/api/v1/employers?format=json', this, '[SALIN STREAM API]')" class="text-xs px-3 py-1.5 bg-black text-white hover:bg-neutral-800">
                    [SALIN STREAM API]
                </button>
                <a href="/docs" target="_blank" class="text-xs px-3 py-1.5 border border-neutral-300 hover:border-black">/docs</a>
            </div>
        </div>
    </header>

    <main class="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 border border-neutral-300 p-4 bg-neutral-50">
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase">TOTAL ENTITAS</span>
                <span class="text-lg font-bold text-black">6 BADAN USAHA</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase">INTEGRASI</span>
                <span class="text-lg font-bold text-black">DIRECT COPY</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase">OUTPUT</span>
                <span class="text-lg font-bold text-black">REAL JSON SYNC</span>
            </div>
            <div>
                <span class="text-[11px] text-neutral-500 block uppercase">REGULASI</span>
                <span class="text-lg font-bold text-black">UU PDP 27/22</span>
            </div>
        </div>

        <div class="flex items-center justify-between border-b border-black pb-2">
            <h2 class="text-xs font-bold uppercase tracking-wider">DAFTAR BADAN USAHA TERDAFTAR (MASTER JKN)</h2>
            <span class="text-xs text-neutral-500">PORT: 9001</span>
        </div>

        <div class="space-y-3">
            {cards_html}
        </div>

        <footer class="pt-6 border-t border-neutral-200 text-xs text-neutral-500 flex flex-col sm:flex-row justify-between gap-2">
            <span>WasrikAgent AI 2.0 &bull; Data Integration Service</span>
            <span>REST API Live Service</span>
        </footer>
    </main>

    <script>
        function copyToClipboard(text, btnElement, label) {{
            navigator.clipboard.writeText(text).then(() => {{
                btnElement.innerText = '[TERSELESAIKAN]';
                setTimeout(() => btnElement.innerText = label, 1500);
            }});
        }}

        function fetchAndCopyJson(nib, btnElement) {{
            fetch('/api/v1/employers/' + nib + '?format=json')
                .then(r => r.json())
                .then(data => {{
                    navigator.clipboard.writeText(JSON.stringify(data, null, 2)).then(() => {{
                        btnElement.innerText = '[JSON TERSALIN]';
                        setTimeout(() => btnElement.innerText = '[SALIN JSON]', 1500);
                    }});
                }})
                .catch(e => alert('Gagal menarik JSON: ' + e));
        }}
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9001)
