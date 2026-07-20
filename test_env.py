import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if api_key:
    print("Groq API Key Loaded Successfully")
else:
    print("Groq API Key Not Found")