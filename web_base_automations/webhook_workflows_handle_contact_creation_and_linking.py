from datetime import datetime
import sys
import time
from utils import  login
from webdriver_configration import driver_confrigration
from selenium.webdriver.common.by import By
import os
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


# Load environment variables from the .env file
load_dotenv()

# Access the google_credentials path from the .env file
GOHIGHLEVEL_EMAIL = os.getenv('KONNECTED_EMAIL')
GOHIGHLEVEL_PASSWORD = os.getenv('KONNECTED_PASSWORD')

WORKFLOW_LOCATION_IDS = os.getenv('WORKFLOW_LOCATION_IDS', '')
# Convert to a list (handles both single & multiple IDs)
WORKFLOW_LOCATION_IDS = [WORKFLOW_LOCATION_IDS] if ',' not in WORKFLOW_LOCATION_IDS else WORKFLOW_LOCATION_IDS.split(',')

BASE_URL = "https://app.konnectd.io/v2/location/{}/automation/"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logs_setup_file import setup_logging

module_name = os.path.splitext(os.path.basename(__file__))[0]

logger = setup_logging(module_name)
 
def navigate_to_marketing(driver):
    """Navigates to the Marketing section."""
    time.sleep(30)
    try:
        marketing = driver.find_element(By.ID, "sb_290bf469-c274-4a79-9482-701dd0a46cbc")
        marketing.click()
        logger.info("Clicked on Marketing.")
        time.sleep(5)
    except:
        logger.info("Marketing section not found.") 

def search_and_click(driver, search_text, search_xpath):
    """Searches for an item and clicks on it."""
    search_box = driver.find_element(By.CSS_SELECTOR, "input.n-input__input-el")
    search_box.send_keys(search_text)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)
    
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, search_xpath)))
    element.click()
    logger.info(f"Clicked on {search_text}.")
    time.sleep(10)
 
def copy_webhook_url(driver, input_id):
    """Copies the webhook URL from the input field."""
    input_field = driver.find_element(By.ID, input_id)
    webhook_url = input_field.get_attribute("value") 
    logger.info(f"Extracted Webhook URL: {webhook_url}")
    print(f"Webhook URL: {webhook_url}")
    time.sleep(5)
    return webhook_url

def paste_webhook_url(driver, input_id, webhook_url):
    """Directly sets the webhook URL into the input field."""
    input_field = driver.find_element(By.ID, input_id)
    input_field.clear() 
    input_field.send_keys(webhook_url)  
    logger.info(f"Pasted Webhook URL: {webhook_url}")  
    time.sleep(20)
    
def save_workflow(driver):
    """Saves the workflow."""
    driver.find_element(By.ID, "pg-actions__btn--save-action-webhook").click()
    logger.info("Workflow saved.")
    time.sleep(10)
    driver.find_element(By.ID, "cmp-header__btn--save-workflow").click()
    time.sleep(10)
    
def scrapping(location_id):
    """Main scraping function."""
    logger.info("Starting the scrapping process.")
    
    # Record the start time
    start_time = datetime.now()
    print("Script started at:", start_time)
    logger.info(f"Script started at: {start_time}")
    
    """Scrapes data for the given location ID."""
    driver = driver_confrigration(logger)
    
    login(driver,logger)
    
    url = BASE_URL.format(location_id.strip())  
    driver.get(url)
    
    logger.info(f"Navigated to {url}.")
    
    navigate_to_marketing(driver)
        
    popup = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, '//div[@class="popup--menu_list"]'))  # Modify this XPATH   
)
    popup_container = driver.find_element(By.CLASS_NAME, 'popup--menu_list')
    anchor_tags = popup_container.find_elements(By.TAG_NAME, 'a')
    desired_link = anchor_tags[2]
    desired_link.click()
    
    logger.info("tag clicked successfully")
    time.sleep(10)
    driver.switch_to.frame("workflow-builder")
    time.sleep(10)
    
    search_box = driver.find_element(By.CSS_SELECTOR, "input.n-input__input-el")
    search_box.send_keys("webhooks")
    search_box.send_keys(Keys.ENTER)      
    logger.info("searching succesfully in search bar")
    time.sleep(10)
    
    webhooks_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(., 'Webhooks')]"))
    )
    webhooks_element.click()
    logger.info("clicked on webhook element ")
    
    time.sleep(5)
    
    webhooks_current_url = driver.current_url
    logger.info(f"Current URL:--- {webhooks_current_url}")

    search_and_click(driver, "Seller Agent Contact Creation", "//span[contains(., '*Seller Agent Contact Creation')]")
    
    driver.refresh()
    time.sleep(25)
    driver.switch_to.frame('workflow-builder')
    logger.info("successfully switched into iframe")
    time.sleep(10)

    zoom_out_button = driver.find_element(By.ID, "workflow-zoom-out")
    for _ in range(3):
        zoom_out_button.click()
    time.sleep(10)
    logger.info("zoom out successfully")
    inbound_webhook = driver.find_element(By.XPATH, "//*[@id='main']/div[1]/div/div[1]/div/div/div[2]/div[5]/div/div/div/div/div[2]")
    inbound_webhook.click()
    logger.info("inbound webhook click successfully")
    time.sleep(20)
    
    webhook_url = copy_webhook_url(driver, "trgr-inbound-webhook__text--url")
      
    driver.get(webhooks_current_url)
     
    logger.info("start script  for Seller Agent Fields changed")
    
    time.sleep(35)
    driver.switch_to.frame('workflow-builder')
    logger.info("successfully switched into iframe")
    time.sleep(10)
    
    search_and_click(driver, "Seller Agent Fields changed", "//span[contains(., '*Seller Agent Fields changed')]")
      
    driver.refresh()
    time.sleep(30)
    driver.switch_to.frame('workflow-builder')
    logger.info("successfully switched into iframe")
    time.sleep(25)

    zoom_out_button = driver.find_element(By.ID, "workflow-zoom-out")
    for _ in range(6):
        zoom_out_button.click()
        time.sleep(1)
        
    time.sleep(10)
    logger.info("zoom out successfully")
    webhook = driver.find_element(By.XPATH, "//*[@id='main']/div[1]/div/div[1]/div/div/div[2]/div[10]/div/div[1]/div[1]")
    webhook.click()
    
    time.sleep(25)
    
    paste_webhook_url(driver, "webhook-url", webhook_url)  
    save_workflow(driver) 
    
    logger.info("Process is successfully completed")
    print("Process is successfully completed")
    
    driver.quit()
    
# Run the scrapping function for each location ID
for location_id in WORKFLOW_LOCATION_IDS:
    if location_id.strip():  # Ignore empty values
        scrapping(location_id)


