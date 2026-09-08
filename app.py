import os
import threading
import requests  # type: ignore
from flask import Flask, jsonify, request  # type: ignore
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore

app = Flask(__name__)

# Secret API Key and Telegram credentials for security and notifications
SECRET_API_KEY = os.environ.get("API_KEY", "sai_teja_secure_job_bot_key_2026")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

# List to track jobs applied for today
applied_jobs_today = []


def verify_api_key(req):
  """Function to check if the incoming request from n8n has a valid API key"""
  auth_header = req.headers.get("Authorization")
  if not auth_header or auth_header != f"Bearer {SECRET_API_KEY}":
    return False
  return True


def run_job_automation(job_data):
  """Core job application automation logic (Runs in the background)"""
  try:
    job_link = job_data.get("url")
    company_name = job_data.get("company", "Unknown Company")

    print(f"Automation started for: {company_name} - {job_link}")

    # TODO: Write your Playwright / Selenium automation code here
    # 1. Open link and check if it's a Fresher/Internship role
    # 2. Sign up / Log in if required
    # 3. Upload PDF resume & generate/upload AI cover letter
    # 4. Handle CAPTCHA / OTP via Telegram Bot if prompted

    # Add to success list after applying
    applied_jobs_today.append(company_name)
    print(f"Successfully applied to {company_name}")

  except Exception as e:
    print(f"Error occurred in automation: {str(e)}")


@app.route("/webhook", methods=["POST"])
def webhook():
  """Webhook endpoint to receive data from n8n"""
  if not verify_api_key(request):
    return jsonify({"error": "Unauthorized Access"}), 401

  data = request.json
  if not data or "url" not in data:
    return jsonify({"error": "Invalid Data, 'url' is required"}), 400

  # Use threading to run in the background without blocking the server
  thread = threading.Thread(target=run_job_automation, args=(data,))
  thread.start()

  return (
      jsonify(
          {
              "status": "Success",
              "message": "Automation triggered in background!",
          }
      ),
      200,
  )


def send_daily_telegram_report():
  """Function to send daily report to Telegram at 8:00 PM"""
  print("Sending daily 8:00 PM report to Telegram...")
  total_applied = len(applied_jobs_today)
  companies_list = (
      "\n".join([f"- {comp}" for comp in applied_jobs_today])
      if applied_jobs_today
      else "No jobs applied today."
  )

  report_message = (
      f"📊 *Daily Job Application Report (8:00 PM)*\n\n"
      f"Total Applied Today: *{total_applied}*\n\n"
      f"*Companies List:*\n{companies_list}"
  )

  # Send report via Telegram Bot API
  if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    telegram_url = (
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": report_message,
        "parse_mode": "Markdown",
    }
    try:
      response = requests.post(telegram_url, json=payload)
      if response.status_code == 200:
        print("Daily report sent successfully to Telegram.")
      else:
        print(f"Failed to send Telegram report: {response.text}")
    except Exception as e:
      print(f"Error sending Telegram report: {str(e)}")

  # Clear the list after sending the report
  applied_jobs_today.clear()


# Setup schedule to run daily at 8:00 PM using APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=send_daily_telegram_report, trigger="cron", hour=20, minute=0
)
scheduler.start()


@app.route("/", methods=["GET"])
def home():
  """Health check route to verify if the server is active"""
  return jsonify({"status": "Bot is active and running 24/7!"}), 200


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)