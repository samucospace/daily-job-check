import requests

def check_workday(config, valid_relative):
    """
    Scrapes jobs from Workday CXS API.
    Expected config keys:
      - name: str (Display name of company)
      - origin_host: str (e.g. 'example.wd1.myworkdayjobs.com')
      - tenant_path: str (e.g. 'example/Careers')
      - payload: dict (JSON search payload)
    """
    name = config.get("name", "Workday")
    origin_host = config.get("origin_host")
    tenant_path = config.get("tenant_path")
    payload = config.get("payload", {})

    endpoint = f"https://{origin_host}/wday/cxs/{tenant_path}/jobs"
    session = requests.Session()
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": f"https://{origin_host}",
        "Referer": f"https://{origin_host}/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    try:
        session.get(f"https://{origin_host}/en-US/{tenant_path.split('/')[-1]}", headers=headers, timeout=10)
        res = session.post(endpoint, headers=headers, json=payload, timeout=15)
        if res.status_code != 200:
            print(f"[{name}] HTTP Error {res.status_code}")
            return []
        
        postings = res.json().get("jobPostings", [])
        matched = []
        for item in postings:
            posted_text = item.get("postedOn", "")
            clean_text = posted_text.strip().lower() if posted_text else ""
            if any(rel in clean_text for rel in valid_relative):
                matched.append({
                    "company": name,
                    "title": item.get("title"),
                    "url": f"https://{origin_host}{item.get('externalPath', '')}",
                    "posted": posted_text
                })
        print(f"[{name}] {len(matched)} job(s) in target window (out of {len(postings)} total).")
        return matched
    except Exception as e:
        print(f"[{name}] Failed: {e}")
        return []
