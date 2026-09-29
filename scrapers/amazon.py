from datetime import datetime
import requests

def check_amazon(config, start_date):
    name = config.get("name", "Amazon")
    url = config.get("url", "https://www.amazon.jobs/en/search.json?country=SGP&radius=24km&result_type=jobs&sort=recent")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"[{name}] HTTP Error {res.status_code}")
            return []
        
        jobs = res.json().get("jobs", [])
        matched = []
        for item in jobs:
            posted_str = item.get("posted_date", "")  # Typically "September 14, 2026"
            try:
                job_date = datetime.strptime(posted_str, "%B %d, %Y").date()
                if job_date >= start_date:
                    matched.append({
                        "company": name,
                        "title": item.get("title"),
                        "url": f"https://amazon.jobs{item.get('job_path')}",
                        "posted": posted_str
                    })
            except Exception:
                continue
        print(f"[{name}] {len(matched)} job(s) in target window (out of {len(jobs)} total).")
        return matched
    except Exception as e:
        print(f"[{name}] Failed: {e}")
        return []
