import database as db
import streamlit as st
from datetime import date

def show_portal():
  # --------------------------------------------------
  # SESSION & SIDEBAR SETUP
  # --------------------------------------------------
  if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access the portal.")
    return

  username = st.session_state.get("username", "")
  role = st.session_state.get("role", "")

  # 📍 Sidebar Logo (Har page/tab par visible rehne ke liye)
  st.sidebar.image("ocean logo.png", width=180)

  st.sidebar.title(f"Welcome, {username}!")
  st.sidebar.info(f"Role: **{role}**")

  # Logout button in sidebar
  if st.sidebar.button("Log Out"):
    for key in list(st.session_state.keys()):
      del st.session_state[key]
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.rerun()

  # --------------------------------------------------
  # ORGANIZER / HOST VIEW
  # --------------------------------------------------
  if role == "Organizer":
    st.title("🌊 Organizer Portal")

    tab1, tab2 = st.tabs(["Host New Event", "My Hosted Events"])

    with tab1:
      st.subheader("Create a New Ocean Event")
      with st.form("create_event_form"):
        title = st.text_input("Event Title")
        activity_type = st.selectbox(
            "Activity Type",
            [
                "Beach Clean-up",
                "Mangrove Conservation",
                "Coral Reef Protection",
                "Ocean Literacy Workshop",
            ],
        )
        location = st.text_input("Location")
        event_date = st.date_input("Event Date")
        description = st.text_area("Event Description")

        submitted = st.form_submit_button("Publish Event")
      if submitted:
        if title and activity_type and location and description:
          db.add_event(
              title,
              username,
              activity_type,
              location,
              event_date,
              description,
          )
          st.success("Event created successfully!")
        else:
          st.warning("Please fill in all event details.")

    with tab2:
      st.markdown("### 📋 Your Hosted Events & Participant Management")
      my_events = db.get_ngo_events(username)

      if my_events:
        for event_idx, ev in enumerate(my_events):
          event_title = ev
          with st.expander(f"📌 Event: {event_title} ({ev})"):
            st.write(f"**Location:** {ev} | **Date:** {ev}")
            st.markdown("#### 👥 Registered Volunteers")

            volunteers = db.get_event_volunteers(event_title)
            selected_volunteers = []

            if volunteers:
              # Use enumerate to guarantee unique keys per row
              for idx, v in enumerate(volunteers):
                v_name, v_email, v_dob, v_age, p_name, p_cont, p_email = v

                col_info, col_select = st.columns()
                with col_info:
                  st.write(
                      f"**{v_name}** ({v_email}) | DOB: {v_dob} | Age: {v_age}"
                  )
                  try:
                    safe_age = int(v_age) if v_age is not None else 0
                  except (ValueError, TypeError):
                    safe_age = 0

                  if safe_age < 23:
                    st.caption(
                        f"⚠️ Parent Consent: {p_name} | Phone: {p_cont} | Email:"
                        f" {p_email}"
                    )

                with col_select:
                  # Unique key using idx, event_title, and v_email
                  is_selected = st.checkbox(
                      "Select",
                      key=f"sel_{event_idx}_{idx}_{event_title}_{v_email}",
                  )
                  if is_selected:
                    selected_volunteers.append(v_email)
                st.divider()

              if selected_volunteers:
                emails_str = ",".join(selected_volunteers)
                mail_subject = (
                    f"Update regarding OceanConnect Event: {event_title}"
                )
                mail_body = (
                    f"Hello,%0D%0A%0D%0AYou have been selected/shortlisted for"
                    f" the event '{event_title}'. See you"
                    "%0D%0A%0D%0ARegards"
                )
                mail_to_url = f"mailto:{emails_str}?subject={mail_subject}&body={mail_body}"

                st.markdown(
                    f'<a href="{mail_to_url}" target="_self"><button'
                    ' style="background-color:#4CAF50; color:white; padding:10px'
                    ' 20px; border:none;">Send Email to Selected'
                    "</button></a>",
                    unsafe_allow_html=True,
                )
            else:
              st.info("No volunteers have registered for this event yet.")
      else:
        st.info("You haven't posted any events yet.")

  # --------------------------------------------------
  # VOLUNTEER / PARTICIPANT VIEW
  # --------------------------------------------------
  else:
    st.subheader("🌐 Explore & Register for Ocean Events")
    events = db.get_all_events()

    if events:
      for idx, ev in enumerate(events):
        ev_title, organizer, activity, location, ev_date, desc = ev
        with st.container():
          st.markdown(f"### 🌊 {ev_title}")

          col_type, col_loc, col_date = st.columns(3)
          with col_type:
            st.info(f"🏷️ **Type:**\n{activity}")
          with col_loc:
            st.success(f"📍 **Location:**\n{location}")
          with col_date:
            st.warning(f"📅 **Date:**\n{ev_date}")

          st.write(f"**Hosted by:** {organizer}")
          st.write(f"**Description:** {desc}")

          # Session state toggle for registration form visibility
          reg_key = f"show_reg_{idx}_{ev_title}"
          if reg_key not in st.session_state:
            st.session_state[reg_key] = False

          if st.button("Join Activity", key=f"join_{idx}_{ev_title}"):
            st.session_state[reg_key] = not st.session_state[reg_key]

          if st.session_state[reg_key]:
            st.markdown("---")
            st.markdown(f"#### 📝 Registration Form for: {ev_title}")

            vol_name = st.text_input("Full Name", key=f"fn_{idx}")
            dob = st.date_input(
                "Date of Birth",
                min_value=date(1940, 1, 1),
                max_value=date.today(),
                key=f"dob_{idx}",
            )

            # Calculate age dynamically
            today = date.today()
            age = (
                today.year
                - dob.year
                - ((today.month, today.day) < (dob.month, dob.day))
            )
            st.info(f"Calculated Age: **{age}**")

            vol_email = st.text_input("Email ID", key=f"em_{idx}")
            phone = st.text_input("Phone Number", key=f"ph_{idx}")
            residence = st.text_area("Residential Address", key=f"res_{idx}")

            parent_name, parent_contact, parent_email = "", "", ""
            if age < 23:
              st.warning(
                  "⚠️ Since you are under 23 years old, parent/guardian consent"
                  " details are required."
              )
              parent_name = st.text_input(
                  "Parent/Guardian Full Name", key=f"pn_{idx}"
              )
              parent_contact = st.text_input(
                  "Parent/Guardian Contact Number", key=f"pc_{idx}"
              )
              parent_email = st.text_input(
                  "Parent/Guardian Email ID", key=f"pe_{idx}"
              )

            if st.button(
                "Confirm Registration", key=f"submit_reg_{idx}_{ev_title}"
            ):
              if not vol_name or not vol_email or not phone:
                st.error("Please fill in all mandatory personal details.")
              elif age < 23 and (
                  not parent_name or not parent_contact or not parent_email
              ):
                st.error(
                    "All parent/guardian fields are compulsory for"
                    " participants under 23."
                )
              else:
                # Successfully passing age along with all parameters
                db.register_volunteer(
                    ev_title,
                    username,
                    vol_name,
                    vol_email,
                    str(dob),
                    age,
                    parent_name,
                    parent_contact,
                    parent_email,
                )
                st.success(f"Successfully registered for {ev_title}! 🎉")
                st.session_state[reg_key] = False
                st.rerun()

          st.markdown("---")
    else:
      st.info("No active ocean events available right now. Check back later!")
