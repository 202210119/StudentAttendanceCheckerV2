import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

# Function to join a class
def join_class(username, class_name):
    try:
        class_sheet = spreadsheet.worksheet(f"{class_name}:STUDENTS")
        class_students = class_sheet.get_all_values()
        for student in class_students:
            if student[0] == username:
                return "You are already enrolled in this class!"
        class_sheet.append_row([username])
        return f"{username} has been added to the class '{class_name}'!"
    except gspread.exceptions.WorksheetNotFound:
        return f"Class '{class_name}' does not exist."

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
    
    elif st.session_state.account_type.lower() == "student":
        st.subheader("Join a Class")
        class_name = st.text_input("Enter Class Name to Join:")
        if st.button("Join Class"):
            message = join_class(st.session_state.username, class_name)
            st.success(message) if "added" in message else st.error(message)

elif page == "Logout" and st.session_state.logged_in:
    st.title("Logout Page")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.account_type = ""
        st.session_state.username = ""
        st.success("You have successfully logged out.")
        st.rerun()  # Reload the page to reflect changes
