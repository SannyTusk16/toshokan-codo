"""Test Gemini API directly"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {GEMINI_API_KEY[:20]}..." if GEMINI_API_KEY else "No API key found")

if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    genai.configure(api_key=GEMINI_API_KEY)
    
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        print("✅ Model initialized")
        
        response = model.generate_content("Say hello in one sentence")
        print(f"✅ Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ No valid API key configured")
