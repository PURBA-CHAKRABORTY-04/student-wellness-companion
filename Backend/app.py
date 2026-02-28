from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat_routes import router as chat_router
from api.journal_routes import router as journal_router 

# 1. Initialize the main application
app = FastAPI(title="Student Wellness Companion API")

# 2. Add Security (CORS) so Streamlit is allowed to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# 3. Plug in the actual routes!
app.include_router(chat_router)
app.include_router(journal_router) 

# 4. A simple root endpoint to verify it's awake
@app.get("/")
def read_root():
    return {"status": "online", "message": "Wellness API is running and ready!"}