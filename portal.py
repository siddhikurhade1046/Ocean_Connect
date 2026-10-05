import datetime
import streamlit as st
import database as db 

def show_portal():

    if st.sidebar.button("Log Out"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.rerun()

    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in to access the portal.")
        return

    username = st.session_state.get("username","")
    role  = st.session_state.get("role","")

    st.title("Ocean Connect Website")
    st.markdown(f"Logged in as: **{st.session_state['username']}** (`{st.session_state['role']}`)")

    st.markdown("<h1 style='text-align: center;'>Welcome to OceanConnect</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555555;'>Events Coming Soon</h3>", unsafe_allow_html=True)

    if st.session_state["role"] == "Organizer":
        st.subheader("Organizer Hub")
        tab1, tab2 = st.tabs(["Host New Activity","My Hosted Events"])

        with tab1:
            st.markdown("### Post an Ocean Event")
            with st.form("create_event_form"):
                title = st.text_input("Event Title")
                activity_type = st.text_input("Activity Type " )
                location = st.text_input("Location / Beach  Name")
                date = st.date_input("Event Date")
                description = st.text_area("Description & Requirements")

                submit_event = st.form_submit_button("Publish Event")

            if submit_event:
            
             if title and activity_type and location and description:
                        db.add_event(title , st.session_state["username"], activity_type, location,date,description)
                        st.success("Event created successfully !!!")
             else:
                        st.warning("Please fill in all event details.")

        with tab2:
            st.markdown("### Your Active Listings")
            my_events = db.get_ngo_events(username)
            if my_events :
                for ev in my_events:
                    with st.expander(f" {ev[0]} ({ev[1]})"): 
                        st.write(f"**Location:** {ev[2]}")
                        st.write(f"**Date:**{ev[3]}")
                        st.write(f"**Details:** {ev[4]}")
            else:
                st.info("You haven't posted any events yet.")
    else:
        st.subheader("🏄 Explore & Register for Ocean Events")
        events = db.get_all_events()

        if events:
            for idx, ev in enumerate(events):
                with st.container():
                    st.markdown(f"### {ev[0]}")
                    col1, col2, col3 = st.columns(3)
                    col1.caption(f"**Type:** {ev[2]}")
                    col2.caption(f"**Location:** {ev[3]}")
                    col3.caption(f"**Date:** {ev[4]}")
                    st.caption(f"Hosted by: **{ev[1]}**")
                    st.write(ev[5])

                    # Expander (WITHOUT st.form) so age calculates live
                    with st.expander("📝 Register for this Event"):
                        st.write(f"**Registering for:** {ev[0]}")
                        
                        vol_name = st.text_input("Full Name", key=f"name_{idx}_{ev[0]}")
                        vol_email = st.text_input("Email Address", key=f"email_{idx}_{ev[0]}")
                        dob = st.date_input("Date of Birth", min_value=datetime.date(1950, 1, 1), max_value=datetime.date.today(), key=f"dob_{idx}_{ev[0]}")

                        # Calculating Age dynamically
                        today_date = datetime.date.today()
                        age = today_date.year - dob.year - ((today_date.month, today_date.day) < (dob.month, dob.day))
                        st.info(f"Calculated Age: **{age} years old**")

                        parent_name = ""
                        parent_contact = ""
                        parent_email = ""

                        if age < 23:
                            st.warning("⚠️ Participants under 23 years old require parental/guardian consent.")
                            parent_name = st.text_input("Parent / Guardian Full Name *", key=f"pname_{idx}_{ev[0]}")
                            parent_contact = st.text_input("Parent / Guardian Contact Number *", key=f"pcont_{idx}_{ev[0]}")
                            parent_email = st.text_input("Parent / Guardian Email *", key=f"pemail_{idx}_{ev[0]}")

                        # Standard button handles submission dynamically outside a form
                        if st.button("Confirm Registration", key=f"submit_reg_{idx}_{ev[0]}"):
                            if not vol_name or not vol_email:
                                st.error("Please fill in your Name and Email.")
                            elif age < 23 and (not parent_name or not parent_contact or not parent_email):
                                st.error("All parent/guardian fields are compulsory for participants under 23.")
                            else:
                                db.register_volunteer(ev[0], username, vol_name, vol_email, str(dob), parent_name, parent_contact, parent_email)
                                st.success(f"Successfully registered for {ev[0]}! 🎉")

                    st.divider()
        else:
            st.info("No upcoming events found. Check back later!")
  

if st.sidebar.button("Log Out"):
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.rerun()
        