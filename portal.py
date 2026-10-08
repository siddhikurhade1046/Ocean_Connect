import database as db
import streamlit as st
from datetime import date
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from constants import COASTAL_CITIES

@st.cache_data
def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="ocean_connect_app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    clean_loc = str(location_name).strip()
    try:
        data = geocode(clean_loc)
        if not data and "," in clean_loc:
            fallback = clean_loc.split(",")[-1].strip() + ", India"
            data = geocode(fallback)
        if data:
            return (data.latitude, data.longitude)
    except Exception:
        pass
    return None

def show_india_map():
    st.subheader("🇮🇳 All-India Ocean Clean-up Map")
    st.write("Explore active clean-up drives happening across India's coastline.")

    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    events = db.get_all_events()

    if events:
        for ev in events:
            raw_location = ev[3]  # Location field
            if not raw_location:
                continue

            # 🔥 Use the cached get_coordinates helper function
            coords = get_coordinates(raw_location)

            if coords:
                folium.Marker(
                    location=coords,
                    popup=f"<b>{ev[0]}</b><br>Type: {ev[2]}<br>Date: {ev[4]}<br>Location: {raw_location.strip()}",
                    tooltip=ev[0],
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)

    # returned_objects=[] prevents map panning/zooming from triggering full Streamlit reruns
    st_folium(m, width=700, height=500, returned_objects=[])

def show_portal():
  # --------------------------------------------------
  # SESSION & SIDEBAR SETUP
  # --------------------------------------------------
  if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access the portal.")
    return

  username = st.session_state.get("username", "")
  role = st.session_state.get("role", "")

  # 📍 Sidebar Logo
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

    tab1, tab2, tab3 = st.tabs(["Host New Event", "My Hosted Events", "All-India Map"])

    with tab1:
      st.subheader("Create a New Ocean Event")
      with st.form("create_event_form"):
        title = st.text_input("Event Title")
        activity_type = st.text_input(
            "Activity Type", 
            placeholder="e.g., Beach Clean-up, Mangrove Planting, Coral Restoration"
        )
        location = st.text_input(
            "Location", placeholder="e.g., Juhu Beach, Mumbai or Nerul, Navi Mumbai"
        )
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
          st.cache_data.clear()
          st.success("Event created successfully!")
        else:
          st.warning("Please fill in all event details.")

    with tab2:
       st.markdown("### 📋 Your Hosted Events & Participant Management")
       my_events = db.get_ngo_events(username)

       if my_events:
        for event_idx, ev in enumerate(my_events):
            # Unpack event details
            ev_title, activity_type, location, event_date, description = ev
            
            with st.expander(f"📌 {ev_title} ({activity_type})"):
                st.write(f"**Location:** {location} | **Date:** {event_date}")
                st.write(f"**Description:** {description}")
                st.divider()

                st.markdown("#### 👥 Registered Volunteers")

                volunteers = db.get_event_volunteers(ev_title)

                if volunteers:
                    selected_volunteers = []

                    for idx, v in enumerate(volunteers):
                        v_name, v_email, v_dob, v_age, p_name, p_cont, p_email = v

                        col_info, col_select = st.columns([3, 1])
                        with col_info:
                            st.write(
                                f"👤 **{v_name}** ({v_email}) | DOB: {v_dob} |"
                                f" Age: {v_age}"
                            )

                            try:
                              safe_age = int(v_age) if v_age is not None else 0
                            except (ValueError, TypeError):
                              safe_age = 0

                            if safe_age < 23:
                              st.caption(
                                  f"⚠️ Parent Consent: {p_name} | Phone:"
                                  f" {p_cont} | Email: {p_email}"
                              )

                        with col_select:
                            is_selected = st.checkbox(
                                "Select",
                                key=f"sel_{event_idx}_{idx}_{ev_title}_{v_email}",
                            )
                            if is_selected:
                              selected_volunteers.append(v_email)

                    st.divider()

                    if selected_volunteers:
                      emails_str = ",".join(selected_volunteers)
                      mail_subject = f"Update regarding OceanConnect Event: {ev_title}"
                      mail_body = (
                          "Hello,%0D%0A%0D%0AYou have been"
                          f" selected/shortlisted for the event '{ev_title}'."
                          " See you there!%0D%0A%0D%0ARegards,"
                          f"%0D%0A{username}"
                      )

                      mail_to_url = f"mailto:{emails_str}?subject={mail_subject}&body={mail_body}"

                      st.markdown(
                          f'<a href="{mail_to_url}" target="_self">'
                          '<button style="background-color:#4CAF50;'
                          " color:white; padding:10px 20px; border:none;"
                          ' border-radius:5px; cursor:pointer;">'
                          "📧 Send Email to Selected Volunteers"
                          f" ({len(selected_volunteers)})"
                          "</button></a>",
                          unsafe_allow_html=True,
                      )
                else:
                    st.info("No volunteers have registered for this event yet.")
       else:
            st.info("You haven't posted any events yet.")

    with tab3:
       show_india_map()

  # --------------------------------------------------
  # VOLUNTEER / PARTICIPANT VIEW
  # --------------------------------------------------
  else:
    st.title("🏄 Volunteer Dashboard")
    
    # Created 2 tabs so volunteers can explore vs view registered events
    v_tab1, v_tab2 = st.tabs(["🌏 Explore Events", "📋 My Registered Events"])

    # ----------------------------------------------
    # TAB 1: Explore & Register
    # ----------------------------------------------
    with v_tab1:
        st.subheader("🌏 Explore & Register for Ocean Events")
        show_india_map()
        
        st.divider()
        
        st.subheader("📍 Find Events Near Your Location")
        user_city = st.text_input(
            "🔎 Filter events by city or location name:", 
            placeholder="e.g., Alibaug, Thane, Surat, or leave blank for all",
            key="vol_filter_input"
        )
        
        all_events = db.get_all_events()

        if user_city.strip() and all_events:
           search_term = user_city.strip().lower()
           events = [
            ev for ev in all_events 
            if ev[3] and search_term in str(ev[3]).lower()
        ]
        else:
           events = all_events
        
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
                    st.cache_data.clear()
                    st.success(f"Successfully registered for {ev_title}! 🎉")
                    st.session_state[reg_key] = False
                    st.rerun()

              st.markdown("---")
        else:
          st.info("No active ocean events available right now. Check back later!")

    # ----------------------------------------------
    # TAB 2: My Registered Events
    # ----------------------------------------------
    with v_tab2:
        st.subheader("📌 Events You Have Registered For")
        
        # Check if the database function exists to fetch user's registered events
        if hasattr(db, "get_user_registered_events"):
            user_events = db.get_user_registered_events(username)
            if user_events:
                for ev in user_events:
                    ev_title, organizer, activity, location, ev_date, desc = ev
                    with st.expander(f"✅ {ev_title} ({activity}) — Date: {ev_date}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"📍 **Location:** {location}")
                            st.write(f"👤 **Organizer:** {organizer}")
                        with col2:
                            st.write(f"📅 **Scheduled Date:** {ev_date}")
                        st.write(f"📝 **Description:** {desc}")
                        st.success("Status: **Registered Participant**")
            else:
                st.info("You haven't joined any ocean events yet! Go to the 'Explore Events' tab to find one.")
        else:
            st.warning("Database function `get_user_registered_events` is missing in `database.py`. Please make sure to add it.") 