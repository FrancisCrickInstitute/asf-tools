Here's a detailed structural and functional breakdown of the script currently used to access the PPMS system (can be found here: https://github.com/FrancisCrickInstitute/pipeline-technologies-airflow-dags/blob/staging/scripts/ppms/ppms_incident_notifier.py )

## **Overall Purpose:**
This script automates the process of notifying users about incidents related to upcoming bookings for PPMS (a core facility management platform). It interacts with a database, sends emails, and posts Slack notifications about equipment issues that could affect users' bookings.

---

## **Main Components and Flow:**
### 1. **Imports and Setup:**
   - The script uses multiple libraries including:
     - `sqlalchemy` for database interaction.
     - `requests` and `json` for HTTP communication and JSON handling.
     - `rich` for enhanced logging and tracebacks.
   - Configuration is loaded from a `toml` file (`crick.toml`).

---

### 2. **Helper Functions (Part 1)**
These functions are utility functions for formatting and data processing:

- **`load_toml_file(file_name)`**: 
   - Reads and parses a TOML configuration file.
   - Returns the configuration as a dictionary.

- **`standardise_datetime_format(datetime_string)`**: 
   - Converts datetime strings into a standardized format (`"%Y-%m-%d %H:%M:%S"`).

- **`swap_words(input_string)`**: 
   - Replaces certain characters (used for obfuscation or anonymization).

- **`insert_record(session, metadata, table_name, record)`**: 
   - Inserts a record into the specified database table using SQLAlchemy.
   - Commits the transaction after insertion.

---

### 3. **Database Setup and ORM Management (Part 1 & 2)**
- **Database Connection Setup**:
   - SQLAlchemy engine and session creation for database interaction.

- **ORM Management:**
   - `metadata = MetaData()` used to define database schema information.
   - Session is created using `sessionmaker` from SQLAlchemy.

---

### 4. **Data Loading and Processing (Part 2)**
- **Fetching Incident Reports and Booking Data:**
   - Data is loaded from an API (`ppms_endpoint`) using the `requests` library.
   - Incident data and booking data are processed to match with user details.
   - Bookings are checked against incident reports for conflicts.

- **Booking and Incident Matching Logic:**
   - Incidents are categorized based on severity and matched against future bookings.
   - Each incident and booking is associated with a user and a system ID.

---

### 5. **Notification Generation (Part 3)**
#### **Email Notifications for New Events:**
- For each user with a booking, the script:
   - Constructs an HTML email body explaining the incident.
   - Provides direct links to PPMS for more details.
   - Emphasizes high-severity incidents with a red warning.
   - Adds the user's email along with the facility's contact to the recipient list.

#### **Slack Notifications for New Events:**
- Slack messages are sent using the `requests.post()` method with a pre-assembled JSON payload.

#### **Reminder Emails for Ongoing Issues:**
- Reminder emails are generated similarly to the new event emails.
- These are sent for bookings happening within the next three days.

---

### 6. **Logging and Dry-Run Modes (Part 3)**
- **Dry-Run Modes:**
   - `dry_run_db`: Simulates database insertions without committing changes.
   - `dry_run_comms`: Simulates sending emails and Slack notifications without actual communication.

- **Logging:**
   - `rich.logging.RichHandler` is configured for detailed console output.
   - Provides tracebacks and structured logging messages.

---

### 7. **Configuration Management (Part 3)**
- **Configuration Loaded From `crick.toml`:**
   - Database credentials and Slack webhook URL are stored in this file.
   - Parameters like `ppms_api_key`, `slack_url`, and table suffix are retrieved here.

---

### 8. **Main Execution Flow (Entry Point) (Part 3)**
- The script begins execution from the `if __name__ == "__main__"` block:
   - Configurations are loaded.
   - Database credentials and communication settings are retrieved.
   - The `execute()` function is called with all necessary parameters and flags for dry-run modes.

---

## **Key Functional Areas:**
1. **Database Interaction:**
   - Uses SQLAlchemy to insert records into a table storing incident reports.
   - SQLAlchemy ORM is used for abstracting SQL operations.

2. **Data Fetching and Processing:**
   - Data is retrieved from an API endpoint.
   - Bookings and incidents are matched and filtered based on conditions (e.g., severity).

3. **Notification Handling:**
   - Email and Slack notifications are generated and sent based on booking conflicts.
   - Users and admins are notified separately with personalized content.

4. **Error Handling and Logging:**
   - Extensive logging using the `rich` library.
   - Errors during execution are traced with `rich.traceback`.

5. **Configuration Management:**
   - Configurations for the database and API keys are stored in a separate TOML file.
   - Enhances security and maintainability.
