# Daily Career Tracker 🎯

An automated, privacy-first career tracking bot designed to monitor corporate career portals and deliver fresh job openings directly to your inbox every business day.

[![Daily Career Check](https://github.com/samucospace/daily-job-check/actions/workflows/daily_scrape.yml/badge.svg)](https://github.com/samucospace/daily-job-check/actions/workflows/daily_scrape.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📌 About

Job hunting often requires checking dozens of company career boards repeatedly for new postings before they get saturated with applicants. 

**Daily Career Tracker** automates this routine:
- Queries official ATS APIs (such as **Workday CXS** and bespoke corporate career endpoints) on a scheduled basis.
- Automatically calculates business-day lookback windows (e.g. accounting for weekends on Monday runs).
- Filters for recently posted positions in your target location (default configured for Singapore SGT timezone).
- Compiles matches into a clean, modern HTML email digest dispatched via SMTP.

### 🔒 Privacy-First by Design
This repository is architected so that the tracking engine is completely decoupled from your target company list:
- **Local Runs**: Your company list lives in `companies.json` and is ignored by `.gitignore`.
- **Public GitHub Deployment**: When deployed via GitHub Actions, your target companies are supplied via encrypted GitHub Secrets (`COMPANIES_CONFIG`), meaning your repository can remain 100% public without exposing what companies you are actively tracking or applying to.

---

## ✨ Features

- **Modular Scraper Architecture**: Plug-and-play scrapers for Workday ATS portals and custom career APIs.
- **Smart Date Windowing**: Accounts for weekends (on Mondays, it checks Friday through Sunday postings; on Tue–Fri, it checks the previous business day).
- **Clean HTML Digest**: Sends a formatted digest table of newly posted roles, or an informative status email if no new roles were posted.
- **Scheduled Automation**: Fully automated via GitHub Actions cron schedules with zero hosting costs.
- **Manual Trigger Support**: Run on demand anytime using the GitHub Actions `workflow_dispatch` button.

---

## 📁 Project Structure

```text
daily-job-check/
├── .github/
│   └── workflows/
│       └── daily_scrape.yml    # GitHub Actions cron & dispatch configuration
├── scrapers/
│   ├── __init__.py             # Scraper registry & dispatcher
│   ├── workday.py              # Generic Workday CXS scraper
│   ├── amazon.py               # Amazon Jobs scraper
│   ├── microsoft.py            # Microsoft Phenom scraper
│   └── google.py               # Google Careers scraper
├── .gitignore                  # Keeps private configs & state out of version control
├── companies.example.json      # Public template showing configuration schema
├── companies.json              # Local private target list (gitignored)
├── main.py                     # Main orchestrator & email generator
└── requirements.txt            # Python dependencies
```

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the repository
```bash
git clone https://github.com/samucospace/daily-job-check.git
cd daily-job-check
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your companies
Create your private `companies.json` by copying the example template:
```bash
cp companies.example.json companies.json
```

Edit `companies.json` to define your target companies (see [Configuration Guide](#-configuration-guide)).

### 4. Set Environment Variables
Set your email credentials (e.g. using a [Gmail App Password](https://support.google.com/accounts/answer/185833)):
```bash
export EMAIL_SENDER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export EMAIL_RECIPIENT="your-destination@email.com"
```

### 5. Run the tracker
```bash
python main.py
```

---

## ⚙️ Configuration Guide

Each target company in `companies.json` is a JSON object with a `type` that maps to a scraper module.

### Workday Portals (`type: "workday"`)
Workday CXS endpoints accept structured JSON search payloads and country/location facets:
```json
{
  "type": "workday",
  "name": "Acme Corp",
  "origin_host": "acme.wd1.myworkdayjobs.com",
  "tenant_path": "acme/Careers",
  "payload": {
    "appliedFacets": {
      "locationCountry": ["80938777cac5440fab50d729f9634969"]
    },
    "limit": 20,
    "offset": 0,
    "searchText": ""
  }
}
```

### Built-in Corporate Scrapers
For career boards with custom endpoints, specify the corresponding type:
```json
{ "type": "amazon", "name": "Amazon" },
{ "type": "microsoft", "name": "Microsoft" },
{ "type": "google", "name": "Google" }
```

---

## ☁️ Running on GitHub Actions (Public Repository)

To run this on GitHub Actions without revealing your target companies:

1. Push your fork / repository to GitHub.
2. In your GitHub repository, navigate to **Settings** > **Secrets and variables** > **Actions**.
3. Create the following **Repository Secrets**:
   - `EMAIL_SENDER`: Your sending email address (e.g. `your-email@gmail.com`).
   - `EMAIL_PASSWORD`: Your email app password.
   - `EMAIL_RECIPIENT`: Destination email address for daily reports.
   - `COMPANIES_CONFIG`: Paste the raw JSON content of your private `companies.json`.
4. The workflow in [`.github/workflows/daily_scrape.yml`](.github/workflows/daily_scrape.yml) will automatically run on the scheduled cron time and read your targets securely from encrypted secrets.

---

## 🛠️ Adding a New Scraper

1. Create a new file in `scrapers/my_company.py`:
   ```python
   def check_my_company(config, start_date):
       name = config.get("name", "Custom Company")
       # Implement search/request logic
       return [{"company": name, "title": "Role", "url": "https://...", "posted": "2026-09-29"}]
   ```

2. Register it in [`scrapers/__init__.py`](scrapers/__init__.py):
   ```python
   from .my_company import check_my_company

   SCRAPERS = {
       # ...
       "my_company": lambda cfg, start_date, valid_rel: check_my_company(cfg, start_date),
   }
   ```

3. Add entries using `"type": "my_company"` to your `companies.json`.

---

## 📄 License

This project is licensed under the MIT License.
