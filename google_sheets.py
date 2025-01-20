import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Define the scope for Google Sheets and Drive API access
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Use an environment variable to define the path to the credentials file
json_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gws-project-5345-d6f6c3dc800b.json")

if not os.path.exists(json_path):
    raise FileNotFoundError(f"Credentials file not found at {json_path}")

# Authorize using the credentials file
creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
client = gspread.authorize(creds)

def get_allowed_emails(sheet_id, sheet_name):
    """
    Fetch allowed emails from the specified Google Sheet.
    Arguments:
        sheet_id (str): The ID of the Google Sheet.
        sheet_name (str): The name of the worksheet to access.
    Returns:
        list: A list of email addresses from column 1 starting at row 16.
    """
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    emails = sheet.col_values(1)[15:]  # Skip the first 15 rows
    return emails

