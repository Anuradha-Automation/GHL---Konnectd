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
API_KEY = os.getenv('API_KEY')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', 5432)  # Default PostgreSQL port
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
# SUB_ACNT_API_KEYS = os.getenv('SUB_ACNT_API_KEYS')
SUB_ACNT_API_KEYS ="SUB_ACNT_API_KEYS"



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

# Function to insert or update contacts into the PostgreSQL database
# Function to insert or update contacts and custom fields into the PostgreSQL database
def upsert_contact_to_db(contacts):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for contact in contacts:
            if isinstance(contact, dict):  # Ensure contact is a dictionary
                contact_id = contact.get('id')
                logger.info(f"Processing contact ID: {contact_id}")
                
                # Map the fields from contact to the schema
                location_id = contact.get('locationId')
                first_name = contact.get('firstName')
                last_name = contact.get('lastName')
                email = contact.get('email')
                company_name = contact.get('companyName')
                phone = contact.get('phone')
                assigned_to = contact.get('assignedTo')
                address1 = contact.get('address1')
                city = contact.get('city')
                state = contact.get('state')
                country = contact.get('country')
                postal_code = contact.get('postalCode')
                website = contact.get('website')
                date_of_birth = contact.get('dateOfBirth')
                
                # Check if the contact already exists
                cursor.execute("SELECT COUNT(*) FROM contact WHERE id = %s", (contact_id,))
                exists = cursor.fetchone()[0]

                if exists:
                    # Update the existing contact
                    cursor.execute("""UPDATE contact SET location_id = %s, first_name = %s, last_name = %s, 
                        email = %s, company_name = %s, phone = %s, assigned_to = %s, 
                        address1 = %s, city = %s, state = %s, country = %s, postal_code = %s,
                        website = %s, date_of_birth = %s
                        WHERE id = %s""", (
                        location_id,
                        first_name,
                        last_name,
                        email,
                        company_name,
                        phone,
                        assigned_to,
                        address1,
                        city,
                        state,
                        country,
                        postal_code,
                        website,
                        date_of_birth,
                        contact_id
                    ))
                    logger.info(f"Contact ID {contact_id} updated.")
                else:
                    # Insert a new contact if it doesn't exist
                    cursor.execute("""INSERT INTO contact (id, location_id, first_name, last_name, email, 
                        company_name, phone, assigned_to, address1, city, state, country, postal_code, 
                        website, date_of_birth) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
                        contact_id,
                        location_id,
                        first_name,
                        last_name,
                        email,
                        company_name,
                        phone,
                        assigned_to,
                        address1,
                        city,
                        state,
                        country,
                        postal_code,
                        website,
                        date_of_birth
                    ))
                    logger.info(f"Contact ID {contact_id} inserted.")

                # Now handle inserting the custom fields
                custom_fields = contact.get('customField', [])
                for field in custom_fields:
                    custom_field_id = field.get('id')
                    custom_field_value = field.get('value')
                    # Check if the custom_field_id already exists for the contact_id
                    cursor.execute("""SELECT COUNT(*) FROM contact_custom_fields 
                                      WHERE contact_id = %s AND custom_field_id = %s""", 
                                      (contact_id, custom_field_id))
                    exists_custom_field = cursor.fetchone()[0]
                    
                    if not exists_custom_field:
                        # Insert custom field if it doesn't already exist
                        cursor.execute("""INSERT INTO contact_custom_fields (contact_id, custom_field_id, value) 
                                          VALUES (%s, %s, %s)""", (contact_id, custom_field_id, custom_field_value))
                        logger.info(f"Inserted custom field ID {custom_field_id} for contact ID {contact_id}.")
                    else:
                        logger.info(f"Custom field ID {custom_field_id} already exists for contact ID {contact_id}. Skipping insert.")
        
        conn.commit()
        logger.info("Contact and custom field data processed successfully!")

    except Exception as e:
        logger.error(f"Error upserting contact data into DB: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Function to fetch contacts with retries
def fetch_with_retry(url,headers, retries=3, delay=5):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, headers=headers, timeout=30000)  # Increased timeout
            if response.status_code == 200:
                return response.json()
            else:
                logger.info(f"Attempt {attempt + 1} failed with status {response.status_code}. Retrying in {delay} seconds...")
                time.sleep(delay)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            logger.error(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
        attempt += 1
    logger.info("Max retries reached. Exiting.")
    return None


def get_env_list(key: str):
    print(key)
    """Reads an environment variable and splits it into a list if multiple values are present."""
    value = os.getenv(key, "")
    return [v.strip() for v in value.split(",") if v.strip()]

# Function to fetch all contacts with pagination and count records per page
def get_all_contacts():
    contacts_list = []
    total_records = 0  # Total contacts count
    per_page = 0
     
    sub_acnt_api_keys = get_env_list(SUB_ACNT_API_KEYS)
    for sub_acnt_api_key in sub_acnt_api_keys:

        headers = {
        'Authorization': f'Bearer {sub_acnt_api_key}',
        'Content-Type': 'application/json'
        }

        url = f"{API_BASE_URL}/contacts/?&limit=100"
        
        total_records = 0  # Total contacts count
        per_page = 0       # Records per page
        page_number = 1    # Track page number
        
        while url:
            print(f"Fetching Page {page_number}: {url}")
            
            # Fetch data with retry mechanism
            data = fetch_with_retry(url,headers)
            
            if data:
                contacts = data.get('contacts', [])
                contacts_list.extend(contacts)  # Store fetched contacts
                
                # Get meta information
                meta = data.get('meta', {})
                per_page = meta.get('perPage', len(contacts))  # Records per page
                total_records = meta.get('total', 0)          # Total records
                logger.info(f"Page {page_number}: Retrieved {len(contacts)} records")

                # Insert or update the contacts into the database
                upsert_contact_to_db(contacts)  # Insert/update contacts on each page

                # Get next page URL
                next_page_url = meta.get('nextPageUrl', None)
                if next_page_url:
                    next_page_url = next_page_url.replace("http://", "https://")  # Fix http to https if needed
                    url = next_page_url  # Update URL for the next page
                    page_number += 1  # Increment page count
                else:
                    url = None  # No more pages, exit the loop
            else:
                break  # If data is None or request fails, stop

    return contacts_list, total_records, per_page

# Fetch all contacts
all_contacts, total_records, per_page = get_all_contacts()

# Display total contacts fetched
if all_contacts:
    logger.info(f"\nTotal contacts fetched: {len(all_contacts)} / {total_records}")
    logger.info(f"Records per page: {per_page}")
    logger.info(json.dumps(all_contacts[:5], indent=4))  # Show first 5 contacts as a sample
else:
    logger.info("No contacts found.")
