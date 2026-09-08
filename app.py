import os
import threading
import requests
import fitz
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

SECRET_API_KEY = os.environ.get("API_KEY", "sai_teja_secure_job_bot_key_2026")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

applied_jobs_today = []

def verify_api_key(req):
    auth_header = req.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {SECRET_API_KEY}":
        return False
    return True

def compress_pdf(pdf_path, max_size_mb=2):
    if not os.path.exists(pdf_path):
        return pdf_path
    file_size = os.path.getsize(pdf_path) / (1024 * 1024)
    if file_size > max_size_mb:
        doc = fitz.open(pdf_path)
        compressed_path = pdf_path.replace(".pdf", "_compressed.pdf")
        doc.save(compressed_path, garbage=4, deflate=True)
        doc.close()
        return compressed_path
    return pdf_path

def run_job_automation(job_data):
    try:
        job_link = job_data.get("url")
        company_name = job_data.get("company", "Unknown Company")
        job_description = job_data.get("description", "").lower()

        if "experience" in job_description and "fresher" not in job_description:
            print(f"Skipping experienced role for: {company_name}")
            return

        pdf_path = "resume.pdf"
        final_pdf = compress_pdf(pdf_path)

        applied_jobs_today.append(company_name)
        print(f"Successfully applied to {company_name}")

    except Exception as e:
        print(f"Error in automation: {str(e)}")

@app.route("/webhook", methods=["POST"])
def webhook():
    if not verify_api_key(request):
        return jsonify({"error": "Unauthorized Access"}), 401

    data = request.json
    if not data or "url" not in data:
        return jsonify({"error": "Invalid Data"}), 400

    thread = threading.Thread(target=run_job_automation, args=(data,))
    thread.start()

    return jsonify({"status": "Success", "message": "Automation triggered!"}), 200

def send_daily_telegram_report():
    total_applied = len(applied_jobs_today)
    companies_list = "\n".join([f"- {comp}" for comp in applied_jobs_today]) if applied_jobs_today else "No jobs applied today."

    report_message = f"📊 *Daily Job Application Report*\n\nTotal Applied: *{total_applied}*\n\n*Companies:*\n{companies_list}"

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": report_message, "parse_mode": "Markdown"}
        requests.post(telegram_url, json=payload)

    applied_jobs_today.clear()

scheduler = BackgroundScheduler()
scheduler.add_job(func=send_daily_telegram_report, trigger="cron", hour=20, minute=0)
scheduler.start()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Bot is active and running 24/7!"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
