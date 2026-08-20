import streamlit as st
import sqlite3
import pandas as pd

# Setting up the page configuration
st.set_page_config(page_title="OceanConnect")

#Initializeing DataBase
db.init_db()

#Initalize Sessions in State
if"logged_in" not in st.sessions_state:
    st.sessions_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

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
                if db.verify_user(username,password):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state("Login Successful !!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            elif choice == "Sign Up":
                st.subheader("Create a new Account ")
                with st.form("Signup_form"):
                    new_user = st.text_input("Choose Username")
                    new_pass = st.text_input("Choose Password",type = "password")
                    confirm_pass = st.text_input("Choice Password",type = "password")
                    submit = st.form_submit_button("Submit Up")

                    if submit :
                        if not new_user or not new_pass:
                            st.warning("Please fill out all the feilds.")
                        elif new_pass != confirm_pass:
                            st.error("Password not matched ")
                        else:
                            if db.register_user(new_user,new_pass):
                                st.success("Account created successfully !! Go to the Login Page to proceed with the Login.")
                            else:
                                st.error("Username already exisits. Plese pick a different Username.")
#App Control
if st.session_state["logged_in"]:
    portal.show_portal()
else:
    show_login_signup()