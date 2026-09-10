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
    if not data or "url" not in data:
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
        "status": "Smart Job Bot with instant Telegram submission alerts is active on MacBook localhost!",
        "applicant": USER_PROFILE["full_name"],
        "state": USER_PROFILE["state"]
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
                
