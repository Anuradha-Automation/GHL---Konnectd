import os
import sys
from selenium.webdriver.support import expected_conditions as EC
from urls import WEBSITE_URL
import time
from login_with_google_api import otp_get_from
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()

# Access the google_credentials path from the .env file
GOHIGHLEVEL_EMAIL = os.getenv('KONNECTED_EMAIL')
GOHIGHLEVEL_PASSWORD = os.getenv('KONNECTED_PASSWORD')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from logs_setup_file import setup_logging

# module_name = os.path.splitext(os.path.basename(__file__))[0]

# logger = setup_logging(module_name)

def login(driver ,logger):
    """Logs into the website."""
    driver.get(WEBSITE_URL)
    logger.info(f"Navigated to {WEBSITE_URL}.")
    time.sleep(20)
    driver.find_element(By.ID, 'email').send_keys(GOHIGHLEVEL_EMAIL)
    driver.find_element(By.ID, 'password').send_keys(GOHIGHLEVEL_PASSWORD)
   
    logger.info("Entered credentials.")
    
    driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[4]/section/div[2]/div/div/div/div[4]/div/button').click()
    logger.info("Clicked on login button.")
    time.sleep(5)
    
    driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[4]/section/div[2]/div/div/div/div[3]/div/button').click()
    logger.info("Sent security code.")
    time.sleep(40)
    
    logger.info("Waiting for OTP.")
    
    # Uncomment and integrate OTP processing as needed
    security_code = otp_get_from(logger)
    time.sleep(10)
    logger.info(f"OTP fetched successfully: {security_code}")
    otp_digits = list(str(security_code))
    otp_inputs = driver.find_elements(By.CLASS_NAME, "otp-input")

    for i in range(len(otp_digits)):
        otp_inputs[i].send_keys(otp_digits[i])

    print("OTP Entered Successfully!")
    
    time.sleep(60)
    
    logger.info("Login successful.")   