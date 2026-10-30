"""
run_all.py - Master Orchestrator for 6 External Data Services (DS-001 s/d DS-006)
Project: WasrikAgent AI 2.0 (BPJS Kesehatan Healthkathon 2026)

Menjalankan 6 web service independen pada background subprocess:
- DS-001: Master Badan Usaha (BPJS Kesehatan/TK)           -> http://localhost:9001
- DS-002: Upah Terlaporkan SIPP (BPJS Ketenagakerjaan)    -> http://localhost:9002
- DS-003: WLKP SIAPkerja (Kemnaker RI)                    -> http://localhost:9003
- DS-004: Iuran & Piutang (BPJS Kesehatan)                -> http://localhost:9004
- DS-005: Klaim Medis & MCU (BPJS Kesehatan HK2026)       -> http://localhost:9005
- DS-006: Sanksi TMP2T (BKPM OSS & PTSP)                  -> http://localhost:9006

Penggunaan:
  python run_all.py start   # Menjalankan ke-6 service
  python run_all.py stop    # Menghentikan ke-6 service
  python run_all.py status  # Mengecek status port ke-6 service
"""

import sys
import os
import time
import subprocess
import socket
import urllib.request
import signal

SERVICES = [
    {
        "id": "DS-001",
        "name": "Master Badan Usaha (BPJS Kesehatan/TK)",
        "dir": "DS-001-master-bu",
        "port": 9001,
        "endpoint": "/api/v1/employers"
    },
    {
        "id": "DS-002",
        "name": "Data Upah Terlaporkan (BPJS Ketenagakerjaan)",
        "dir": "DS-002-upah-bpjstk",
        "port": 9002,
        "endpoint": "/api/v1/wages"
    },
    {
        "id": "DS-003",
        "name": "Data WLKP (SIAPkerja Kemnaker RI)",
        "dir": "DS-003-wlkp-kemnaker",
        "port": 9003,
        "endpoint": "/api/v1/wlkp/reports"
    },
    {
        "id": "DS-004",
        "name": "Data Iuran & Piutang (BPJS Kesehatan)",
        "dir": "DS-004-iuran-bpjskes",
        "port": 9004,
        "endpoint": "/api/v1/billing"
    },
    {
        "id": "DS-005",
        "name": "Data Klaim Medis & MCU (BPJS Kesehatan Healthkathon)",
        "dir": "DS-005-klaim-mcu",
        "port": 9005,
        "endpoint": "/api/v1/claims"
    },
    {
        "id": "DS-006",
        "name": "Master Sanksi TMP2T (PTSP / BKPM OSS)",
        "dir": "DS-006-sanksi-oss-bkpm",
        "port": 9006,
        "endpoint": "/api/v1/sanctions"
    }
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

def check_status():
    print("=" * 70)
    print("  STATUS 6 STANDALONE EXTERNAL SERVICES (WASRIK AI 2.0 DATA LAKE)")
    print("=" * 70)
    for svc in SERVICES:
        in_use = is_port_in_use(svc["port"])
        status_text = "[ONLINE]" if in_use else "[OFFLINE]"
        color_flag = "OK" if in_use else "FAIL"
        print(f"[{color_flag:4s}] {svc['id']} | Port {svc['port']} | {status_text:9s} | {svc['name']}")
        if in_use:
            print(f"       -> Portal: http://localhost:{svc['port']}/")
            print(f"       -> API:    http://localhost:{svc['port']}{svc['endpoint']}")
    print("=" * 70)

def start_all():
    print("=" * 70)
    print("  MEMULAI 6 STANDALONE DATA SERVICES")
    print("=" * 70)
    processes = []
    
    for svc in SERVICES:
        port = svc["port"]
        if is_port_in_use(port):
            print(f"[ALREADY RUNNING] {svc['id']} pada port {port}")
            continue
        
        script_path = os.path.join(BASE_DIR, svc["dir"], "app.py")
        print(f"[STARTING] {svc['id']} ({svc['name']}) -> Port {port}...")
        
        # Spawn detached background process on Windows
        flags = 0
        if sys.platform == "win32":
            flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        
        p = subprocess.Popen(
            [sys.executable, script_path],
            cwd=os.path.join(BASE_DIR, svc["dir"]),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags
        )
        processes.append((svc, p))

    # Tunggu sebentar untuk warm-up
    time.sleep(2)
    print("\nVerifikasi status setelah inisialisasi:")
    check_status()

def stop_all():
    print("=" * 70)
    print("  MENGHENTIKAN 6 STANDALONE DATA SERVICES")
    print("=" * 70)
    import subprocess
    # Kill process listening on ports 9001..9006 on Windows
    for port in range(9001, 9007):
        try:
            cmd = f'powershell -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess"'
            res = subprocess.check_output(cmd, shell=True).decode().strip()
            if res:
                pids = set(res.split())
                for pid in pids:
                    print(f"[KILLING] Port {port} (PID: {pid})...")
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            pass
    print("Semua service pada port 9001 - 9006 telah dihentikan.")

def serve_all():
    print("=" * 70)
    print("  MENJALANKAN 6 STANDALONE DATA SERVICES (FOREGROUND RUNNER)")
    print("=" * 70)
    processes = []
    try:
        for svc in SERVICES:
            port = svc["port"]
            script_path = os.path.join(BASE_DIR, svc["dir"], "app.py")
            print(f"[LAUNCH] {svc['id']} ({svc['name']}) -> Port {port}...")
            p = subprocess.Popen(
                [sys.executable, script_path],
                cwd=os.path.join(BASE_DIR, svc["dir"])
            )
            processes.append((svc, p))

        time.sleep(2)
        print("\nSemua 6 service aktif! Tekan Ctrl+C untuk menghentikan.")
        check_status()
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMenerima sinyal berhenti (Ctrl+C). Mematikan semua service...")
    finally:
        for svc, p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        print("Semua proses telah dimatikan.")

if __name__ == "__main__":
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    if action == "serve":
        serve_all()
    elif action == "start":
        start_all()
    elif action == "stop":
        stop_all()
    elif action == "status":
        check_status()
    else:
        print("Penggunaan: python run_all.py [serve|start|stop|status]")
