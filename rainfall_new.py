#!/usr/bin/env python
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def login_navigate_and_capture_targets():
    # Set up Firefox driver (headless mode is optional)
    options = Options()
    options.headless = True  # Enables headless mode
    options.add_argument("--headless")  # Extra enforcement
    options.headless = True  # Change to False for debugging (visible browser)
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    

    target_images = {"1630": False, "1700": False}#ADJUST TO LOCAL TIME 0700/5 & 0800/5
    max_attempts = 50
    attempt = 0

    # Function to download an image using requests with cookies from Selenium.
    def download_image(img_url, target_time):
        # Ensure the URL is absolute.
        if not img_url.startswith("http"):
            img_url = "https://www.metweb.ie" + img_url
        print(f"Downloading image for time {target_time} from: {img_url}")
        
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])
        response = session.get(img_url)
        if response.status_code == 200:
            filename = os.path.join(os.getcwd(), f"rainfall_radar_{target_time}.png")
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Image for {target_time} saved as: {filename}")
        else:
            print(f"Failed to download image for {target_time}. HTTP status code: {response.status_code}")

    try:
        # ------------------
        # Login Section
        # ------------------
        driver.get("https://www.metweb.ie/login")
        time.sleep(2)
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys("FTSOPS")
        password_field.send_keys("FTSWX")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(5)
        print("Logged in. Page title:", driver.title)
        
        # ------------------
        # Navigation Section
        # ------------------
        driver.get("https://www.metweb.ie/home-page")
        time.sleep(3)
        print("Navigated to home page. Current URL:", driver.current_url)
        
        # Click the "Observations" dropdown menu using JavaScript click
        obs_xpath = "/html/body/div[2]/header/div/nav[2]/ul/li[2]/a"
        observations_button = driver.find_element(By.XPATH, obs_xpath)
        driver.execute_script("arguments[0].scrollIntoView(true);", observations_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", observations_button)
        time.sleep(3)
        print("Clicked Observations dropdown.")
        
        # Click the "Radar" button from the dropdown
        radar_xpath = "/html/body/div[2]/header/div/nav[2]/ul/li[2]/ul/li[3]"
        radar_button = driver.find_element(By.XPATH, radar_xpath)
        driver.execute_script("arguments[0].scrollIntoView(true);", radar_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", radar_button)
        time.sleep(3)
        print("Clicked Radar button.")
        
        # Click the "(5min): IRE" button from the expanded Radar menu
        ire_xpath = "/html/body/div[2]/header/div/nav[2]/ul/li[2]/ul/li[3]/ul/li[1]/a"
        ire_button = driver.find_element(By.XPATH, ire_xpath)
        driver.execute_script("arguments[0].scrollIntoView(true);", ire_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", ire_button)
        time.sleep(5)
        print("Clicked (5min): IRE button.")
        
        # ------------------
        # Loop to Find Target Images
        # ------------------
        # XPath for the image element:
        image_xpath = "/html/body/div[2]/div[1]/div/div/div[2]/article/section/div[1]/img"
        next_button_xpath = "/html/body/div[2]/div[1]/div/div/div[2]/article/section/div[1]/form/input[6]"
        
        while attempt < max_attempts and not all(target_images.values()):
            attempt += 1
            try:
                image_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, image_xpath))
                )
            except TimeoutException:
                print(f"Attempt {attempt}: Timeout waiting for image element.")
                break
            
            img_src = image_element.get_attribute("src")
            print(f"Attempt {attempt}: Found image src: {img_src}")
            
            # Parse the timestamp from the src.
            # Expected format: ..._202504021705_RND.png
            parts = img_src.split("_")
            if len(parts) >= 2:
                timestamp = parts[-2]  # e.g., "202504021705"
                time_part = timestamp[-4:]  # e.g., "1705", "1630", etc.
                print(f"Extracted time part: {time_part}")
                
                # Check if this time is one of our targets and not yet captured.
                if time_part in target_images and not target_images[time_part]:
                    download_image(img_src, time_part)
                    target_images[time_part] = True
            else:
                print("Unexpected image src format.")
            
            # Click the "next" button to update the image
            try:
                next_button = driver.find_element(By.XPATH, next_button_xpath)
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
            except Exception as e:
                print("Error clicking next button:", e)
                break
        
        if all(target_images.values()):
            print("Successfully captured both target images: 1630 and 1700.")
        else:
            missing = [t for t, found in target_images.items() if not found]
            print("Did not capture target image(s) for:", missing)
            
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    login_navigate_and_capture_targets()
