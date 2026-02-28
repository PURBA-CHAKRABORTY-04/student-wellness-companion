from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.llm_engine import generate_chat_response
from databases.models import SessionLocal, ChatMessage
import requests

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatRequest(BaseModel):
    user_id: str
    user_message: str
    current_mood: str
    location: str = "Unknown" 
    schedule: list = []  # <--- NEW! Default is an empty list
# ==========================================
# 🚨 AGENT 1: CRISIS DETECTION INTERCEPTOR
# ==========================================
def crisis_agent(text: str) -> str:
    # "hurt myself" is safely in this list!
    crisis_keywords = ["want to die", "kill myself", "can't take it anymore", "end it", "suicide", "giving up", "hurt myself"]
    text_lower = text.lower()
    
    if any(word in text_lower for word in crisis_keywords):
        return (
            "🚨 **CRISIS ALERT: You are not alone. Help is available right now.** 🚨\n\n"
            "Please, I urge you to reach out to someone immediately:\n"
            "📞 **AASRA (24x7 Helpline):** 9820466726\n"
            "📞 **Kiran (Mental Health Helpline):** 1800-599-0019\n"
            "👥 **Next Step:** Please call a trusted friend, family member, or go to the nearest hospital.\n\n"
            "*Your life has immense value. Please make the call.*"
        )
    return None
# 📅 AGENT 3: CALENDAR OVERLOAD DETECTOR
# ==========================================
def calendar_agent(schedule: list) -> str:
    # If no calendar is synced, do nothing
    if not schedule:
        return ""
        
    # Logic: If the student has 3 or more events, trigger an overload warning
    total_events = len(schedule)
    if total_events >= 3:
        # We dynamically grab the names of their classes to make it sound personal
        event_names = ", ".join(schedule[:2]) 
        return (
            f"\n\n---\n📅 **Calendar Insight:** I noticed you have a very heavy schedule today with {total_events} back-to-back events "
            f"(including {event_names}). \n\n"
            "🚨 **Overload Warning:** Your brain needs time to consolidate information. "
            "**Suggested Action:** Please block out 20 minutes for a screen-free walk right after your second class. Hydrate and step away from the desk!"
        )
    return ""
# ==========================================
# 🗺️ AGENT 2: LIVE RESOURCE RECOMMENDATION (Upgraded)
# ==========================================
def recommendation_agent(mood: str, location: str) -> str:
    if not location or location == "Unknown" or location == "Could not detect city":
        return ""
        
    if any(m in mood for m in ["Anxious", "Stressed", "Sad"]):
        search_term = "yoga"
        emoji = "🧘‍♀️"
    elif "Angry" in mood:
        search_term = "gym"
        emoji = "🏋️‍♂️"
    else:
        return "" 

    try:
        headers = {'User-Agent': 'MentalWellnessApp/2.0'}
        # This uses the new comma format that Nominatim map API prefers
        url = f"https://nominatim.openstreetmap.org/search?q={search_term},{location}&format=json&limit=3"
        
        # Print the exact URL to the terminal so we can see what it's searching!
        print(f"🌍 MAP SEARCH URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            results = response.json()
            # Print the results to the terminal so we can see if it found anything
            print(f"🗺️ MAP RESULTS FOUND: {len(results)}")
            
            if len(results) > 0:
                places_text = f"\n\n---\n📍 **Live Local Support in {location}:**\n"
                
                for place in results:
                    name = place.get('name', '')
                    if not name:
                        name = place.get('display_name', '').split(',')[0]
                    places_text += f"* {emoji} **{name}**\n"
                    
                return places_text
    except Exception as e:
        print(f"Location API Error: {e}")
        
    # Safely fall back to this message if 0 results
    return f"\n\n---\n📍 **Tip:** Open Google Maps and search for '{search_term}' near {location}."

# --- Endpoint to load past chat history ---
@router.get("/chat/{user_id}")
def get_chat_history(user_id: str, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(ChatMessage.timestamp.asc()).all()
    return messages

# ==========================================
# 🧠 THE MAIN CHAT ENDPOINT (The Switchboard)
# ==========================================
@router.post("/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    user_msg = ChatMessage(user_id=request.user_id, role="user", content=request.user_message)
    db.add(user_msg)
    db.commit()

    try:
        # --- EXECUTE AGENT 1: Crisis Check ---
        crisis_response = crisis_agent(request.user_message)
        
        if crisis_response:
            final_reply = crisis_response
        else:
            # --- NORMAL FLOW: Call the LLM ---
            ai_reply = generate_chat_response(
                user_message=request.user_message,
                current_mood=request.current_mood
            )
            
            # --- EXECUTE AGENT 2: Add Recommendations ---
            local_resources = recommendation_agent(request.current_mood, request.location)
            # --- EXECUTE AGENT 3: Calendar Check ---
            calendar_warning = calendar_agent(request.schedule)
            final_reply = ai_reply + calendar_warning+local_resources

        bot_msg = ChatMessage(user_id=request.user_id, role="assistant", content=final_reply)
        db.add(bot_msg)
        db.commit()

        return {"type": "chat", "response": final_reply}
        
    except Exception as e:
        print(f"AI Error: {e}")
        return {"type": "error", "response": "I'm having a little trouble connecting right now. Please try again."}