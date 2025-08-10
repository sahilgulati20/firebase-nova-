from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
import datetime
import random
import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from login import click_login_button
from location import enter_location_details
from options import read_ride_options
from confirm_and_request import confirm_and_request_ride

# === FIREBASE SETUP ===
import firebase_admin
from firebase_admin import credentials, firestore

# Path to your Firebase service account key JSON
# FIREBASE_CRED_PATH = "serviceAccountKey.json"
FIREBASE_CRED_PATH = "C:\\Users\\gulat\\OneDrive\\Desktop\\firebase nova\\nova-agentic-ai\\serviceAccountKey.json"


if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# === COOKIE FUNCTIONS ===
def save_cookies_to_firebase(user_id, driver):
    try:
        cookies = driver.get_cookies()
        db.collection("uber_cookies").document(user_id).set({"cookies": cookies})
        print(f"✅ Cookies saved for {user_id}")
    except Exception as e:
        print(f"⚠️ Failed to save cookies: {e}")

def load_cookies_from_firebase(user_id, driver):
    try:
        doc = db.collection("uber_cookies").document(user_id).get()
        if doc.exists:
            cookies = doc.to_dict().get("cookies", [])
            driver.get("https://m.uber.com/go/home")
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    pass
            driver.refresh()
            print(f"✅ Cookies loaded for {user_id}")
            return True
        else:
            print(f"⚠️ No cookies found for {user_id}")
            return False
    except Exception as e:
        print(f"⚠️ Failed to load cookies: {e}")
        return False

# === SPEAK FUNCTION ===
def nova_speak(text):
    print(f"\n🔊 Nova: {text}")
    tts = gTTS(text=text, lang='en')
    filename = f"nova_{random.randint(1000,9999)}.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

# === LISTEN FUNCTION ===
def nova_listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as mic:
        print("🎙️ Listening...")
        recognizer.adjust_for_ambient_noise(mic)
        try:
            audio = recognizer.listen(mic, timeout=8, phrase_time_limit=10)
            query = recognizer.recognize_google(audio, language='en-IN')
            print(f"🗣️ You said: {query}")
            return query.lower()
        except sr.WaitTimeoutError:
            print("⏱️ No response detected.")
            return ""
        except:
            nova_speak("Sorry, I didn't understand.")
            return ""

# === GREETING ===
def get_time_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

# === INTRODUCTION ===
def nova_intro():
    messages = [
        "Hello, I'm NovaCab. Your voice is my command.",
        "I'm Nova, designed by Sahil to assist you with cabs and conversation.",
        "Nova here! Ready to make your travels smooth and easy."
    ]
    nova_speak(random.choice(messages))

# === SLEEP MODE ===
def sleep_mode():
    nova_speak("Entering sleep mode. Say 'wake up Nova' when you're ready.")
    while True:
        cmd = nova_listen()
        if "wake up nova" in cmd or ("wake" in cmd and "nova" in cmd):
            nova_speak("Nova is awake and ready.")
            break

# === OPEN UBER WITH COOKIE PERSISTENCE ===
def open_uber_with_persistence():
    nova_speak("Opening Uber mobile website. Please wait...")

    try:
        user_id = "test_user"  # Replace with unique ID for each user if needed

        options = uc.ChromeOptions()
        options.add_argument(
            "user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 "
            "Mobile/15E148 Safari/604.1"
        )
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(version_main=138, options=options)
        driver.set_window_size(420, 900)

        # Try to load cookies from Firebase
        cookies_loaded = load_cookies_from_firebase(user_id, driver)

        if not cookies_loaded:
            # First time login
            driver.get("https://m.uber.com/go/home")
            click_login_button(driver, nova_speak)

            nova_speak("Please log in to Uber manually. I will save your login for future use.")
            time.sleep(25)  # Give user time to log in (adjust as needed)

            save_cookies_to_firebase(user_id, driver)

        enter_location_details(driver, nova_speak, nova_listen)
        read_ride_options(driver)
        confirm_and_request_ride(driver)

    except Exception as e:
        print(f"⚠️ Error: {e}")
        nova_speak("Failed to open Uber mobile website.")

# === COMMAND HANDLER ===
def handle_command(cmd):
    if "introduce" in cmd or "who are you" in cmd:
        nova_intro()
    elif "sleep" in cmd:
        sleep_mode()
    elif "exit" in cmd or "quit" in cmd:
        nova_speak("Goodbye. Nova signing off.")
        return False
    elif "book a cab" in cmd or "open uber" in cmd:
        open_uber_with_persistence()
    else:
        nova_speak("I didn't catch that.")
    return True

# === ASSISTANT LOOP ===
def nova_loop():
    nova_speak("Nova is standing by. Say 'wake up Nova' to begin.")
    awake = False

    while True:
        command = nova_listen()
        if not awake:
            if "wake up nova" in command or ("wake" in command and "nova" in command):
                awake = True
                nova_speak(get_time_greeting())
                continue
            else:
                continue

        if not handle_command(command):
            break

# === START NOVA ===
if __name__ == "__main__":
    nova_loop()
