import os
import sys
import psycopg2
import requests
import datetime
# import logging
from dotenv import load_dotenv



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logs_setup_file import setup_logging

module_name = os.path.splitext(os.path.basename(__file__))[0]

logger = setup_logging(module_name)

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/15959141/2l7nq1b/"

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def get_birthdays_next_month(location_id):
    today = datetime.date.today()
    next_month = today.month + 1 if today.month < 12 else 1
    assigned_to_id = os.getenv('ASSIGNED_TO_ID')  # Get from .env

    query = """
        SELECT first_name, last_name, email, phone,
            TO_CHAR(date_of_birth, 'MM-DD') AS dob,
            TRIM(
                BOTH ', ' FROM
                COALESCE(NULLIF(address1, 'null'), '') ||
                CASE WHEN COALESCE(NULLIF(address1, 'null'), '') <> '' AND COALESCE(NULLIF(city, 'null'), '') <> '' THEN ', ' ELSE '' END ||
                COALESCE(NULLIF(city, 'null'), '') ||
                CASE WHEN (COALESCE(NULLIF(address1, 'null'), '') <> '' OR COALESCE(NULLIF(city, 'null'), '') <> '') AND COALESCE(NULLIF(state, 'null'), '') <> '' THEN ', ' ELSE '' END ||
                COALESCE(NULLIF(state, 'null'), '') ||
                CASE
                    WHEN LENGTH(COALESCE(NULLIF(postal_code, 'null'), '')) <= 5 THEN
                        CASE WHEN (COALESCE(NULLIF(address1, 'null'), '') <> '' OR COALESCE(NULLIF(city, 'null'), '') <> '' OR COALESCE(NULLIF(state, 'null'), '') <> '')
                        THEN ', ' ELSE '' END || COALESCE(NULLIF(postal_code, 'null'), '')
                    ELSE
                        CASE WHEN (COALESCE(NULLIF(address1, 'null'), '') <> '' OR COALESCE(NULLIF(city, 'null'), '') <> '' OR COALESCE(NULLIF(state, 'null'), '') <> '')
                        THEN ', ' ELSE '' END || LEFT(COALESCE(NULLIF(postal_code, 'null'), ''), 5)
                END
            ) AS full_address
        FROM contact
        WHERE EXTRACT(MONTH FROM date_of_birth) = %s
            AND location_id = %s
            AND assigned_to = %s
        ORDER BY TO_CHAR(date_of_birth, 'MM-DD') ASC;
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (next_month, location_id, assigned_to_id))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return data


def send_data_to_zapier(data, location_id, email, name, report_index):
    if not data:
        logger.info(f"No birthdays found for next month at location: {location_id} (Report: {report_index})")
        return 0

    row_count = len(data)

    payload = {
        "location_id": location_id,
        "report_index": report_index,
        "row_count": row_count,
        "first_names": [(row[0] or "").capitalize() for row in data],
        "last_names": [(row[1] or "").capitalize() for row in data],
        "emails": [row[2] for row in data],    
        "phones": [row[3] for row in data],    
        "dob": [row[4] for row in data],        
        "addresses": [row[5] for row in data],    
        "birthday_report_email": email,        
        "birthday_report_name": name,            
        "birthday_report_number": report_index    
    }

    response = requests.post(ZAPIER_WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        logger.info(f"Data successfully sent to Zapier for location: {location_id} (Report: {report_index}, Rows: {row_count})")

    else:
        logger.error(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")


    return row_count

def parse_birthday_reports():
    email_location_map = {}

    index = 1
    while True:
        env_var_name = f"BIRTHDAY_REPORTS{index}"
        report = os.getenv(env_var_name)

        if not report:
            break

        if " from " not in report:
            logger.error(f"Skipping malformed entry: '{report}' (missing ' from ')")

            index += 1
            continue

        email, rest = report.split(" from ", 1)

        if " - " not in rest:
            logger.error(f"Skipping malformed entry: '{report}' (missing ' - ')")
            index += 1
            continue

        name, location = rest.split(" - ", 1)
        location_id = location.strip()
        email_location_map[index] = (email, name, location_id)

        index += 1

    return email_location_map


def main():
    email_location_map = parse_birthday_reports()
    total_rows = 0

    for report_index, (email, name, location_id) in email_location_map.items():
        logger.info(f"Processing birthdays for {name} ({email}) at location: {location_id} (Report: {report_index})")
        data = get_birthdays_next_month(location_id)
        total_rows += send_data_to_zapier(data, location_id, email, name, report_index)

    logger.info(f"Total Rows Processed: {total_rows}")

if __name__ == '__main__':
    main()