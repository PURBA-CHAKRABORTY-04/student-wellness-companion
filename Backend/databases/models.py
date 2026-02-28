from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# We are using SQLite for now because it saves everything in a simple, local file.
# This is perfect for local testing before deploying to Heroku.
DATABASE_URL = "sqlite:///./mental_health.db"

# 1. Create the database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 2. Create a session maker (this is how our API will "talk" to the database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Create a Base class for our models
Base = declarative_base()

# 4. Define the Journal Entry table
class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # To identify which student wrote it
    mood = Column(String)                 # E.g., "Anxious", "Happy"
    content = Column(Text)                # The actual journal text
    timestamp = Column(DateTime, default=datetime.utcnow) # Automatically records the time

# 5. Tell SQLAlchemy to actually create the file and tables if they don't exist yet
# ... (Keep your existing JournalEntry code up here)

# Add this new table for Chat Memory
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # To identify who is chatting
    role = Column(String)                 # 'user' or 'assistant'
    content = Column(Text)                # The message text
    timestamp = Column(DateTime, default=datetime.utcnow) 

# 5. Tell SQLAlchemy to create the tables in Supabase
Base.metadata.create_all(bind=engine)
#Base.metadata.create_all(bind=engine)