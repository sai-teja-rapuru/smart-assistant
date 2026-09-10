        if any(keyword in job_description for keyword in fee_keywords):
            print(f"Skipping job because it asks for money/fee: {company_name}")
            return

        # --- IT FRESHERS & IT ROLES FILTER RULE (Restored safely) ---
        it_keywords = ["python", "software", "developer", "engineer", "java", "data", "analyst", "IT", "programmer", "cse", "apply"]
        is_it_role = any(keyword in job_description or keyword in job_title.lower() for keyword in it_keywords)
        is_fresher_role = ("fresher" in job_description) or ("0-1" in job_description) or ("entry" in job_description) or ("trainee" in job_description) or ("experience" not in job_description) or True

        if not is_it_role:
            print(f"Skipping non-IT role for: {company_name} ({job_title})")
            return

        pdf_path = "resume.pdf"
        if not os.path.exists(pdf_path):
            print("Warning: resume.pdf not found locally! Please ensure resume.pdf is placed in the project directory.")
        
        final_pdf = compress_pdf(pdf_path)

        # Selenium Browser Initialization (MacBook M5 / Cloud optimized)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Enabled for seamless server/cloud execution
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
        
        driver.get(job_link)
        wait = WebDriverWait(driver, 15)
        
        # --- ఇక్కడ మెయిల్ బటన్ క్లిక్ చేసిన తర్వాత వచ్చే పేజీలో 'Apply' బటన్‌ని వెతికి క్లిక్ చేసే లాజిక్ ---
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
            # Name & Email Fields
            wait.until(EC.presence_of_element_located((By.NAME, "firstname"))).send_keys(USER_PROFILE["first_name"])
            try:
                driver.find_element(By.NAME, "middlename").send_keys(USER_PROFILE["middle_name"])
            except:
                pass
            driver.find_element(By.NAME, "lastname").send_keys(USER_PROFILE["last_name"])
            driver.find_element(By.NAME, "email").send_keys(USER_PROFILE["email"])
            
            # --- State Selection ---
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

            # --- Gender Selection ---
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

            # --- Citizenship / Nationality Selection ---
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

            # --- Address Entry ---
            try:
                driver.find_element(By.NAME, "address").send_keys(USER_PROFILE["address"])
            except:
                try:
                    driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Address') or contains(@name, 'location') or contains(@name, 'addr')]").send_keys(USER_PROFILE["address"])
                except:
                    pass

            # --- Pincode Entry ---
            try:
                driver.find_element(By.NAME, "pincode").send_keys(USER_PROFILE["pincode"])
            except:
                try:
                    driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Pin') or contains(@placeholder, 'Postal') or contains(@name, 'zip') or contains(@name, 'pincode')]").send_keys(USER_PROFILE["pincode"])
                except:
                    pass

            # --- Phone Number & Country Code ---
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

            # --- Country Selection ---
            try:
                country_element = driver.find_element(By.NAME, "country")
                if country_element.tag_name == "select":
                    Select(country_element).select_by_visible_text(USER_PROFILE["country"])
                else:
                    country_element.send_keys(USER_PROFILE["country"])
            except:
                pass

            # --- Relocation Question Handling (Yes) ---
            try:
                relocate_element = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'RELOCATE', 'relocate'), 'relocate') or contains(translate(@name, 'RELOCATE', 'relocate'), 'relocate')]")
                if relocate_element:
                    if relocate_element.tag_name == "select":
                        Select(relocate_element).select_by_visible_text("Yes")
                    else:
                        relocate_element.send_keys(USER_PROFILE["relocate"])
            except:
                pass

            # --- Passport Question (No) ---
            try:
                passport_element = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'PASSPORT', 'passport'), 'passport') or contains(translate(@name, 'PASSPORT', 'passport'), 'passport')]")
                if passport_element:
                    if passport_element.tag_name == "select":
                        Select(passport_element).select_by_visible_text("No")
                    else:
                        passport_element.send_keys(USER_PROFILE["passport"])
            except:
                pass

            # --- University Selection (JNTUA) ---
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

            # --- Academic Start and Passout Years ---
            try:
                driver.find_element(By.NAME, "start_year").send_keys(USER_PROFILE["start_year"])
                driver.find_element(By.NAME, "passout_year").send_keys(USER_PROFILE["passout_year"])
            except:
                pass

            # --- GitHub & LinkedIn Links ---
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

        driver.quit()

        applied_jobs_today.append(company_name)
        applied_jobs_history.add(unique_job_id)
        
        # సబ్మిట్ అయిన వెంటనే టెలిగ్రామ్‌కి ఇన్‌స్టంట్ అలర్ట్ వెళ్తుంది
        send_telegram_notification(company_name, job_title)
        print(f"Successfully applied to {company_name} and notified via Telegram immediately!")

    except Exception as e:
        print(f"Error in automation: {str(e)}")

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
            
