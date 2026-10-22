from datetime import datetime
import urllib.parse
import zoneinfo
import requests

SGT = zoneinfo.ZoneInfo("Asia/Singapore")

def check_ashby(config, start_date):
    """
    Scrapes jobs from Ashby's public Job Postings API.
    Expected config keys:
      - name: str (Display name of company, e.g. 'Mistral AI')
      - job_board_name: str (e.g. 'mistral.ai') OR url: str (e.g. 'https://jobs.ashbyhq.com/mistral.ai')
      - location: str or list (e.g. 'Singapore' [default], 'all' or None to disable filter)
    """
    name = config.get("name", "Ashby")
    board_name = config.get("job_board_name")
    if not board_name and config.get("url"):
        parsed_path = urllib.parse.urlparse(config["url"]).path.strip("/")
        if parsed_path:
            board_name = parsed_path.split("/")[0]

    if not board_name:
        board_name = name.lower()

    target_location = config.get("location", "Singapore")
    api_url = f"https://api.ashbyhq.com/posting-api/job-board/{board_name}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }

    try:
        res = requests.get(api_url, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"[{name}] HTTP Error {res.status_code}")
            return []

        data = res.json()
        jobs = data.get("jobs", [])
        matched = []

        for item in jobs:
            if not item.get("isListed", True):
                continue

            # Location filtering
            if target_location and str(target_location).lower() != "all":
                loc_tokens = [item.get("location") or ""]
                for sec in item.get("secondaryLocations", []):
                    if isinstance(sec, dict):
                        loc_tokens.append(sec.get("location") or "")
                        addr = sec.get("address", {}).get("postalAddress", {})
                        loc_tokens.extend([
                            addr.get("addressCountry", ""),
                            addr.get("addressRegion", ""),
                            addr.get("addressLocality", "")
                        ])
                    elif isinstance(sec, str):
                        loc_tokens.append(sec)

                addr = item.get("address", {}).get("postalAddress", {})
                loc_tokens.extend([
                    addr.get("addressCountry", ""),
                    addr.get("addressRegion", ""),
                    addr.get("addressLocality", "")
                ])
                all_loc_text = " ".join(loc_tokens).lower()

                if isinstance(target_location, list):
                    if not any(loc.lower() in all_loc_text for loc in target_location):
                        continue
                else:
                    if str(target_location).lower() not in all_loc_text:
                        continue

            pub_str = item.get("publishedAt", "")
            job_date = None
            if pub_str:
                try:
                    job_date = datetime.fromisoformat(pub_str.replace("Z", "+00:00")).astimezone(SGT).date()
                except Exception:
                    pass

            if job_date and job_date >= start_date:
                matched.append({
                    "company": name,
                    "title": item.get("title"),
                    "url": item.get("jobUrl"),
                    "posted": str(job_date)
                })

        print(f"[{name}] {len(matched)} job(s) in target window (out of {len(jobs)} total).")
        return matched
    except Exception as e:
        print(f"[{name}] Failed: {e}")
        return []
