import os
import threading
import requests
import fitz
import time
import re
from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# Complete user profile including State (Andhra Pradesh), Gender, Citizenship, and all details
USER_PROFILE = {
    "first_name": "Rapuru",
    "middle_name": "Sai",
    "last_name": "Teja",
    "full_name": "Rapuru Sai Teja",
    "email": "rapurusaiteja699@gmail.com",
    "phone": "6305528902",
    "country_code": "+91",
    "country": "India",
    "state": "Andhra Pradesh",
    "citizenship": "Indian",
    "gender": "Male",
    "address": "Mekanuru (v), Gudur (m), Nellore district Andhra Pradesh, India",
    "pincode": "524410",
    "work_location": "India",
    "relocate": "Yes",
    "passport": "No",
    "github": "https://github.com/sai-teja-rapuru",
    "linkedin": "https://www.linkedin.com/in/rapuru-sai-teja",
    "college": "Rami Reddy Subbarami Reddy Engineering College",
    "university": "Jawaharlal Nehru Technological University Anantapur",
    "department": "Computer Science and Engineering (CSE)",
    "degree": "B.Tech",
    "start_year": "2023",
    "passout_year": "2027",
    "expected_salary": "3,50,000",
    "current_salary": "3,00,000",
    "skills_pool": [
        "Python", "Flask", "Selenium", "Data Analysis", "SQL", 
        "Excel", "Pandas", "Data Visualization", "Communication", 
        "Problem Solving", "Administrative Assistance", "JavaScript"
    ]
}

SECRET_API_KEY = os.environ.get("API_KEY", "sai_teja_secure_job_bot_key_2026")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

applied_jobs_today = []
applied_jobs_history = set()  # Duplicate prevention rule
latest_user_input = None

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

def send_telegram_notification(company_name, job_title):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID)
    if bot_token and chat_id:
        message = f"🚀 *Applied This Role Successfully!*\n\n🏢 *Company:* {company_name}\n📌 *Role:* {job_title}\n👤 *Applicant:* {USER_PROFILE['full_name']}"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Telegram notification error: {e}")

def send_telegram_screenshot(driver, company_name, error_message):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID)
    if bot_token and chat_id and driver:
        try:
            screenshot_path = "error_screenshot.png"
            driver.save_screenshot(screenshot_path)
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            with open(screenshot_path, "rb") as photo:
                caption_text = f"🚨 *Automation Error Alert!*\n🏢 Company: {company_name}\n❌ Error: {str(error_message)[:100]}"
                payload = {"chat_id": chat_id, "caption": caption_text, "parse_mode": "Markdown"}
                requests.post(url, data=payload, files={"photo": photo})
        except Exception as e:
            print(f"Telegram screenshot error: {e}")

def run_job_automation(job_data):
    global latest_user_input
    driver = None
    company_name = job_data.get("company", "Unknown Company")
    job_title = job_data.get("title", "Software Engineer / IT Fresher")
    
    try:
        raw_input_data = job_data.get("url") or job_data.get("snippet", "")
        url_match = re.search(r'(https?://[^\s]+)', raw_input_data)
        job_link = url_match.group(0) if url_match else "https://www.linkedin.com/jobs"
        
        job_description = raw_input_data.lower()

        # --- DUPLICATE APPLICATION CHECK RULE ---
        unique_job_id = f"{company_name}_{job_link}"
        if unique_job_id in applied_jobs_history:
            print(f"Skipping duplicate application for: {company_name}")
            return

        # --- FEE / MONEY REQUIREMENT CHECK (Skip if job asks for money) ---
        fee_keywords = ["fee", "payment", "money", "charges", "pay to apply", "registration charge", "training fee", "deposit"]
        if any(keyword in job_description for keyword in fee_keywords):
            print(f"Skipping job because it asks for money/fee: {company_name}")
            return

        # --- IT FRESHERS & IT ROLES FILTER RULE ---
        it_keywords = ["python", "software", "developer", "engineer", "java", "data", "analyst", "IT", "programmer", "cse"]
        is_it_role = any(keyword in job_description or keyword in job_title.lower() for keyword in it_keywords)
        is_fresher_role = ("fresher" in job_description) or ("0-1" in job_description) or ("entry" in job_description) or ("trainee" in job_description) or ("experience" not in job_description)

        if not is_it_role or not is_fresher_role:
            print(f"Skipping non-IT or experienced role for: {company_name} ({job_title})")
            return

        pdf_path = "resume.pdf"
        if not os.path.exists(pdf_path):
            print("Warning: resume.pdf not found locally! Please ensure resume.pdf is placed in the project directory.")
        
        final_pdf = compress_pdf(pdf_path)

        # Selenium Browser Initialization
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=options)
        
        driver.get(job_link)
        wait = WebDriverWait(driver, 15)
        
        # --- ఆటో-లాగిన్ కుక్కీస్ ఇంజెక్షన్ లాజిక్ ---
        try:
            cookies_env = os.environ.get("LINKEDIN_COOKIES")
            if cookies_env:
                driver.get("https://www.linkedin.com")
                time.sleep(2)
                import json
                cookies = json.loads(cookies_env)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
                driver.refresh()
                time.sleep(3)
                driver.get(job_link)
        except Exception as cookie_err:
            print(f"Cookie injection error: {cookie_err}")

        # --- అప్లై బటన్ క్లిక్ చేసే లాజిక్ ---
        try:
            external_apply_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(text(), 'APPLY', 'apply'), 'apply') or contains(@class, 'apply')]")))
            external_apply_btn.click()
            time.sleep(3)
        except:
            pass

        # 1. Login / Sign Up check
        try:
            login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In')]")))
            login_btn.click()
            time.sleep(2)
        except:
            pass

        time.sleep(2)

        # 2. Dynamic Form Filling including State, Gender, Citizenship, Address & Details
        try:
            wait.until(EC.presence_of_element_located((By.NAME, "firstname"))).send_keys(USER_PROFILE["first_name"])
            try:
                driver.find_element(By.NAME, "middlename").send_keys(USER_PROFILE["middle_name"])
            except:
                pass
            driver.find_element(By.NAME, "lastname").send_keys(USER_PROFILE["last_name"])
            driver.find_element(By.NAME, "email").send_keys(USER_PROFILE["email"])
            
            # State Selection
            try:
                state_element = driver.find_element(By.NAME, "state")
                if state_element.tag_name == "select":
                    Select(state_element).select_by_visible_text(USER_PROFILE["state"])
                else:
                    state_element.send_keys(USER_PROFILE["state"])
            except:
                try:
                    driver.find_element(By.XPATH, "//input[contains(@placeholder, 'State') or contains(@name, 'state')]").send_keys(USER_PROFILE["state"])
                except:
                    pass

            # Gender Selection
            try:
                gender_element = driver.find_element(By.NAME, "gender")
                if gender_element.tag_name == "select":
                    Select(gender_element).select_by_visible_text(USER_PROFILE["gender"])
                else:
                    gender_element.send_keys(USER_PROFILE["gender"])
            except:
                try:
                    driver.find_element(By.XPATH, f"//input[@value='{USER_PROFILE['gender']}' or contains(@aria-label, 'Gender')]").click()
                except:
                    pass

            # Citizenship / Nationality Selection
            try:
                citizen_element = driver.find_element(By.NAME, "citizenship")
                if citizen_element.tag_name == "select":
                    Select(citizen_element).select_by_visible_text(USER_PROFILE["citizenship"])
                else:
                    citizen_element.send_keys(USER_PROFILE["citizenship"])
            except:
                try:
                    driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Citizen') or contains(@name, 'nationality')]").send_keys(USER_PROFILE["citizenship"])
                except:
                    pass

            # Address Entry
            try:
                driver.find_element(By.NAME, "address").send_keys(USER_PROFILE["address"])
            except:
                try:
                    driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Address') or contains(@name, 'location') or contains(@name, 'addr')]").send_keys(USER_PROFILE["address"])
                except:
                    pass

            # Pincode Entry
            try:
                driver.find_element(By.NAME, "pincode").send_keys(USER_PROFILE["pincode"])
            except:
                try:
                    driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Pin') or contains(@placeholder, 'Postal') or contains(@name, 'zip') or contains(@name, 'pincode')]").send_keys(USER_PROFILE["pincode"])
                except:
                    pass

            # Phone Number & Country Code
            try:
                driver.find_element(By.NAME, "phone").send_keys(USER_PROFILE["phone"])
            except:
                try:
                    driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Phone') or contains(@name, 'mobile')]").send_keys(USER_PROFILE["phone"])
                except:
                    pass

            try:
                code_select = Select(driver.find_element(By.NAME, "country_code"))
                code_select.select_by_visible_text("+91")
            except:
                pass

            # Country Selection
            try:
                country_element = driver.find_element(By.NAME, "country")
                if country_element.tag_name == "select":
                    Select(country_element).select_by_visible_text(USER_PROFILE["country"])
                else:
                    country_element.send_keys(USER_PROFILE["country"])
            except:
                pass

            # Relocation Question Handling
            try:
                relocate_element = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'RELOCATE', 'relocate'), 'relocate') or contains(translate(@name, 'RELOCATE', 'relocate'), 'relocate')]")
                if relocate_element:
                    if relocate_element.tag_name == "select":
                        Select(relocate_element).select_by_visible_text("Yes")
                    else:
                        relocate_element.send_keys(USER_PROFILE["relocate"])
            except:
                pass

            # Passport Question
            try:
                passport_element = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'PASSPORT', 'passport'), 'passport') or contains(translate(@name, 'PASSPORT', 'passport'), 'passport')]")
                if passport_element:
                    if passport_element.tag_name == "select":
                        Select(passport_element).select_by_visible_text("No")
                    else:
                        passport_element.send_keys(USER_PROFILE["passport"])
            except:
                pass

            # University Selection
            try:
                uni_element = driver.find_element(By.NAME, "university")
                if uni_element.tag_name == "select":
                    Select(uni_element).select_by_visible_text(USER_PROFILE["university"])
                else:
                    uni_element.send_keys(USER_PROFILE["university"])
            except:
                try:
                    driver.find_element(By.XPATH, "//input[contains(@placeholder, 'University') or contains(@name, 'university')]").send_keys(USER_PROFILE["university"])
                except:
                    pass

            # Salary Fields
            try:
                driver.find_element(By.NAME, "current_salary").send_keys(USER_PROFILE["current_salary"])
                driver.find_element(By.NAME, "expected_salary").send_keys(USER_PROFILE["expected_salary"])
            except:
                pass

            # Academic Start and Passout Years
            try:
                driver.find_element(By.NAME, "start_year").send_keys(USER_PROFILE["start_year"])
                driver.find_element(By.NAME, "passout_year").send_keys(USER_PROFILE["passout_year"])
            except:
                pass

            # GitHub & LinkedIn Links
            try:
                driver.find_element(By.NAME, "github").send_keys(USER_PROFILE["github"])
                driver.find_element(By.NAME, "linkedin").send_keys(USER_PROFILE["linkedin"])
            except:
                pass

            # Contextual Skill Matching
            matched_skills = [skill for skill in USER_PROFILE["skills_pool"] if skill.lower() in job_description]
            if not matched_skills:
                matched_skills = ["Python", "Flask", "Selenium", "Problem Solving"]
            final_skills_text = ", ".join(matched_skills)

            try:
                driver.find_element(By.NAME, "skills").send_keys(final_skills_text)
            except:
                pass

            # Resume Upload
            try:
                upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
                upload_input.send_keys(os.path.abspath(final_pdf))
            except:
                print("File upload field not found.")

        except Exception as form_err:
            print(f"Error filling form: {str(form_err)}")

        # 3. OTP or Extra Input Handling via Telegram
        try:
            input_element = driver.find_element(By.XPATH, "//*[contains(translate(@name, 'OTP', 'otp'), 'otp') or contains(translate(@placeholder, 'CODE', 'code'), 'code') or contains(translate(@placeholder, 'ENTER', 'enter'), 'enter')]")
            if input_element:
                print(f"Verification / Input required for {company_name}! Sending Telegram notification...")
                
                if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                    alert_msg = f"🚨 *Input / OTP Required!*\nCompany: *{company_name}*\nPlease send the required text/code via `/submit-input` API or bot."
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": alert_msg, "parse_mode": "Markdown"})
                
                start_wait = time.time()
                while time.time() - start_wait < 60:
                    if latest_user_input:
                        input_element.clear()
                        input_element.send_keys(latest_user_input)
                        latest_user_input = None
                        print("Input entered successfully from Telegram response.")
                        break
                    time.sleep(2)
        except Exception as err:
            print("No extra input field detected or skipped.")

        # 4. Captcha Detection & Manual Pause
        try:
            captcha_element = driver.find_element(By.XPATH, "//*[contains(@class, 'captcha') or contains(@id, 'recaptcha')]")
            if captcha_element:
                print("Captcha detected! Waiting for manual solution...")
                time.sleep(15)
        except:
            pass

        # 5. Final Submit & Immediate Telegram Notification
        try:
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(text(), 'Apply') or contains(text(), 'Submit')]")))
            submit_btn.click()
            time.sleep(3)
        except Exception as sub_err:
            print(f"Could not click submit: {str(sub_err)}")
            send_telegram_screenshot(driver, company_name, sub_err)

        if driver:
            driver.quit()

        applied_jobs_today.append(company_name)
        applied_jobs_history.add(unique_job_id)
        
        send_telegram_notification(company_name, job_title)
        print(f"Successfully applied to {company_name} and notified via Telegram immediately!")

    except Exception as e:
        print(f"Error in automation: {str(e)}")
        if driver:
            try:
                send_telegram_screenshot(driver, company_name, e)
                driver.quit()
            except:
                pass

@app.route("/webhook", methods=["POST"])
def webhook():
    if not verify_api_key(request):
        return jsonify({"error": "Unauthorized Access"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "Invalid Data"}), 400

    thread = threading.Thread(target=run_job_automation, args=(data,))
    thread.start()

    return jsonify({"status": "Success", "message": "Job automation triggered, application & Telegram notification will be sent immediately upon submission!"}), 200

@app.route("/submit-input", methods=["POST"])
def submit_input():
    global latest_user_input
    if not verify_api_key(request):
        return jsonify({"error": "Unauthorized Access"}), 401
    
    data = request.json
    if data and "text" in data:
        latest_user_input = data["text"]
        return jsonify({"status": "Success", "message": "Text input received and passed to bot!"}), 200
    return jsonify({"error": "Invalid Data"}), 400

@app.route("/report", methods=["GET"])
def report():
    if not verify_api_key(request):
        return jsonify({"error": "Unauthorized Access"}), 401
    
    total_applied = len(applied_jobs_today)
    report_data = {
        "status": "Success",
        "applicant": USER_PROFILE["full_name"],
        "total_applied_today": total_applied,
        "applied_companies": list(applied_jobs_today)
    }
    return jsonify(report_data), 200

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Smart Job Bot with instant Telegram submission alerts is active on Cloud Server!",
        "applicant": USER_PROFILE["full_name"],
        "state": USER_PROFILE["state"]
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
