import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from speak import speak
from listen import listen

def try_to_click(driver, by, identifier, name):
    try:
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((by, identifier))
        )
        speak(f"Should I {name}?")
        for _ in range(2):
            response = listen()
            if response and ("yes" in response.lower() or "confirm" in response.lower()):
                button.click()
                speak(f"{name.capitalize()} clicked.")
                return True
            elif response and ("no" in response.lower() or "cancel" in response.lower()):
                speak("Action cancelled.")
                return False
            else:
                speak("Sorry, I didn't catch that. Please say yes or no.")
        speak("No clear response. Skipping.")
        return False
    except Exception:
        return False

def confirm_and_request_ride(driver):
    success = False

    # 1. Try the main request button (if visible)
    success |= try_to_click(
        driver,
        By.XPATH,
        '//*[@id="wrapper"]/div[1]/div[3]/main/div/section/div[3]/div/div/button',
        "request the ride"
    )

    time.sleep(2)

    # 2. If fare confirmation popup appears, handle it
    try:
        confirm_button = driver.find_element(By.CSS_SELECTOR, 'button.css-lmEOwb')
        cancel_button = driver.find_element(By.CSS_SELECTOR, 'button.css-kcHUdO')

        speak("The fare has changed. Should I confirm the new fare?")
        for _ in range(2):
            response = listen()
            if response and ("yes" in response.lower() or "confirm" in response.lower()):
                confirm_button.click()
                speak("Fare confirmed.")
                success = True
                break
            elif response and ("no" in response.lower() or "cancel" in response.lower()):
                cancel_button.click()
                speak("Cancelled as requested.")
                return
            else:
                speak("Sorry, please say yes or no.")
        else:
            speak("No clear response. Skipping fare confirmation.")

    except NoSuchElementException:
        pass  # No fare popup appeared

    # 3. Try the expired fare page's request button (if it appears later)
    time.sleep(2)
    success |= try_to_click(
        driver,
        By.XPATH,
        '//*[@id="wrapper"]/div[2]/div/div[2]/div/div/div/div/div/div/div[3]/div[2]/button',
        "confirm and request the ride"
    )

    if success:
        speak("Your ride has been requested.")
    else:
        speak("I did not request the ride, as the buttons were missing or not confirmed.")

