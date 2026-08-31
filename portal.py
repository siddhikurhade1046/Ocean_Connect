import streamlit as st
import database as db

def show_portal():
    st.title("Ocean Connect Website")
    st.write(f"Logged in as:**{st.session_state['username']}**(`{st.session_state['role']}`) ")

    if st.session_state["role"] == "Organizer":
        st.subheader("Organizer Hub")
        tab1, tab2 = st.tabs(["Host New Activity","My Hosted Events"])

        with tab1:
            st.markdown("### Post an Ocean Event")
            with st.form("create_event_form"):
                title = st.text_input("Event Title")
                activity_type = st.text("Activity Type " )

                location = st.text_input("Location / Beach  Name")
                date = st.date_input("Event Date")
                description = st.text_area("Description & Requirements")

                submit_event = st.form_submit_button("Publish Event")

                if submit_event:
                    if title and activity_type and location and description:
                        db.add_event(title , st.session_state["Username"], activity_type, location,date,description)
                        st.success("Event created successfully !!!")
                    else:
                        st.warning("Please fill in all event details.")

        with tab2:
            st.markdown("### Your Active Listings")
            my_events = db.get_ngo_events(st.session_state["Username"])
            if my_events :
                for ev in my_events:
                    with st.expaner(f" {ev[0]} ({ev[1]})"): 
                        st.write(f"**Location:** {ev[2]}")
                        st.write(f"**Date:**{ev[3]}")
                        st.write(f"**Details:** {ev[4]}")
            else:
                st.info("You haven't posted any events yet.")
    else:
        st.subheader("Explore & Register for Ocean Events")            
        events = db.get_all_events()

        if events:
            for ev in events:
                with st.container():
                    # ev format: (title, ngo_username, activity_type, location, event_date, description)
                    st.markdown(f"### {ev[0]}")
                    col1, col2, col3 = st.columns(3)
                    col1.caption(f"**Type:** {ev[2]}")
                    col2.caption(f"**Location:** {ev[3]}")
                    col3.caption(f"**Date:** {ev[4]}")
                    st.caption(f"Hosted by :**{ev[1]}**")
                    st.write(ev[5])

                    if st.button("Join Activity", key =f"join{ev[0]}_{ev[1]}"):
                        st.success(f"You have successfully registered for {ev[0]}!!")                                      
                    st.divider()
        else:
            st.info("No Upcoming events found. Check back later!!")  

if st.sidebar._button("Log Out"):
    st.session_state("looged_in") = False
    st.session_state("username") = ""
    st.session_state("role") = ""
    st.rerun()
        