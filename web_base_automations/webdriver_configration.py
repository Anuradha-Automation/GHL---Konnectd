import os
import sys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from logs_setup_file import setup_logging

# module_name = os.path.splitext(os.path.basename(__file__))[0]

# logger = setup_logging(module_name)
# def driver_confrigration():
#     options = webdriver.ChromeOptions()
#     options.add_argument("--disable-notifications")
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-popup-blocking")
#     # options.add_argument("--headless")
    
#     # Use Service for ChromeDriverManager
#     service = Service(ChromeDriverManager().install())
    
#     # Pass options and service to Chrome WebDriver
#     driver = webdriver.Chrome(service=service, options=options)
#     return driver



# FOR DOCKER------------------------------------------------------------

def driver_confrigration(logger):
    # Set Chrome options
    logger.info("driver function calll ")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument("--remote-debugging-port=9222") 
    service = Service(executable_path="/home/ubuntu/chromedriver-linux64/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(180)  # Set a longer timeout for page load
    driver.set_script_timeout(180)
    logger.info("driver intialize successfully")
    return driver
