from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv
import logging
import re  # Regex module for extracting email

# Load environment variables
load_dotenv()

# Get database connection details
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_NAME = os.getenv('DB_NAME', 'Surinder')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres@123')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

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

# Function to extract email from a given string
def extract_email(text):
    if not text:
        return None  # No email found

    # Regex pattern to extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return email_match.group(0) if email_match else None

# Function to extract name (excluding email) from contact_name
def extract_name(text):
    if not text:
        return None  # No name found

    # Remove email from the text
    return re.sub(r'[\w\.-]+@[\w\.-]+', '', text).strip()

# Webhook endpoint to receive JSON data from GHL
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get JSON data from the request
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        # Log received data
        logger.info(f"Received Data: {data}")

        # Extract fields
        contact_name = data.get("contact_name", "")
        user_email = data.get("user_email", "")

        # Extract email from contact_name if needed
        extracted_email = extract_email(contact_name)

        # If user_email is empty or "null", replace it with extracted_email
        if not user_email or user_email.lower() in ["null", ""]:
            user_email = extracted_email if extracted_email else "no-email@example.com"

        # Extract proper name from contact_name
        cleaned_name = extract_name(contact_name)

        # Update data dictionary with correct values
        data["contact_name"] = cleaned_name
        data["user_email"] = user_email

        # Print extracted values before inserting
        logger.info(f"Extracted Name: {cleaned_name}, Extracted Email: {user_email}")

        # Ensure `id` is treated as a string
        if "id" in data:
            data["id"] = str(data["id"])  # Convert ID to string if needed

        # Dynamically prepare query based on available fields
        columns = ', '.join([f'"{col}"' for col in data.keys()])
        values = tuple(data.values())
        placeholders = ', '.join(['%s'] * len(values))

        # Insert data into realtorfridayupdates table
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        insert_query = f'INSERT INTO realtorfridayupdates ({columns}) VALUES ({placeholders})'
        cursor.execute(insert_query, values)

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("Data inserted successfully into realtorfridayupdates table")
        return jsonify({"message": "Data inserted successfully"}), 200

    except psycopg2.Error as db_error:
        logger.error(f"Database error: {db_error.pgerror}")
        return jsonify({"error": "Database error occurred", "details": str(db_error.pgerror)}), 500
    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
