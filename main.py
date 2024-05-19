import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key("15VPgLMbxjrtAKhI4TdSEGuRWLexm8zE1XXkGUmdv55k")

# Function to create a new class sheet
def create_class(class_name):
    try:
        spreadsheet.add_worksheet(title=class_name, rows=100, cols=20)
        return True
    except Exception as e:
        st.error(f"An error occurred while creating the class: {e}")
        return False

# Function to get the list of classes
def get_classes():
    # Get all worksheet titles
    all_worksheets = [worksheet.title for worksheet in spreadsheet.worksheets()]
    # Filter out users as classes
    classes = [worksheet for worksheet in all_worksheets if worksheet.lower() != "users"]
    return classes

# Function to log attendance
def log_attendance(username, class_name):
    try:
        schedule_sheet = spreadsheet.worksheet(f"{class_name}:SCHEDULE")
        current_time = datetime.now().strftime("%I:%M %p")
        schedule_data = schedule_sheet.get_all_records()

        # Debugging: Print schedule data to check the structure
        st.write(schedule_data)

        current_time_obj = datetime.strptime(current_time, "%I:%M %p")

        for i, entry in enumerate(schedule_data):
            schedule_time_str = entry.get('Time')
            if not schedule_time_str:
                continue

            try:
                schedule_time_obj = datetime.strptime(schedule_time_str, "%I:%M %p")
            except ValueError:
                continue

            if i + 1 < len(schedule_data):
                next_schedule_time_str = schedule_data[i + 1].get('Time')
                if next_schedule_time_str:
                    try:
                        next_schedule_time_obj = datetime.strptime(next_schedule_time_str, "%I:%M %p")
                    except ValueError:
                        next_schedule_time_obj = schedule_time_obj + timedelta(hours=1)
                else:
                    next_schedule_time_obj = schedule_time_obj + timedelta(hours=1)
            else:
                next_schedule_time_obj = schedule_time_obj + timedelta(hours=1)

            if schedule_time_obj <= current_time_obj < next_schedule_time_obj:
                subject = entry.get('Subject', 'N/A')
                date_str = datetime.now().strftime("%m/%d/%Y, %A")
                attendance_sheet = schedule_sheet.col_values(1)
                if date_str not in attendance_sheet:
                    schedule_sheet.append_row([date_str])

                row_index = attendance_sheet.index(date_str) + 1
                column_index = len(schedule_sheet.row_values(row_index)) + 1
                attendance_time = datetime.now().strftime("%I:%M %p")
                attendance_record = f"{username} present in {subject} at {attendance_time}"
                schedule_sheet.update_cell(row_index, column_index, attendance_record)
                return f"Attendance logged for {username} in {subject} at {current_time}"

        return f"No class scheduled at {current_time}"
    except Exception as e:
        return f"An error occurred while logging attendance: {e}"

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
    
    # Display dropdown menu to select a class
    classes = get_classes()
    selected_class = st.selectbox("Select a Class:", classes)

    if st.session_state.account_type.lower() == "student" and selected_class:
        if st.button("Log Attendance"):
            message = log_attendance(st.session_state.username, selected_class)
            st.success(message) if "logged" in message else st.error(message)

elif page == "Logout" and st.session_state.logged_in:
    st.title("Logout Page")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.account_type = ""
        st.session_state.username = ""
        st.success("You have successfully logged out.")
        st.rerun()  # Reload the page to reflect changes
