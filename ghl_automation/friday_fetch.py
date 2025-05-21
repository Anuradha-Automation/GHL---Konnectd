from flask import Flask, jsonify
import psycopg2
import os
from dotenv import load_dotenv
import logging
import requests
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Get database connection details
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME', 'Surinder')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres@123')

# Webhook URL
WEBHOOK_URL = os.getenv(
    'WEBHOOK_URL',
    "https://services.leadconnectorhq.com/hooks/FTJnay91o7L6mDzHkzci/webhook-trigger/b8631f7e-2c8b-40e3-8537-5fe0c20e73fb"
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to get database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

# Function to fetch data and send to webhook
def fetch_and_send_data():
    conn = get_db_connection()
    
    if conn is None:
        logger.error("Database connection failed")
        return
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM realtorfridayupdates")
            columns = [desc[0] for desc in cursor.description]
            records = cursor.fetchall()
        
        # Convert to list of dictionaries
        data_array = []

        for record in records:
            row = {columns[i]: (value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value) for i, value in enumerate(record)}
            data_array.append(row)
        
        logger.info("Fetched Data:")
        logger.info(json.dumps(data_array, indent=2))
        
        formatted_data = """        
        
        <ul>
        """
        
        for item in data_array:
            formatted_data += f"""
            <li>
                <strong>Contact Realtor Email:</strong> {item['contact_realtor_email']}<br>
                <strong>Contact Name:</strong> {item['contact_name']}<br>
                <strong>Contact Address:</strong> {item['contact_address']}<br>
                <strong>Contact Phone:</strong> {item['contact_phone']}<br>  
            </li>
            <hr>
            """
        
        formatted_data += "</ul>"

        
        json_response = {"response": formatted_data}
        print(json.dumps(json_response, indent=2))
        
        # Send the formatted response to webhook
        send_to_webhook(json_response)

    except psycopg2.Error as db_error:
        logger.error(f"Database error: {db_error.pgerror}")
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
    finally:
        conn.close()

# Function to send data to webhook
def send_to_webhook(payload):
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            logger.info("✅ Data successfully sent to webhook")
        else:
            logger.error(f"❌ Failed to send data: {response.status_code} - {response.text}")

    except requests.RequestException as e:
        logger.error(f"❌ Error sending data to webhook: {e}")

# Run function on script execution
if __name__ == '__main__':
    fetch_and_send_data()