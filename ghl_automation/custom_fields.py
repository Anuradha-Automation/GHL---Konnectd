import os
import sys
import requests
import json
import time
import psycopg2
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Get API base URL, API key, and DB connection details from environment variables
API_BASE_URL = os.getenv('API_BASE_URL')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', 5432)  # Default PostgreSQL port
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
SUB_ACNT_API_KEYS = "SUB_ACNT_API_KEYS"

def get_env_list(key: str):
    """Reads an environment variable and splits it into a list if multiple values are present."""
    value = os.getenv(key, "")
    return [v.strip() for v in value.split(",") if v.strip()]

# Get logger instance (assumed to be a custom logger)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logs_setup_file import setup_logging

module_name = os.path.splitext(os.path.basename(__file__))[0]

logger = setup_logging(module_name)

# Function to get DB connection
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Function to insert or update custom fields in the PostgreSQL database
def upsert_custom_fields_to_db(custom_fields):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_fields (
                id VARCHAR PRIMARY KEY,
                name VARCHAR,
                field_key VARCHAR,
                placeholder VARCHAR,
                position INT,
                dataType VARCHAR,
                picklist_options TEXT
            );
        """)

        # Insert or update each custom field
        for field in custom_fields:
            field_id = field.get('id')
            logger.info(f"Processing custom field ID: {field_id}")

            # Map the fields from custom_field to the schema
            name = field.get('name')
            field_key = field.get('fieldKey')
            placeholder = field.get('placeholder')
            position = field.get('position')
            date_type = field.get('dataType')
            picklist_options = json.dumps(field.get('picklistOptions'))  # Store as JSON

            # Check if the custom field already exists
            cursor.execute("SELECT COUNT(*) FROM custom_fields WHERE id = %s", (field_id,))
            exists = cursor.fetchone()[0]

            if exists:
                # Update the existing custom field
                cursor.execute("""
                    UPDATE custom_fields SET name = %s, field_key = %s, placeholder = %s, 
                    position = %s, dataType = %s, picklist_options = %s
                    WHERE id = %s
                """, (
                    name, field_key, placeholder, position, date_type, picklist_options, field_id
                ))
                logger.info(f"Custom field ID {field_id} updated.")
            else:
                # Insert a new custom field if it doesn't exist
                cursor.execute("""
                    INSERT INTO custom_fields (id, name, field_key, placeholder, position, 
                    dataType, picklist_options)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    field_id, name, field_key, placeholder, position, date_type, picklist_options
                ))
                logger.info(f"Custom field ID {field_id} inserted.")

        conn.commit()
        logger.info("Custom field data processed successfully!")

    except Exception as e:
        logger.error(f"Error upserting custom field data into DB: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Function to fetch custom fields from GoHighLevel API with retries
def fetch_with_retry(url,headers, retries=3, delay=5):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, headers=headers, timeout=30000)  # Increased timeout
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Attempt {attempt + 1} failed with status {response.status_code}. Retrying in {delay} seconds...")
                time.sleep(delay)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            logger.error(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
        attempt += 1
    logger.error("Max retries reached. Exiting.")
    return None

# Function to fetch all custom fields
def get_all_custom_fields():
    custom_fields_list = []
    # Set headers for API request
    sub_acnt_api_keys = get_env_list(SUB_ACNT_API_KEYS)
    print(sub_acnt_api_keys)
    for sub_acnt_api_key in sub_acnt_api_keys:

        headers = {
        'Authorization': f'Bearer {sub_acnt_api_key}',
        'Content-Type': 'application/json'
        }

        url = f"{API_BASE_URL}/custom-fields/"
        
        data = fetch_with_retry(url,headers)
        
        if data:
            custom_fields = data.get('customFields', [])
            custom_fields_list.extend(custom_fields)
            upsert_custom_fields_to_db(custom_fields)  # Insert/update custom fields in DB

    return custom_fields_list

# Fetch all custom fields
all_custom_fields = get_all_custom_fields()

# Display total custom fields fetched
if all_custom_fields:
    logger.info(f"\nTotal custom fields fetched: {len(all_custom_fields)}")
    logger.info(f"Sample custom fields: {json.dumps(all_custom_fields[:5], indent=4)}")  # Show first 5 custom fields as a sample
else:
    logger.error("No custom fields found.")
