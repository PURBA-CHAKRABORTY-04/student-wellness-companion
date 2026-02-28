import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# 1. Load the HF_TOKEN from the .env file you just created
load_dotenv()
hf_token = os.getenv("HF_TOKEN")

if not hf_token:
    raise ValueError("HF_TOKEN is missing! Please check your .env file.")

# 2. Initialize the AI Client
# We are using Zephyr, an incredibly fast and smart conversational model
client = InferenceClient(
    model="Qwen/Qwen2.5-7B-Instruct",  # This is a smaller, faster model perfect for our use case
    token=hf_token
)

def generate_chat_response(user_message: str, current_mood: str) -> str:
    """
    Takes the student's message and mood, applies the system prompt, 
    and gets a response from the Hugging Face model.
    """
    
    # 3. The Guardrail (System Prompt)
    system_prompt = (
        "You are a highly empathetic Student Wellness and Academic Support Companion. "
        "Your ONLY purpose is to discuss mental health, study strategies, stress management, "
        "and student well-being. If a user asks about anything unrelated (like coding, politics, "
        "or general trivia), you must politely refuse and redirect the conversation back to their well-being. "
        f"IMPORTANT: The student has indicated they are currently feeling {current_mood}. "
        "Tailor your advice and tone to support someone feeling this way. Keep responses concise and supportive."
    )

    # 4. Format the conversation for the AI
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        # 5. Send to Hugging Face and wait for the reply
        response = client.chat_completion(
            messages=messages,
            max_tokens=300,       # Keeps responses from getting too long
            temperature=0.7       # 0.7 gives a warm, natural tone without being too random
        )
        
        # Extract the text from the AI's response
        return response.choices[0].message.content

    except Exception as e:
        print(f"AI Engine Error: {e}")
        return "I'm having a little trouble connecting right now. Please take a deep breath, and try asking me again in a moment."