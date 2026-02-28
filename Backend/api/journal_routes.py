from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from databases.models import SessionLocal, JournalEntry

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class JournalCreate(BaseModel):
    user_id: str
    mood: str
    content: str

@router.post("/journal")
def create_entry(entry: JournalCreate, db: Session = Depends(get_db)):
    try:
        new_entry = JournalEntry(user_id=entry.user_id, mood=entry.mood, content=entry.content)
        db.add(new_entry)
        db.commit()          
        db.refresh(new_entry) 
        return {"status": "success", "message": "Journal saved!", "id": new_entry.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not save to database.")

@router.get("/journal/{user_id}")
def get_entries(user_id: str, db: Session = Depends(get_db)):
    entries = db.query(JournalEntry).filter(JournalEntry.user_id == user_id).order_by(JournalEntry.timestamp.desc()).all()
    return entries