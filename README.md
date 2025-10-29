# 🕌 Hijri Clock API

A simple FastAPI-based API that provides **Hijri (Islamic) date** and **daily prayer timings** using the Aladhan API.

---

## 🚀 Endpoints

### 1. `/get_prayer_times`
**Method:** `POST`

Fetch prayer times using either **city/country** or **latitude/longitude**.

#### 📩 Example Request:
```bash
curl -X POST "https://hijri-api.vercel.app/get_prayer_times" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Hyderabad",
    "country": "India",
    "method": 2,
    "local_date": "2025-10-29"
  }'
