import socket as _socket
# ponytail: force IPv4 — Docker container has broken IPv6 routing (no routes but kernel IPv6 enabled), httpx picks IPv6 causing SSL handshake timeout
_orig_getaddrinfo = _socket.getaddrinfo
def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, _socket.AF_INET, type, proto, flags)
_socket.getaddrinfo = _ipv4_getaddrinfo

import os
import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from tabpfn_client import set_access_token
import traceback

load_dotenv()

# 1. Inisialisasi Model & Auth
TOKEN_TABPFN = os.getenv("TABPFN_TOKEN")

if not TOKEN_TABPFN:
    raise ValueError("ERROR: TABPFN_TOKEN tidak ditemukan! Pastikan file .env sudah dibuat dan diisi.")

set_access_token(TOKEN_TABPFN)

print("Memuat model TabPFN...")
model_ai = joblib.load('model_tabpfn_production.pkl')
print("Model siap digunakan!")

app = FastAPI(title="Permatatex AI Estimation Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Skema Request (DTO)
class PredictionRequest(BaseModel):
    qty_s: float
    qty_m: float
    qty_l: float
    qty_xl: float
    qty_xxl: float
    qty_total: float
    jumlah_size: float
    rasio_s: float
    rasio_m: float
    rasio_l: float
    rasio_xl: float
    rasio_xxl: float
    jenis: float
    men_women: float
    panjang_01: float
    embro: float
    furing: float
    cutting_in_house: float
    konsumsi_kain_per_pcs: float
    jenis_kain: float

# 3. Endpoint Prediksi
@app.post("/api/v1/predict")
def predict_schedule(data: PredictionRequest):
    try:
        df_input = pd.DataFrame([{
            'QTY S': data.qty_s,
            'QTY M': data.qty_m,
            'QTY L': data.qty_l,
            'QTY XL': data.qty_xl,
            'QTY XXL': data.qty_xxl,
            'QTY Total': data.qty_total,
            'Jumlah Size': data.jumlah_size,
            'Rasio S': data.rasio_s,
            'Rasio M': data.rasio_m,
            'Rasio L': data.rasio_l,
            'Rasio XL': data.rasio_xl,
            'Rasio XXL': data.rasio_xxl,
            'Jenis': data.jenis,
            'Men/Women': data.men_women,
            'Panjang 0/1': data.panjang_01,
            'Embro': data.embro,
            'Furing': data.furing,
            'Cutting in House': data.cutting_in_house,
            'Konsumsi Kain per pcs': data.konsumsi_kain_per_pcs,
            'Jenis Kain': data.jenis_kain
        }])

        hasil_prediksi = model_ai.predict(df_input)

        return {
            "status": "success",
            "message": "Estimasi jadwal produksi berhasil dikalkulasi",
            "data": {
                "estimasi_waktu_total_hari": round(float(hasil_prediksi[0][0]), 1),
                "estimasi_tahap_cutting_hari": round(float(hasil_prediksi[0][1]), 1),
                "estimasi_tahap_sewing_hari": round(float(hasil_prediksi[0][2]), 1),
                "estimasi_tahap_qc_hari": round(float(hasil_prediksi[0][3]), 1)
            }
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Gagal melakukan prediksi: {str(e)}")

# 4. Run Server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
