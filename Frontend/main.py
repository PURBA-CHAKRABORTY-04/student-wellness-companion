import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation 

# The URLs of your running FastAPI backend
BACKEND_URL = "http://127.0.0.1:8000/chat"
JOURNAL_URL = "http://127.0.0.1:8000/journal"

# Dummy user ID until we add a real login system
USER_ID = "student_123"

st.set_page_config(page_title="Student Wellness Hub", page_icon="🌱", layout="wide")

# --- SIDEBAR: Mood & Journal ---
with st.sidebar:
    st.title("Check-In 🌿")
    # --- NEW: Location Services ---
    st.subheader("📍 Your Location")
    st.write("Click below to find nearby support:")
    geo = streamlit_geolocation()
    # Default city
    city_name = ""
    if geo and geo.get('latitude'):
        try:
            lat = geo['latitude']
            lon = geo['longitude']
            # Reverse geocode: turn Lat/Lon into a city name using OpenStreetMap
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            res = requests.get(url, headers={'User-Agent': 'MentalWellnessApp/1.0'}).json()
            # Extract the city or state district
            address = res.get('address', {})
            city_name = address.get('city', address.get('state_district', address.get('county', 'Unknown')))
        except Exception as e:
            city_name = "Could not detect city"

    # The text box auto-fills with their real city, but they can still edit it
    user_location = st.text_input("City for local recommendations:", value=city_name)
    st.markdown("---")

    # ==========================================
    # 🚨 1. NEW: CALENDAR TOGGLE ADDED HERE 🚨
    # ==========================================
    st.subheader("📅 Schedule Sync")
    sync_calendar = st.toggle("Connect Google Calendar")
    
    # This simulates pulling data from Google API
    student_schedule = []
    if sync_calendar:
        # A heavy simulated schedule
        student_schedule = ["Data Structures", "Advanced Calculus", "Physics Lab", "Study Group"]
        st.success(f"Synced! Found {len(student_schedule)} events today.")
        
    st.markdown("---")
    # ==========================================

    selected_mood = st.radio(
        "How are you feeling right now?",
        ["Happy ☀️", "Neutral ☁️", "Stressed 📈", "Anxious 🌪️", "Sad 🌧️", "Angry 🌩️"]
    )
    
    st.markdown("---")
    
    st.subheader("Daily Journal 📔")
    journal_entry = st.text_area(
        "Express your feelings safely here. This is just for you.",
        height=150,
        placeholder="Today I felt overwhelmed because..."
    )
    
    if st.button("Save Journal Entry"):
        if journal_entry:
            try:
                response = requests.post(JOURNAL_URL, json={
                    "user_id": USER_ID,
                    "mood": selected_mood,
                    "content": journal_entry
                })
                if response.status_code == 200:
                    st.success("Journal saved securely to the cloud! ☁️")
                else:
                    st.error("Failed to save to database.")
            except requests.exceptions.ConnectionError:
                st.error("Backend is offline. Cannot save.")
        else:
            st.warning("Please write something before saving.")
            
    st.markdown("---")
    
    st.subheader("Your Past Entries 📖")
    if st.button("Load Past Entries"):
        try:
            res = requests.get(f"{JOURNAL_URL}/{USER_ID}")
            if res.status_code == 200:
                entries = res.json()
                if entries:
                    for entry in entries:
                        date_str = entry['timestamp'][:10]
                        st.info(f"**{date_str}** | Mood: {entry['mood']}\n\n{entry['content']}")
                else:
                    st.write("No entries found. Start journaling above!")
        except Exception as e:
            st.error("Could not fetch entries.")

# --- MAIN PAGE: The Chat Interface ---
st.title("Your Wellness Companion")
st.write(f"**Current state:** You indicated you are feeling **{selected_mood.split()[0]}**. I'm here to support you.")

# --- NEW: Load Chat History from Supabase Database ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    try:
        # Ask the backend for past messages
        res = requests.get(f"{BACKEND_URL}/{USER_ID}")
        if res.status_code == 200:
            history = res.json()
            for msg in history:
                st.session_state.messages.append({"role": msg["role"], "content": msg["content"]})
    except Exception as e:
        pass # If the backend is off, just start with an empty chat

# Display all messages (past and present)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT ---
if user_input := st.chat_input("Ask about stress, study tips, or your mental health..."):
    
    with st.chat_message("user"):
        st.markdown(user_input)
    # Temporarily add to screen
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.spinner("Thinking..."):
            # ==========================================
            # 🚨 2. NEW: SCHEDULE ADDED TO PAYLOAD 🚨
            # ==========================================
            response = requests.post(BACKEND_URL, json={
                "user_id": USER_ID,
                "user_message": user_input,
                "current_mood": selected_mood,
                "location": user_location, 
                "schedule": student_schedule  # <--- THIS IS THE CRITICAL NEW LINE
            })
            # ==========================================
            
        if response.status_code == 200:
            data = response.json()
            bot_reply = data.get("response", "I'm here for you.")
            
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
            # Temporarily add to screen (it's already saved in the database!)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        else:
            st.error(f"Backend Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
         st.error("Cannot connect to the backend. Is your FastAPI server running?")