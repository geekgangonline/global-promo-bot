"""
Email Outreach Script for Global Promo TV
Sends bulk invites to join Whop + Telegram.

Usage:
    python3 outreach/send_invites.py emails.csv [--dry-run]

CSV format:
    name,email
    John Doe,john@example.com

Requires Gmail App Password:
    1. Enable 2FA on your Google account
    2. Generate app password at https://myaccount.google.com/apppasswords
    3. Set env vars: GMAIL_USER=your.email@gmail.com  GMAIL_APP_PASSWORD=xxxx
"""

import csv
import os
import sys
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

WHOP_LINK = "https://whop.com/global-promo-tv"
TELEGRAM_BOT_LINK = "https://t.me/GlobalPromo_bot"
TELEGRAM_GROUPS = [
    ("THE ENGAGEMENT", "Tier 1 — Core engagement circle"),
    ("THE LOUNGE", "Tier 1 — Premium lounge discussions"),
    ("THE COLLECTIVE", "Tier 1 — Collective feedback group"),
    ("THE CYPHER", "Tier 2 — Music critique & cyphers"),
    ("THE STREAM", "Tier 2 — Live streaming community"),
    ("THE THREAD", "Tier 2 — Thread discussions"),
    ("THE RUNWAY", "Tier 2 — Fashion & style"),
    ("THE DAILY GRIND", "Tier 2 — Hustle & motivation"),
]


def send_email_via_gmail(to_email, to_name, dry_run=False):
    """Send a personalized invite email via Gmail SMTP"""
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_pass:
        print("ERROR: Set GMAIL_USER and GMAIL_APP_PASSWORD in .env")
        return False

    subject = f"Join Global Promo TV — Exclusive Creator Network"
    body = f"""Hi {to_name},

You're invited to join Global Promo TV — an exclusive network for music artists, fashion designers, and streamers.

What you get:
🎵 ClipFarm — Get paid to create clips (music, fashion & streaming)
💬 11 private Telegram engagement groups
📈 Feature on our billboard (top engagers weekly)
🤝 Network with 200+ creators

Step 1: Join our Whop membership
{WHOP_LINK}

Step 2: Join our Telegram network
{TELEGRAM_BOT_LINK}

Start earning points, getting feedback, and growing your brand.

See you inside.

— Global Promo TV Team
"""

    msg = MIMEMultipart("alternative")
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg["Subject"] = subject

    html_body = body.replace("\n", "<br>")
    html = f"""<html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<h2 style="color: #1a1a2e;">Join Global Promo TV</h2>
<p style="font-size: 16px; color: #333;">Hi {to_name},</p>
<p style="font-size: 16px; color: #333;">You're invited to join <strong>Global Promo TV</strong> — an exclusive network for music artists, fashion designers, and streamers.</p>

<table style="width: 100%; margin: 20px 0;">
<tr><td style="padding: 8px 0;">🎵 <strong>ClipFarm</strong> — Get paid to create clips</td></tr>
<tr><td style="padding: 8px 0;">💬 <strong>11 private Telegram groups</strong> for engagement</td></tr>
<tr><td style="padding: 8px 0;">📈 <strong>Billboard feature</strong> for top engagers</td></tr>
<tr><td style="padding: 8px 0;">🤝 <strong>Network</strong> with 200+ creators</td></tr>
</table>

<a href="{WHOP_LINK}" style="display: inline-block; background: #e94560; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-size: 16px; margin: 10px 0;">Join Whop Membership</a>
<br><br>
<a href="{TELEGRAM_BOT_LINK}" style="display: inline-block; background: #1a1a2e; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-size: 16px; margin: 10px 0;">Join Telegram Network</a>

<br><br><hr style="border: 1px solid #eee;">
<p style="font-size: 14px; color: #666;">— Global Promo TV Team</p>
</body></html>"""

    msg.attach(MIMEText(body, "plain"))
    msg.attach(MIMEText(html, "html"))

    if dry_run:
        print(f"[DRY RUN] Would send to {to_name} <{to_email}>")
        return True

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(gmail_user, gmail_pass)
        server.sendmail(gmail_user, to_email, msg.as_string())
        server.quit()
        print(f"✓ Sent to {to_name} <{to_email}>")
        return True
    except Exception as e:
        print(f"✗ Failed for {to_email}: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    csv_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        sys.exit(1)

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} contacts from {csv_path}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")

    if not dry_run:
        confirm = input(f"\nSend to {len(rows)} people? (yes/no): ")
        if confirm != "yes":
            print("Cancelled.")
            sys.exit(0)

    sent = 0
    failed = 0

    for row in rows:
        name = row.get("name", "").strip()
        email = row.get("email", "").strip()
        if not email:
            print(f"✗ Skipping row — no email: {row}")
            continue

        ok = send_email_via_gmail(email, name or email.split("@")[0], dry_run)
        if ok:
            sent += 1
        else:
            failed += 1
        time.sleep(2)  # rate limit

    print(f"\n{'='*40}")
    print(f"Done: {sent} sent, {failed} failed")
    if not dry_run:
        print(f"Check your Gmail 'Sent' folder for delivery status.")


if __name__ == "__main__":
    main()
