import json
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import zoneinfo

from scrapers import scrape_company

SGT = zoneinfo.ZoneInfo("Asia/Singapore")

def get_business_window():
    """Calculates the date threshold and matching labels for SGT."""
    now_sgt = datetime.now(SGT)
    today = now_sgt.date()
    weekday = today.weekday()  # 0 = Monday, 6 = Sunday

    if weekday == 0:  # Monday: Look back to Friday (3 days prior)
        start_date = today - timedelta(days=3)
        valid_relative = ["posted today", "posted yesterday", "posted 2 days ago", "posted 3 days ago"]
    else:  # Tue-Fri: Look back 1 business day
        start_date = today - timedelta(days=1)
        valid_relative = ["posted today", "posted yesterday"]

    return start_date, valid_relative

def load_companies_config():
    """
    Loads company targets from environment variable (COMPANIES_CONFIG) or
    local companies.json file. Falls back to companies.example.json if neither exists.
    """
    env_config = os.environ.get("COMPANIES_CONFIG")
    if env_config:
        try:
            return json.loads(env_config)
        except Exception as e:
            print(f"Error parsing COMPANIES_CONFIG environment variable: {e}")

    config_path = os.path.join(os.path.dirname(__file__), "companies.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {config_path}: {e}")

    example_path = os.path.join(os.path.dirname(__file__), "companies.example.json")
    if os.path.exists(example_path):
        print("Notice: 'companies.json' not found. Falling back to 'companies.example.json'.")
        try:
            with open(example_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {example_path}: {e}")

    return []

def send_email(jobs, start_date, company_names):
    sender_email = os.environ.get("EMAIL_SENDER")
    app_password = os.environ.get("EMAIL_PASSWORD")
    recipient_email = os.environ.get("EMAIL_RECIPIENT")

    if not all([sender_email, app_password, recipient_email]):
        print("Email secrets missing. Skipping send.")
        return

    today_str = datetime.now(SGT).strftime("%Y-%m-%d")
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Singapore Careers Tracker <{sender_email}>"
    msg["To"] = recipient_email

    checked_summary = ", ".join(company_names) if company_names else "No companies configured"

    if jobs:
        msg["Subject"] = f"🎯 {len(jobs)} New Singapore Job(s) (Since {start_date})"
        rows = "".join(f"""
            <tr style="border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 10px 14px; font-weight: bold; color: #2563eb;">{j['company']}</td>
                <td style="padding: 10px 14px;"><a href="{j['url']}" target="_blank" style="color: #111827; text-decoration: none; font-weight: 500;">{j['title']}</a></td>
                <td style="padding: 10px 14px; color: #4b5563; font-size: 13px;">{j['posted']}</td>
            </tr>
        """ for j in jobs)
        content_body = f"""
            <h2 style="margin-bottom: 8px; color: #111827;">Singapore Career Digest</h2>
            <p style="margin-top: 0; color: #6b7280; font-size: 14px;">Showing jobs posted between <strong>{start_date}</strong> and <strong>{today_str}</strong>.</p>
            <table style="width: 100%; border-collapse: collapse; text-align: left; max-width: 800px; margin-top: 16px;">
                <thead>
                    <tr style="background: #f3f4f6; border-bottom: 2px solid #d1d5db;">
                        <th style="padding: 10px 14px;">Company</th>
                        <th style="padding: 10px 14px;">Role</th>
                        <th style="padding: 10px 14px;">Posted</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        """
    else:
        msg["Subject"] = f"ℹ️ Singapore Careers Check: No New Postings (Since {start_date})"
        content_body = f"""
            <h2 style="margin-bottom: 8px; color: #111827;">Singapore Career Digest</h2>
            <p style="margin-top: 0; color: #6b7280; font-size: 14px;">Checked: {checked_summary}.</p>
            <div style="background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 18px; margin-top: 16px; max-width: 600px;">
                <p style="margin: 0; color: #374151;"><strong>No jobs posted</strong> in Singapore over the last 2 business days (between {start_date} and {today_str}).</p>
            </div>
        """

    html = f"""
    <html>
      <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 24px; background-color: #ffffff;">
        {content_body}
      </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
    print(f"Dispatched email to {recipient_email}")

def main():
    start_date, valid_relative = get_business_window()
    print(f"Running Singapore job scan for window: >= {start_date}")
    print(f"Valid Workday relative tokens: {valid_relative}\n")

    companies = load_companies_config()
    if not companies:
        print("No companies configured to check.")
        return

    company_names = [c.get("name", "Unknown") for c in companies]
    print(f"Loaded {len(companies)} company target(s): {', '.join(company_names)}\n")

    jobs = []
    for company in companies:
        matched = scrape_company(company, start_date, valid_relative)
        jobs.extend(matched)

    print(f"\nTotal qualifying jobs found: {len(jobs)}")
    send_email(jobs, start_date, company_names)

if __name__ == "__main__":
    main()