import streamlit as st
import sqlite3
import pandas as pd
import database as db
import portal

# Setting up the page configuration
st.set_page_config(page_title="OceanConnect")

#Initializeing DataBase
db.init_db()

#Initalize Sessions in State
if"logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = ""

#Screen before the login/Sign up
if st.session_state["logged _in"]:
    st.title("Ocean Connect DashBoard")
    st.success(f"Successfully logged in a **{st.session_state['username']}**!")
    st.info(f"Account Type: **{st.session_state['role']}**")

    if st.button("Log Out"):
        st.session_state["Logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] =""
        st.rerun()


def show_login_signup():
    st.title("Ocean Connect")
    st.caption("Connecting people to ocean- realated activies")

    menu = ["Login","Sign Up"]
    choice = st.sidebar.selectbox("Navigation",menu)

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
                    st.session_state["role"] = username
                    st.session_state(f"Login Successful as {user_role} !!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            elif choice == "Sign Up":
                st.subheader("Create a new Account ")
                with st.form("Signup_form"):
                    new_user = st.text_input("Choose Username")
                    new_pass = st.text_input("Choose Password",type = "password")
                    confirm_pass = st.text_input("Choice Password",type = "password")

                    role = st.radio("Account Type",["Volunteer","Organizer"])
                    role_value = "Organizer" if "Organizer" in role else "Volunteer"

                    submit = st.form_submit_button("Sign Up")

                    if submit :
                        role = "Organizer" if "Organizer" in role else "Volunteer"
                        if not new_user or not new_pass:
                            st.warning("Please fill out all the fields.")
                        elif new_pass != confirm_pass:
                            st.error("Password not matched ")
                        else:
                            if db.register_user(new_user,new_pass,role_value):
                                st.success("Account created successfully !! Go to the Login Page to proceed with the Login.")
                            else:
                                st.error("Username already exisits. Plese pick a different Username.")
#App Control
if st.session_state["logged_in"]:
    portal.show_portal()
else:
    show_login_signup()