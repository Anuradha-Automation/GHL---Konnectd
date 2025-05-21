# Project Name
## GHL(GoHighLevel) - Konnectd - Brad

# Project Structure
* GHL---Konnectd/

## ghl_automation

  │── ghl_automation/ 


  │ ├── birthday_reminder.py 

  │   ├── contact_insert.py
  
  │   ├── custom_fields.py

  │   ├── friday_fetch.py

  │   ├── friday_insert.py

  │   ├── ghl_get_insert.py

  │   ├── mortgage_report_generate.py




## web_base_automations

  │── web_base_automations/ 


  │ ├── course_progress_report.py


  │   ├── generate_token_file.py


  │   ├── login_with_google_api.py

  │   ├── leadership_leap.py

  │   ├── webdriver_configration.py

  │├──webhook_workflows_handle_contact_creation_and_linking.py

# Setup Instructions

## Installation

### Python Installation Process
Before proceeding, ensure Python is installed on your system. If not, you can download and install Python from [python.org](https://www.python.org/downloads/).

# Getting Started

### Clone the Project
```
git clone https://github.com/exoticaitsolutions/GHL---Konnectd.git
```

## Navigate to the Project Directory

```
  cd GHL---Konnectd
```

# Install Dependencies
## Using requirements.txt
```
pip install -r requirements.txt
```

## Prerequisites
Ensure you have the following installed:
- Python 3.x
- PostgreSQL

# Setup .env File
* Create a `.env` file in the main project directory with the following variables
```
API_BASE_URL=https://rest.gohighlevel.com/v1
API_KEY='Enter API_KEY'
DELETED_USER_ZAP_WEBHOOK_URL='Enter DELETED_USER_ZAP_WEBHOOK_URL'
SUB_ACNT_API_KEYS= 'Enter SUB_ACNT_API_KEYS'
MORTGAGE_LOCATION_IDS='Enter MORTGAGE_LOCATION_IDS'
ASSIGNED_TO_ID='Enter ASSIGNED_TO_ID'
DB_HOST='Enter DB_HOST'
DB_PORT='Enter DB_PORT'
DB_NAME='Enter DB_NAME'
DB_USER='Enter DB_USER'
DB_PASSWORD='Enter DB_PASSWORD'
BIRTHDAY_REPORTS1='Enter BIRTHDAY_REPORTS1'
#web autmations cred start here ------------------------
KONNECTED_EMAIL = 'Enter KONNECTED_EMAIL'
KONNECTED_PASSWORD = 'Enter KONNECTED_PASSWORD'
WORKFLOW_LOCATION_IDS='Enter WORKFLOW_LOCATION_IDS'
# Login wih google credential
TOKEN_PATH = 'Enter TOKEN_PATH'
CLIENT_SECRET_PATH = 'Enter CLIENT_SECRET_PATH'
VONLANE_COURSE_EXCLUDED_EMAILS= 'Enter VONLANE_COURSE_EXCLUDED_EMAILS'
LEADERSHIP_COURSE_EXCLUDED_EMAILS= 'Enter LEADERSHIP_COURSE_EXCLUDED_EMAILS'
CourseProgressReport1='Enter CourseProgressReport1'
CourseProgressReport2='Enter CourseProgressReport2'
CourseProgressReport3='Enter CourseProgressReport3'
COURSE_PROGRESS_ZAP_WEBHOOK_URL='Enter COURSE_PROGRESS_ZAP_WEBHOOK_URL'
```


# File Run Process

### 1. Birthday Reminder Script(File Name-`birthday_reminder.py`)

## Run the script using the command
```
python birthday_reminder.py
```

## Overview
* The birthday_reminder.py script fetches upcoming birthdays from a PostgreSQL database, generates a CSV file, and sends it to a Zapier webhook for processing. It automates data retrieval, extraction, and transmission in one seamless flow.


## How It Works
1. The script loads environment variables from the `.env` file.
2. It connects to the PostgreSQL database and fetches contact details of individuals whose birthdays fall in the next month.
3. The extracted data is written to a CSV file named `Birthday_labels.xlsx`.
4. The generated CSV file is sent to a Zapier webhook for further processing.


## Cron Job Schedule
* This script runs automatically on the 23rd of every month at 12:00 AM:
0 0 23 * * /usr/bin/python3 /home/ubuntu/GHL---Konnectd/ghl_automation/birthday_reminder.py >> /home/ubuntu/cronlogs/birthday_reminder_cronjob.log 2>&1


## 2. Contact Insert Script(File Name-`contact_insert.py`)
## Run the script using the command
```
python contact_insert.py
```

## Overview
* The contact_insert.py script fetches contact data from an API, processes the data, and inserts or updates records in a PostgreSQL database. It also handles pagination and custom fields efficiently.


## Cron Job Schedule
* This script runs automatically every Sunday at 12:00 AM:
0 0 * * 0 /usr/bin/python3 /home/ubuntu/GHL---Konnectd/ghl_automation/contact_insert.py >> /home/ubuntu/cronlogs/contact_insert_cronjob.log 2>&1


## 3. Custom Fields Script(File Name-`custom_fields.py`)

## Run the script using the command
```
python custom_fields.py
```

## Overview
The `custom_fields.py` script is designed to fetch custom field data from an API, process the data, and insert or update records in a PostgreSQL database. It ensures data integrity and handles retries for API requests.

## Features
- Fetches custom fields from an API
- Retries failed requests with exponential backoff
- Inserts or updates custom fields into a PostgreSQL database
- Uses environment variables for configuration
- Implements structured logging for better debugging


### 4. Webhook Workflow Script(File Name-`friday_insert.py`)

## Run the script using the command
```
python friday_insert.py
```
## Overview
* This  script is inserting multiple contacts' data into a PostgreSQL database.

### 5. Webhook Workflow Script(File Name-`friday_fetch.py`)

## Run the script using the command
```
python friday_fetch.py
```
## Overview
* This script retrieves data from the database and then sends all the data via an inbound webhook for automation, which delivers it through email.

## 6. GHL Get and Insert Script(File Name-`ghl_get_insert.py`)

## Run the script using the command
```
python ghl_get_insert.py
```

## Overview
* This script fetches user and location data from an API and inserts or updates the data into a PostgreSQL database. It also monitors deleted users and sends notifications through a Zapier webhook.

## Features
- Fetches user and location data from an API.
- Inserts or updates user data into PostgreSQL.
- Monitors and deletes users missing from the API.
- Notifies of deleted users via a Zapier webhook.
- Uses structured logging for debugging.


## Cron Job Schedule
* This script runs automatically every 3 days at 7:00 AM:
0 13 */3 * * /usr/bin/python3 /home/ubuntu/GHL---Konnectd/ghl_automation/ghl_get_insert.py >> /home/ubuntu/cronlogs/ghl_get_insert_cronjob.log 2>&1


## 5. Custom Contacts Script(File Name-`mortgage_report_generate.py`)

## Run the script:
```
python mortgage_report_generate.py
```
## Overview
This file, mortgage_report_generate.py, generates a mortgage report for the subaccount C2 Financial - Rob Tennyson by extracting all data from the contacts' custom fields. It creates an Excel (.xlsx) file named updated_invoice_ycUwnMJkYgOAtPXXJBaP_template.xlsx.

## Features
- Connects to a PostgreSQL database
- Fetches contacts along with custom field data
- Writes data to a CSV file
- Implements logging for tracking script execution

### 6. Course Progress Report Script(File Name-`course_progress_report.py`)

## Run the script:
```
python course_progress_report.py
```

## Overview
The course_progress_report.py script retrieves weekly video and quiz progress details and saves this data in an XLSX format along with user details.

## Features
- Generates an XLSX file with user details.
- Users who have **never logged in** are highlighted in **red** in the report.
- Sends the generated XLSX file to a Zapier webhook.


## Cron Job Schedule
* This script runs automatically every Monday and Thursday at 3:00 AM:
0 3 * * 1,4 /usr/bin/python3 /home/ubuntu/GHL---Konnectd/web_base_automations/course_progress_report.py >> /home/ubuntu/cronlogs/course_progress_report.log 2>&1


## 7. Leadership Leap Script (File Name-` leadership_leap.py`)

## Run the script using the command
```
python leadership_leap.py
```

## Overview
This script processes leadership development program data and exports it to a log file.


## Cron Job Schedule
This script runs automatically every Wednesday at 8:00 PM:
0 20 * * 3 /usr/bin/python3 /home/ubuntu/GHL---Konnectd/web_base_automations/leadership_leap.py >> /home/ubuntu/cronlogs/leadership_leap.log 2>&1


### 8. Webhook Workflow Script(File Name-`webhook_workflows_handle_contact_creation_and_Linking.py`)

## Run the script using the command
```
python webhook_workflows_handle_contact_creation_and_Linking.py
```

## Overview
The `webhook_workflows_handle_contact_creation_and_Linking.py` script tracks a specific **location ID** and navigates inside the **workflow's webhook**. It copies the **inbound webhook URL** from the **seller agent contact creation** section. Then, it returns and pastes the copied URL into the **webhook for seller agent fields changed**, completing the webhook setup.

## Features
- Monitors workflows for a given location ID.
- Reduces manual effort by automating the webhook linking process.
- Ensures accurate and error-free integration.
- Helps in seamless contact creation and linking automation


# Troubleshooting
- Ensure the `.env` file is correctly configured.
- Check the database connection settings.
- If API requests fail, verify the API key and endpoint.
- Ensure PostgreSQL is running and accessible.
- Verify that the database contains valid date entries.

# Logs Monitoring
* Check the logs_detail folder to track and analyze the output responses of each script for better debugging and performance monitoring.