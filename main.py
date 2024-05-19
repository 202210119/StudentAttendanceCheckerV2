import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("path/to/credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Your Google Sheet Name").sheet1  # Open the Google Sheet

def register_user(username, password, account_type):
    users = sheet.get_all_records()
    for user in users:
        if user['Username'] == username:
            return "Username already exists!"
    sheet.append_row([username, password, account_type])
    return "Registration successful!"

def login_user(username, password):
    users = sheet.get_all_records()
    for user in users:
        if user['Username'] == username and user['Password'] == password:
            return user['AccountType']
    return None

# Streamlit application
st.title("Registration and Login Page")

# User Registration
st.header("Register")
register_username = st.text_input("Username", key="register_username")
register_password = st.text_input("Password", type="password", key="register_password")
account_type = st.radio("Account Type", ("Teacher", "Student"))
if st.button("Register"):
    message = register_user(register_username, register_password, account_type)
    st.success(message) if message == "Registration successful!" else st.error(message)

# User Login
st.header("Login")
login_username = st.text_input("Username", key="login_username")
login_password = st.text_input("Password", type="password", key="login_password")
if st.button("Login"):
    account_type = login_user(login_username, login_password)
    if account_type:
        st.success(f"Logged in as {account_type}")
    else:
        st.error("Invalid username or password")
