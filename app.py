import streamlit as st
import sqlite3
import pandas as pd
import database as db
import portal
import folium
from streamlit_folium import st_folium


# Setting up the page configuration
st.set_page_config(page_title="OceanConnect")

#Initializeing DataBase
db.init_db()

#Initalize Sessions in State
# Initialize Sessions in State
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = ""

def show_login_signup():
    st.title("Ocean Connect")
    st.caption("Connecting people to ocean- realated activies")

    menu = ["Login","Sign Up"]
    choice = st.sidebar.selectbox("Navigation", menu, key="super_unique_login_nav_choice_999")

    if choice == "Login":
        st.subheader("Log into your account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Log In")

            if submit:
                user_role =  db.verify_user(username,password)
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
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")

            # Role Selection Widget
            role = st.radio("Account Type", ["Volunteer", "Organizer"])
            role_value = "Organizer" if role == "Organizer" else "Volunteer"

            submit = st.form_submit_button("Sign Up")

            if submit:
                if not new_user or not new_pass:
                    st.warning("Please fill out all fields.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                else:
                    if db.register_user(new_user, new_pass, role_value):
                        # Automatically log in and redirect upon successful registration
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = new_user
                        st.session_state["role"] = role_value
                        st.success("Account created successfully! Redirecting...")
                        st.rerun()
                    else:
                        st.error("Username already exists.")
#App Control
if st.session_state["logged_in"]:
    portal.show_portal()
else:
    show_login_signup()