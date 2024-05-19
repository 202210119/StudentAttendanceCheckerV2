import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

# Function to register a new user to Google Sheets.
def register_user(username, password, account_type):
    # Read data from the connected Google Sheets spreadsheet.
    df = conn.read()

    # Check if the username already exists.
    if username in df['Username'].values:
        return "Username already exists!"
    
    # Append new user information to the DataFrame.
    new_row = {'Username': username, 'Password': password, 'AccountType': account_type}
    df = df.append(new_row, ignore_index=True)
    
    # Write the updated DataFrame back to the Google Sheets spreadsheet.
    conn.write(df)
    
    return "Registration successful!"

# Function to log in a user from Google Sheets.
def login_user(username, password):
    # Read data from the connected Google Sheets spreadsheet.
    df = conn.read()

    # Check if the username and password match.
    user_row = df[(df['Username'] == username) & (df['Password'] == password)]
    if not user_row.empty:
        return user_row.iloc[0]['AccountType']
    else:
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
