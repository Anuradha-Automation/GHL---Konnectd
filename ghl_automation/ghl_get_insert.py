import os
import sys
import requests
import psycopg2
import json
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
DELETED_USER_ZAP_WEBHOOK_URL = os.getenv("DELETED_USER_ZAP_WEBHOOK_URL")
# Set the headers with the API key
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
}

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

# Function to fetch Location data
def get_locations():
    url = f'{API_BASE_URL}/locations'
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        locations = response.json()
        logger.info(f"Successfully fetched {len(locations)} locations.")
        return locations
    else:
        logger.error(f"Error fetching locations: {response.status_code}")
        return None

# Function to send data to Zapier webhook
def send_to_zapier_webhook(data):
    try:
        response = requests.post(DELETED_USER_ZAP_WEBHOOK_URL, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            logger.info("Data successfully sent to Zapier.")
        else:
            logger.error(f"Failed to send data to Zapier: {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending data to Zapier: {e}")

# Function to fetch User data
def get_users():
    url = f'{API_BASE_URL}/users'
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        logger.info(f"Successfully fetched {len(response.json())} users.")
        return response.json()
    else:
        logger.error(f"Error fetching users: {response.status_code}")
        return None

# Function to monitor and notify deleted users from PostgreSQL based on GHL user data
def monitor_and_notify_deleted_users(current_ghl_users):
    try:
        users_ghl = current_ghl_users['users']
        ghl_user_emails = {user['email'] for user in users_ghl}
        # Connect to PostgreSQL and fetch existing users
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to get emails of users already in PostgreSQL
        cursor.execute("SELECT email FROM users")
        postgres_user_emails = {email[0] for email in cursor.fetchall()}

        # Find deleted users (users in PostgreSQL but not in GHL)
        deleted_users = postgres_user_emails - ghl_user_emails

        if deleted_users:
            sr_no = 1  # Serial number for reporting
            deleted_count = 0  # Counter for deleted users

            for email in deleted_users:
                # Query to get user details from PostgreSQL based on email
                cursor.execute("SELECT location_id, first_name, last_name, email, phone FROM users WHERE email = %s", (email,))
                user_to_notify = cursor.fetchone()

                if user_to_notify:
                    location_id, firstname, lastname, email, phone = user_to_notify
                    cursor.execute("SELECT name FROM location WHERE id = %s", (location_id,))
                    location_name_result = cursor.fetchone()
                    # Prepare data to send to Zapier for this individual user
                    zapier_data = {
                        "message": "Slack Notify",
                        "type": "deleted_user",
                        "sr_no": sr_no,
                        "firstname": firstname,
                        "lastname": lastname,
                        "email": email,
                         "subaccount": location_name_result,
                        "phone": phone
                    }

                    # Send the webhook for this deleted user to Zapier
                    send_to_zapier_webhook(zapier_data)
                    logger.info(f"Sent webhook for deleted user: {firstname} {lastname} with email: {email}")

                    # Delete the user from PostgreSQL
                    cursor.execute("DELETE FROM users WHERE email = %s", (email,))
                    conn.commit()
                    logger.info(f"Deleted user {firstname} {lastname} with email {email} from PostgreSQL.")
                    deleted_count += 1

                    sr_no += 1  # Increment serial number for the next user

            logger.info(f"Total {deleted_count} users were deleted and notified via Zapier.")
        else:
            logger.info("No users were deleted from PostgreSQL.")

    except Exception as e:
        logger.error(f"Error monitoring and notifying deleted users: {e}")
    finally:
        # Ensure cursor and conn are closed, even if they are not initialized
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

# Function to insert or update user data into the PostgreSQL database
def upsert_user_to_db(user_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Loop over each user in the provided list
        for user in user_data['users']:
            if isinstance(user, dict):  # Ensure the user is a dictionary
                user_email = user.get('email')
                logger.info(f"Processing user email: {user_email}")

                # Extract location_id, type, and role from the 'roles' field
                location_ids = user.get('roles', {}).get('locationIds', [])
                location_id = location_ids[0] if location_ids else None
                user_type = user.get('roles', {}).get('type', None)
                user_role = user.get('roles', {}).get('role', None)

                # Check if the user already exists by email
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (user_email,))
                exists_in_db = cursor.fetchone()[0]

                # If user exists in the database, update or delete accordingly
                if exists_in_db:
                    cursor.execute("SELECT * FROM users WHERE email = %s", (user_email,))
                    db_user = cursor.fetchone()

                    # Check if user is missing in GHL (i.e., exists in DB but not in GHL)
                    if user_email not in [user['email'] for user in user_data['users']]:
                        location_id, sr_no, firstname, lastname, email, phone = db_user

                        zapier_data = {
                            "message": "Slack Notify",
                            "type": "deleted_user",
                            "sr_no": sr_no,
                            "firstname": firstname,
                            "lastname": lastname,
                            "email": email,
                            "phone": phone
                        }
                        # Send the webhook for this individual user
                        send_to_zapier_webhook(zapier_data)
                        cursor.execute("DELETE FROM users WHERE email = %s", (email,))
                        conn.commit()
                        logger.info(f"Deleted user {firstname} {lastname} with email {email} from PostgreSQL.")

                    # Update the existing user in DB
                    cursor.execute("""
                        UPDATE users 
                        SET location_id = %s, first_name = %s, last_name = %s, phone = %s, 
                            role_type = %s, role = %s
                        WHERE email = %s
                    """, (
                        location_id,
                        user.get('firstName'),
                        user.get('lastName'),
                        user.get('phone'),
                        user_type,
                        user_role,
                        user_email
                    ))
                    logger.info(f"User with email {user_email} updated.")
                else:
                    # If the user doesn't exist in DB, insert them
                    cursor.execute("""
                        INSERT INTO users (location_id, first_name, last_name, email, phone, role_type, role)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        location_id,
                        user.get('firstName'),
                        user.get('lastName'),
                        user.get('email'),
                        user.get('phone'),
                        user_type,
                        user_role
                    ))
                    logger.info(f"User with email {user_email} inserted.")
        
        # Commit the transaction
        conn.commit()
        logger.info("User data processed successfully!")

    except Exception as e:
        logger.error(f"Error upserting user data into DB: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Function to insert or update location data into the PostgreSQL database
def upsert_location_to_db(location_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for location in location_data['locations']:
            if isinstance(location, dict):  # Ensure location is a dictionary
                location_id = location.get('id')
                logger.info(f"Processing location ID: {location_id}")
                
                # Check if the location already exists
                cursor.execute("SELECT COUNT(*) FROM location WHERE id = %s", (location_id,))
                exists = cursor.fetchone()[0]
                
                if exists:
                    # Update the existing location
                    cursor.execute("""
                        UPDATE location SET name = %s, address = %s, city = %s, state = %s,
                            country = %s, postal_code = %s, website = %s, timezone = %s,
                            first_name = %s, last_name = %s, email = %s, phone = %s
                        WHERE id = %s
                    """, (
                        location.get('name'),
                        location.get('address'),
                        location.get('city'),
                        location.get('state'),
                        location.get('country'),
                        location.get('postal_code'),
                        location.get('website'),
                        location.get('timezone'),
                        location.get('first_name'),
                        location.get('last_name'),
                        location.get('email'),
                        location.get('phone'),
                        location_id
                    ))
                    logger.info(f"Location ID {location_id} updated.")
                else:
                    # Insert a new location if it doesn't exist
                    cursor.execute("""
                        INSERT INTO location (id, name, address, city, state, country, postal_code,
                            website, timezone, first_name, last_name, email, phone)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        location_id,
                        location.get('name'),
                        location.get('address'),
                        location.get('city'),
                        location.get('state'),
                        location.get('country'),
                        location.get('postal_code'),
                        location.get('website'),
                        location.get('timezone'),
                        location.get('first_name'),
                        location.get('last_name'),
                        location.get('email'),
                        location.get('phone')
                    ))
                    logger.info(f"Location ID {location_id} inserted.")
        
        conn.commit()
        logger.info("Location data processed successfully!")

    except Exception as e:
        logger.error(f"Error upserting location data into DB: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Main execution
if __name__ == "__main__":
    logger.info("Fetching User Data...")
    users = get_users()
    if users:
        logger.info(f"Fetched {len(users)} users.")
        
        # Monitor and notify if users are deleted
        monitor_and_notify_deleted_users(users)
        
        # Insert or update users into the PostgreSQL database
        upsert_user_to_db(users)
    else:
        logger.warning("No users fetched.")
    
    # Fetch and upsert location data
    logger.info("Fetching Location Data...")
    locations = get_locations()
    if locations:
        logger.info(f"Fetched {len(locations)} locations.")
        upsert_location_to_db(locations)
