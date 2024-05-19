import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key("15VPgLMbxjrtAKhI4TdSEGuRWLexm8zE1XXkGUmdv55k")
sheet = spreadsheet.sheet1

# Function to create a new class with schedule and students sheets
def create_class(class_name):
    try:
        # Create schedule sheet
        schedule_sheet = spreadsheet.add_worksheet(title=f"{class_name}:SCHEDULE", rows=100, cols=20)
        # Create students sheet
        students_sheet = spreadsheet.add_worksheet(title=f"{class_name}:STUDENTS", rows=100, cols=20)
        return True
    except Exception as e:
        st.error(f"An error occurred while creating the class: {e}")
        return False

# Function to register a new user
def register_user(username, password, account_type):
    users = sheet.get_all_records()
    for user in users:
        if user.get('Username') == username:
            return "Username already exists!"
    sheet.append_row([username, password, account_type])
    return "Registration successful!"

# Function to login a user
def login_user(username, password):
    users = sheet.get_all_records()
    for user in users:
        if user.get("Username") == username and str(user.get("Password")) == str(password):
            account_type = user.get("Account Type")
            return account_type, username
    return None, None

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.account_type = ""
    st.session_state.username = ""

# Streamlit application
st.sidebar.title("Navigation")
if st.session_state.logged_in:
    page = st.sidebar.selectbox("Choose a page", ["Home", "Logout"])
else:
    page = st.sidebar.selectbox("Choose a page", ["Login", "Register"])

if page == "Register" and not st.session_state.logged_in:
    st.title("Registration Page")
    st.header("Register")
    register_username = st.text_input("Username", key="register_username")
    register_password = st.text_input("Password", type="password", key="register_password")
    account_type = st.radio("Account Type", ("Teacher", "Student"))
    if st.button("Register"):
        try:
            message = register_user(register_username, register_password, account_type)
            st.success(message) if message == "Registration successful!" else st.error(message)
        except Exception as e:
            st.error(f"An error occurred: {e}")

elif page == "Login" and not st.session_state.logged_in:
    st.title("Login Page")
    st.header("Login")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        try:
            account_type, username = login_user(login_username, login_password)
            if account_type:
                st.session_state.logged_in = True
                st.session_state.account_type = account_type
                st.session_state.username = username
                st.success(f"Logged in as {account_type}")
            else:
                st.error("Invalid username or password")
        except Exception as e:
            st.error(f"An error occurred: {e}")

elif page == "Home" and st.session_state.logged_in:
    st.title("Home Page")
    st.header(f"Welcome, {st.session_state.account_type.lower()} {st.session_state.username}!")

    if st.session_state.account_type.lower() == "teacher":
        st.subheader("Create a Class")
        class_name = st.text_input("Enter Class Name:")
        if st.button("Create Class"):
            if create_class(class_name):
                st.success(f"Class '{class_name}' created successfully!")
            else:
                st.error("Failed to create the class.")
    
    # Display dropdown menu to select a class, excluding the "Users" sheet
    classes = [worksheet.title for worksheet in spreadsheet.worksheets() if "Users" not in worksheet.title]
    selected_class = st.selectbox("Select a Class:", classes)
    
    # Display editable table corresponding to the selected class's schedule
    schedule_sheet = spreadsheet.worksheet(f"{selected_class}:SCHEDULE")
    schedule_data = schedule_sheet.get_all_values()
    df = pd.DataFrame(schedule_data[1:], columns=schedule_data[0])
    st.write(df)  # Display DataFrame
    if st.button("Save Changes"):
        schedule_sheet.update([df.columns.values.tolist()] + df.values.tolist())

elif page == "Logout" and st.session_state.logged_in:
    st.title("Logout Page")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.account_type = ""
        st.session_state.username = ""
        st.success("You have successfully logged out.")
        st.rerun()  # Reload the page to reflect changes
