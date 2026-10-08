import sqlite3
import database as db
import pandas as pd
import portal
import streamlit as st

# Setting up the page configuration
st.set_page_config(page_title="OceanConnect", page_icon="🌊")

# Initialize DataBase
db.init_db()

# Initialize Sessions in State
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
if "username" not in st.session_state:
  st.session_state["username"] = ""
if "role" not in st.session_state:
  st.session_state["role"] = ""

def show_login_signup():
  # 📍 Sidebar logo with custom width
  st.sidebar.image("ocean logo.png", width=180)

  st.title("Ocean Connect")
  st.caption("Connecting people to ocean-related activities")

  menu = ["Login", "Sign Up"]
  choice = st.sidebar.selectbox("Navigation", menu)

  if choice == "Login":
    st.subheader("Log into your account")
    with st.form("login_form"):
      username = st.text_input("Username")
      password = st.text_input("Password", type="password")
      submit = st.form_submit_button("Log In")

    if submit:
      user_role = db.verify_user(username, password)
      if user_role:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["role"] = user_role
        st.success(f"Login Successful as {user_role} !!")
        st.rerun()
      else:
        st.error("Invalid username or password.")

  elif choice == "Sign Up":
        st.subheader("Create a new Account")
        with st.form("signup_form"):
            new_user = st.text_input("Choose Username", autocomplete="off")
            new_pass = st.text_input("Add Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            
            role_choice = st.radio("Account Type", ["Volunteer", "Organizer"])
            submit = st.form_submit_button("Sign Up")

            if submit:
                role = "Organizer" if "Organizer" in role_choice else "Volunteer"
                if not new_user or not new_pass:
                    st.warning("Please fill out all the fields.")
                elif new_pass != confirm_pass:
                    st.error("Password not matched")
                else:
                    if db.register_user(new_user, new_pass, role):
                        # 1. Set session state variables immediately upon registration
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = new_user
                        st.session_state["role"] = role
                        st.success("Account created successfully! Redirecting...")
                        
                        # 2. Automatically rerun to open portal.py directly
                        st.rerun()
                    else:
                        st.error("Username already exists. Please pick a different Username.")

# App Control Flow
if st.session_state["logged_in"]:
  portal.show_portal()
else:
  show_login_signup()
