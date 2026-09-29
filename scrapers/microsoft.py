from datetime import datetime
import zoneinfo
import requests

SGT = zoneinfo.ZoneInfo("Asia/Singapore")

def check_microsoft(config, start_date):
    name = config.get("name", "Microsoft")
    url = config.get("url", "https://apply.careers.microsoft.com/api/apply/v2/jobs?domain=microsoft.com&location=Singapore&remote=1&sort_by=timestamp")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"[{name}] HTTP Error {res.status_code}")
            return []
            
        data = res.json()
        positions = data.get("positions", []) or data.get("jobs", [])
        matched = []
        for item in positions:
            # Phenom backend often supplies postedDate ISO or timestamp
            posted_raw = item.get("postedDate") or item.get("creationDate") or ""
            job_date = None
            if posted_raw:
                try:
                    job_date = datetime.fromisoformat(posted_raw.replace("Z", "+00:00")).astimezone(SGT).date()
                except Exception:
                    pass
            
            if job_date and job_date >= start_date:
                job_id = item.get("id") or item.get("jobId")
                matched.append({
                    "company": name,
                    "title": item.get("name") or item.get("title"),
                    "url": f"https://apply.careers.microsoft.com/careers/job/{job_id}",
                    "posted": str(job_date)
                })
        print(f"[{name}] {len(matched)} job(s) in target window.")
        return matched
    except Exception as e:
        print(f"[{name}] Failed: {e}")
        return []
