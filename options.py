from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from gtts import gTTS
import os
from playsound import playsound
import time
import speech_recognition as sr

def nova_speak(text):
    tts = gTTS(text=text, lang='en')
    filename = "ride_options.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

def listen_to_user():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            print("🎙️ Listening...")
            audio = recognizer.listen(source)
            try:
                user_input = recognizer.recognize_google(audio)
                print(f"🗣️ You said: {user_input}")
                return user_input.lower()
            except sr.UnknownValueError:
                print("❌ Couldn't understand audio")
                nova_speak("Sorry, I didn't catch that. Please say it again.")
            except sr.RequestError:
                print("❌ Speech recognition service failed")
                nova_speak("There was a problem with speech recognition.")
                return None

def read_ride_options(driver):
    try:
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-testid='product_selector.list_item']")))

        ride_blocks = driver.find_elements(By.CSS_SELECTOR, "li[data-testid='product_selector.list_item']")

        if not ride_blocks:
            nova_speak("Sorry, I couldn't find any ride options.")
            return

        ride_options = []
        ride_names = []

        for ride in ride_blocks:
            text = ride.text.strip()
            if text:
                ride_options.append(text)

        refined_options = []
        for raw_text in ride_options:
            lines = raw_text.split("\n")
            ride_name = None
            price = None

            for line in lines:
                if not ride_name:
                    ride_name = line.strip()
                elif "₹" in line:
                    price = line.strip()
                    break

            if ride_name and price:
                ride_names.append(ride_name.lower())
                refined_options.append(f"{ride_name} for {price}")

        for idx, option in enumerate(refined_options, 1):
            message = f"Ride {idx}: {option}"
            print(f"🔹 {message}")
            nova_speak(message)
            time.sleep(1)

        # Loop to ask for ride selection until successful
        while True:
            nova_speak("Which ride would you like to choose?")
            user_choice = listen_to_user()
            if not user_choice:
                continue

            matched_index = None
            for idx, ride_name in enumerate(ride_names):
                if ride_name in user_choice or user_choice in ride_name:
                    matched_index = idx
                    break

            if matched_index is not None:
                selected_ride = ride_names[matched_index]
                ride_blocks[matched_index].click()
                print(f"✅ '{selected_ride}' ride selected!")
                nova_speak(f"{selected_ride} selected!")

                # Ask for confirmation to request the ride
                nova_speak("Do you want to confirm and request this ride?")
                confirmation = listen_to_user()

                if confirmation and ("yes" in confirmation or "confirm" in confirmation):
                    try:
                        request_buttons = driver.find_elements(
                            By.XPATH, '//*[@id="wrapper"]/div[1]/div[3]/main/div/section/div[3]/div/div/button'
                        )
                        for btn in request_buttons:
                            if btn.is_displayed() and btn.is_enabled():
                                btn.click()
                                print("✅ Request button clicked!")
                                nova_speak("Ride request sent.")
                                break
                        else:
                            print("ℹ️ Optional request button not found.")

                        # Wait for possible confirmation pop-up
                        time.sleep(2)

                        # Check for confirm/cancel popup
                        confirm_xpath = '//*[@id="wrapper"]/div[2]/div/div[2]/div/div/div/div/div/div/div[3]/div[2]/button'
                        cancel_xpath = '//*[@id="wrapper"]/div[2]/div/div[2]/div/div/div/div/div/div/div[3]/div[1]/button'
                        confirm_buttons = driver.find_elements(By.XPATH, confirm_xpath)

                        if confirm_buttons:
                            nova_speak("Do you want to confirm the booking?")
                            final_confirm = listen_to_user()
                            if final_confirm and ("yes" in final_confirm or "confirm" in final_confirm):
                                try:
                                    driver.find_element(By.XPATH, confirm_xpath).click()
                                    print("✅ Final confirm button clicked.")
                                    nova_speak("Your ride is confirmed.")
                                except Exception as e:
                                    print("❌ Error clicking confirm:", e)
                                    nova_speak("Failed to confirm the booking.")
                            else:
                                try:
                                    driver.find_element(By.XPATH, cancel_xpath).click()
                                    print("❌ Final booking cancelled.")
                                    nova_speak("Booking cancelled as requested.")
                                except Exception as e:
                                    print("❌ Error clicking cancel:", e)
                                    nova_speak("Could not cancel the ride.")
                    except Exception as e:
                        print("❌ Could not click the request button:", e)
                        nova_speak("Sorry, I could not click the request button.")
                else:
                    nova_speak("Okay, ride request cancelled.")
                return
            else:
                nova_speak("Sorry, I couldn't find the ride you asked for. Please say it again.")

    except Exception as e:
        print(f"❌ Failed to read ride options: {e}")
        nova_speak("I couldn't read the ride options. Please try again.")
