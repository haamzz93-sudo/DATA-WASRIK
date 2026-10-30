# 🔌 Panduan Integrasi API Eksternal (DS-001 s/d DS-006) ke Wasrik AI

Dokumen ini berisi format endpoint, skema payload, dan contoh fungsi integrasi Python (`httpx` / `requests`) untuk langsung di-copy-paste ke backend/agent tools Wasrik AI di VPS (`wasrik.unsmadiun.id`).

---

## 1. Matriks Endpoint Integrasi

| Service | Port | Endpoint Wasrik | Method | Deskripsi Data yang Ditarik |
| :--- | :---: | :--- | :---: | :--- |
| **DS-001** | `9001` | `/api/v1/employers/{nib}` | `GET` | Master profil Badan Usaha, skala usaha, jumlah peserta terdaftar JKN |
| **DS-002** | `9002` | `/api/v1/wages/{nib}` | `GET` | Data upah terlaporkan SIPP BPJS TK, sample NIK salted-hash |
| **DS-003** | `9003` | `/api/v1/wlkp/reports/{nib}` | `GET` | Data upah & pekerja riil (PKWTT + PKWT) SIAPkerja Kemnaker |
| **DS-004** | `9004` | `/api/v1/billing/{nib}` | `GET` | Status pembayaran iuran 4%+1%, histori tunggakan & denda |
| **DS-005** | `9005` | `/api/v1/claims/company/{company_id}` | `GET` | Transaksi riil klaim RS (FKRTL), kode ICD-10 & biaya INA-CBGs |
| **DS-006** | `9006` | `/api/v1/sanctions/{nib}` | `GET` / `POST` | Status kepatuhan PP 86/2013, blokir izin OSS BKPM / TMP2T |

---

## 2. Kode Integrasi Python Siap Copas (Wasrik Agent Tool)

File: `wasrik_data_client.py`

```python
import httpx
from typing import Dict, Any, Optional

class WasrikDataLakeClient:
    def __init__(self, base_host: str = "http://localhost"):
        self.base_host = base_host
        self.headers = {"Accept": "application/json"}

    def get_master_bu(self, nib: str) -> Optional[Dict[str, Any]]:
        """DS-001: Tarik Profil Master Badan Usaha JKN"""
        url = f"{self.base_host}:9001/api/v1/employers/{nib}?format=json"
        res = httpx.get(url, headers=self.headers, timeout=5.0)
        return res.json().get("data") if res.status_code == 200 else None

    def get_sipp_wage(self, nib: str) -> Optional[Dict[str, Any]]:
        """DS-002: Tarik Upah Terlaporkan SIPP BPJS TK"""
        url = f"{self.base_host}:9002/api/v1/wages/{nib}"
        res = httpx.get(url, headers=self.headers, timeout=5.0)
        return res.json().get("data") if res.status_code == 200 else None

    def get_wlkp_real(self, nib: str) -> Optional[Dict[str, Any]]:
        """DS-003: Tarik Upah & Jumlah Pekerja Riil WLKP Kemnaker"""
        url = f"{self.base_host}:9003/api/v1/wlkp/reports/{nib}"
        res = httpx.get(url, headers=self.headers, timeout=5.0)
        return res.json().get("data") if res.status_code == 200 else None

    def get_billing_status(self, nib: str) -> Optional[Dict[str, Any]]:
        """DS-004: Tarik Buku Piutang & Tunggakan Iuran BPJS Kes"""
        url = f"{self.base_host}:9004/api/v1/billing/{nib}"
        res = httpx.get(url, headers=self.headers, timeout=5.0)
        return res.json().get("data") if res.status_code == 200 else None

    def get_medical_claims(self, company_id: str) -> Optional[Dict[str, Any]]:
        """DS-005: Tarik Morbiditas & Klaim INA-CBGs Real Rilis 2024"""
        url = f"{self.base_host}:9005/api/v1/claims/company/{company_id}"
        res = httpx.get(url, headers=self.headers, timeout=5.0)
        return res.json() if res.status_code == 200 else None

    def check_or_issue_sanction(self, nib: str, issue_payload: Optional[dict] = None) -> Optional[Dict[str, Any]]:
        """DS-006: Cek atau Terbitkan Sanksi PP 86/2013 ke BKPM OSS"""
        if issue_payload:
            url = f"{self.base_host}:9006/api/v1/sanctions/issue"
            res = httpx.post(url, json=issue_payload, headers=self.headers, timeout=5.0)
        else:
            url = f"{self.base_host}:9006/api/v1/sanctions/{nib}"
            res = httpx.get(url, headers=self.headers, timeout=5.0)
        return res.json().get("data") if res.status_code == 200 else None

    def audit_reconcile_employer(self, nib: str) -> Dict[str, Any]:
        """Engine Otomatis Wasrik: Rekonsiliasi Selisih Upah & PDUK"""
        bu = self.get_master_bu(nib)
        if not bu:
            return {"status": "error", "message": f"NIB {nib} tidak ditemukan di master data."}

        sipp = self.get_sipp_wage(nib)
        wlkp = self.get_wlkp_real(nib)
        billing = self.get_billing_status(nib)
        claims = self.get_medical_claims(bu["id"])

        # Perhitungan Anomali
        reported_wage = sipp["average_reported_wage"] if sipp else 0
        real_wage = wlkp["payroll_aggregates"]["average_real_wage"] if wlkp else 0
        wage_gap = max(0, real_wage - reported_wage)

        reported_workers = sipp["total_reported_workers"] if sipp else 0
        real_workers = wlkp["workforce_composition"]["total_active_workers"] if wlkp else 0
        pduk_gap = max(0, real_workers - reported_workers)

        potential_lost_contribution = (wage_gap * reported_workers * 0.05) + (pduk_gap * real_wage * 0.05)

        return {
            "company_name": bu["company_name"],
            "nib": nib,
            "wage_gap_idr": wage_gap,
            "pduk_unregistered_workers": pduk_gap,
            "potential_monthly_lost_contribution_idr": potential_lost_contribution,
            "arrears_months": billing.get("arrears_months", 0) if billing else 0,
            "total_medical_claims_count": claims.get("total_claims", 0) if claims else 0
        }

# --- Contoh Uji Coba Langsung ---
if __name__ == "__main__":
    client = WasrikDataLakeClient()
    result = client.audit_reconcile_employer("0123456789012")  # PT Cipta Busana Mandiri
    print("Hasil Audit Cross-Reconcile:", result)
```

---

## 3. Contoh Response JSON (Untuk Mock / Unit Testing)

```json
{
  "status": "success",
  "data": {
    "id": "BU-006",
    "nib": "7788990011223",
    "company_name": "PT Global Prima Elektronik",
    "sector": "Industri Peralatan Elektronik",
    "scale": "Besar",
    "address": "Kawasan Industri Lippo Cikarang Blok B-12",
    "bpjs_registered_employees": 410,
    "total_active_employees": 620,
    "compliance_status": "TMP2T_REKOMENDASI",
    "compliance_score": 93.8
  }
}
```
