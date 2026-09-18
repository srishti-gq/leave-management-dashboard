import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file("secrets/service_account.json", scopes=SCOPES)
client = gspread.authorize(creds)

SHEET_ID = "1Yjw5dLapgWWHrVy0zGJ1pBYmJWVu0IKkuhoYOiE5ZtY"
sheet = client.open_by_key(SHEET_ID).sheet1

data = sheet.get_all_records()
print(data)