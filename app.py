import base64
import base64
import sqlite3
import database as db
import pandas as pd
import portal
import streamlit as st
from constants import COASTAL_CITIES

@st.cache_data
def add_bg_from_local(image_file):
  try:
    with open(image_file, "rb") as f:
      encoded_string = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        /* Main website background */
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Styling for form cards to keep text readable */
        div[data-testid="stForm"] {{
            background-color: rgba(255, 255, 255, 0.88);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
  except FileNotFoundError:
    st.error(
        f"Background image '{image_file}' not found. Please check the file name"
        " and location."
    )

# Configure Streamlit page settings
st.set_page_config(page_title="OceanConnect", page_icon="🌊")

# Set the background image (Specify your image file name here)
add_bg_from_local("ocean bg.png")

# Initialize the SQLite database
db.init_db()

# Initialize session state variables
# Initialize session state variables
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
if "username" not in st.session_state:
  st.session_state["username"] = ""
if "role" not in st.session_state:
  st.session_state["role"] = ""


def show_login_signup():
  # Display the sidebar logo (Specify your logo file name here)
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
        st.success(f"Login successful as {user_role}!")
        st.success(f"Login successful as {user_role}!")
        st.rerun()
      else:
        st.error("Invalid username or password.")

  elif choice == "Sign Up":
    st.subheader("Create a new account")
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
        st.error("Passwords do not match.")
      else:
        if db.register_user(new_user, new_pass, role):
          st.session_state["logged_in"] = True
          st.session_state["username"] = new_user
          st.session_state["role"] = role
          st.success("Account created successfully!")
          st.rerun()
        else:
          st.error("Username already exists. Please choose a different one.")

# Application control flow
# Application control flow
if st.session_state["logged_in"]:
  portal.show_portal()
else:
  show_login_signup()