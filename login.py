from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

# === Check if user is already logged in ===
def is_logged_in(driver):
    try:
        # Mobile: if "Login" button is present, user is NOT logged in
        driver.find_element(By.CSS_SELECTOR, "button.css-dHHA-DQ")
        return False
    except NoSuchElementException:
        return True

# === Click login button if needed ===
def click_login_button(driver, speak_func):
    if is_logged_in(driver):
        speak_func("You're already logged in. Skipping login.")
        return

    speak_func("It looks like you're not logged in yet. Please log in manually.")

    try:
        login_btn = driver.find_element(By.CSS_SELECTOR, "button.css-dHHA-DQ")
        driver.execute_script("arguments[0].click();", login_btn)
    except Exception as e:
        print(f"⚠️ Failed to click login button: {e}")
        speak_func("Couldn't click the login button. Please try manually.")

    # Wait for manual login
    for i in range(60):
        if is_logged_in(driver):
            speak_func("Login detected. You're now logged in.")
            return
        time.sleep(2)

    speak_func("Login not detected within time. Please try again.")
