from datetime import datetime
import zoneinfo
import requests

SGT = zoneinfo.ZoneInfo("Asia/Singapore")

def check_google(config, start_date):
    name = config.get("name", "Google")
    url = config.get("url", "https://careers.google.com/api/v3/search/?location=Singapore")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"[{name}] HTTP Error {res.status_code}")
            return []
            
        jobs = res.json().get("jobs", [])
        matched = []
        for item in jobs:
            publish_date_str = item.get("publish_date", "")  # ISO format
            job_date = None
            if publish_date_str:
                try:
                    job_date = datetime.fromisoformat(publish_date_str.replace("Z", "+00:00")).astimezone(SGT).date()
                except Exception:
                    pass
            
            if job_date and job_date >= start_date:
                matched.append({
                    "company": name,
                    "title": item.get("title"),
                    "url": f"https://www.google.com/about/careers/applications/jobs/results/{item.get('id')}",
                    "posted": str(job_date)
                })
        print(f"[{name}] {len(matched)} job(s) in target window.")
        return matched
    except Exception as e:
        print(f"[{name}] Failed: {e}")
        return []
