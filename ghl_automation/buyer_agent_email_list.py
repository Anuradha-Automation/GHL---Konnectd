import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
BUYER_AGENTS_EMAILS = os.getenv('BUYER_AGENTS_EMAILS')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logs_setup_file import setup_logging

module_name = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logging(module_name)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def parse_buyer_agent_emails():
    """
    Extracts just the email addresses from the environment variable
    """
    email_mappings = BUYER_AGENTS_EMAILS.split(",")
    emails = [entry.split(":")[1] for entry in email_mappings if ":" in entry]
    return emails

def fetch_buyer_agent_email_list():
    emails = parse_buyer_agent_emails()
    if not emails:
        logger.error("No emails found to query.")
        return

    # Dynamically create placeholders for the IN clause
    placeholders = ','.join(['%s'] * len(emails))
    query = f"""
        SELECT 
            c.id AS contact_id,
            c.location_id,
            c.first_name,
            c.last_name,
            c.email,
            c.company_name,
            c.phone,
            ccf.value AS custom_field_value,
            cf.name AS custom_field_name,
            cf.field_key AS custom_field_key
        FROM 
            contact_custom_fields ccf
        JOIN 
            contact c ON ccf.contact_id = c.id
        JOIN 
            custom_fields cf ON ccf.custom_field_id = cf.id
        WHERE 
            ccf.value IN ({placeholders});
    """

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, emails)
        records = cursor.fetchall()

        record_count = len(records)
        logger.info(f"Total records fetched: {record_count}")

        print("\nFetched Records:\n")
        for record in records:
            print(record)

        cursor.close()
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    fetch_buyer_agent_email_list()
