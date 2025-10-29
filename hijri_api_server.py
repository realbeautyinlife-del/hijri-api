from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(title="Hijri Clock API", description="Fetch Hijri Date & Islamic Prayer Timings", version="1.0")

# ---------------------------
# Data Models
# ---------------------------

class PrayerRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None
    method: int
    local_date: str


# ---- Root Endpoint ----
@app.get("/")
def root():
    return {"message": "Welcome to Hijri Clock API. Use /get_prayer_times to get timings."}


# ---------------------------
# API ENDPOINT 1 — BY CITY & COUNTRY
# ---------------------------

@app.post("/get_prayer_times")
def get_prayer_times(req: PrayerRequest):
    try:
        # Validate the date format
        datetime.strptime(req.local_date, "%Y-%m-%d")
        converted_date = datetime.strptime(req.local_date, "%Y-%m-%d").strftime("%d-%m-%Y")

        # Choose API endpoint based on input
        if req.latitude and req.longitude:
            url = f"https://api.aladhan.com/v1/timings/{converted_date}"
            params = {
                "latitude": req.latitude,
                "longitude": req.longitude,
                "method": req.method
            }
        elif req.city and req.country:
            url = f"https://api.aladhan.com/v1/timingsByCity/{converted_date}"
            params = {
                "city": req.city,
                "country": req.country,
                "method": req.method
            }
        else:
            raise HTTPException(status_code=400, detail="Either provide (latitude & longitude) OR (city & country).")


        response = requests.get(url, params=params)
        data = response.json()

        if data["code"] != 200:
            raise HTTPException(status_code=400, detail="Invalid request or API error")

        # Extract required fields
        # hijri_date = data["data"]["date"]["hijri"]["date"]
        readable_date = data["data"]["date"]["readable"]
        prayer_timings = data["data"]["timings"]
        arabic_weekday = data["data"]["date"]["hijri"]["weekday"]["en"]

        hijri_moth = data["data"]["date"]["hijri"]["month"]["en"]
        hijri_Year = data["data"]["date"]["hijri"]["year"]
        hijri_day = data["data"]["date"]["hijri"]["day"]

        timings = data["data"]["timings"]

        maghrib_str = timings["Maghrib"]
        isha_str = timings["Isha"]
        # Firstthird_str =timings["Firstthird"]
        lastthird_str =timings["Lastthird"]
        Fajr_str =timings["Fajr"]
        Sunrise_str =timings["Sunrise"]
        Dhuhr_str =timings["Dhuhr"]
        Asr =timings["Asr"]
        middNight =date_diff_to_add(maghrib_str,"23:59")

        # hijri_date =f"{hijri_day}-{hijri_moth}-{hijri_Year}"
        hijri_full_date = f"{hijri_day} {hijri_moth} {hijri_Year}"

        return {
            "status": "success",
            "gregorian_date": readable_date,
            "arabic_weekday": arabic_weekday,
            # "hijri_moth":hijri_moth,
            # "hijri_Year":hijri_Year,
            # "hijri_day":hijri_day,
            "hijri_full_date":hijri_full_date,
            # "city": req.city,
            # "country": req.country,
            "method": req.method,
            "Maghrib":maghrib_str,
            "ishan":date_diff_to_add(maghrib_str,isha_str),
            "last_night":date_add_to_add(middNight,lastthird_str),
            "fajir":date_add_to_add(middNight,Fajr_str),
            "Sunrise":date_add_to_add(middNight,Sunrise_str),
            "FDhuhr":date_add_to_add(middNight,Dhuhr_str),
            "Asr":date_add_to_add(middNight,Asr),
            "timings": prayer_timings
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ---------------------------
# Helper Functions
# ---------------------------

# clocktime calculation
def date_diff_to_add(first_time,second_time):
    
    # Convert to datetime objects (same date, for simplicity)
    fmt = "%H:%M"
    maghrib_time = datetime.strptime(first_time, fmt)
    isha_time = datetime.strptime(second_time, fmt)

    # Compute the difference
    time_diff = isha_time - maghrib_time

    # Convert difference to hours and minutes
    total_seconds = time_diff.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    # Format nicely
    isha_gap = f"{hours:02d}:{minutes:02d}"
    return isha_gap
    # print(isha_gap)

# clocktime calculation
def date_add_to_add(first_time,second_time):
    
    # Convert to datetime objects (same date, for simplicity)
    fmt = "%H:%M"
    maghrib_time = datetime.strptime(first_time, fmt)
    isha_time = datetime.strptime(second_time, fmt)
    
    # Convert time2 into a timedelta (1 hour 1 minute)
    delta = timedelta(hours=maghrib_time.hour, minutes=maghrib_time.minute)

    # Compute the difference
    time_diff = isha_time + delta

    # Convert difference to hours and minutes
    # total_seconds = time_diff.total_seconds()
    # hours = int(total_seconds // 3600)
    # minutes = int((total_seconds % 3600) // 60)

    # # Format nicely
    # isha_gap = f"{hours:02d}:{minutes:02d}"
    return time_diff.strftime("%H:%M")
    # print(isha_gap)
