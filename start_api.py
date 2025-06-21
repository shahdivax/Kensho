#!/usr/bin/env python3
"""
Start script for Kensho FastAPI server
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("🌌 Starting Kensho FastAPI Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🧘‍♂️ Ready for mindful learning!")
    print("="*50)
    
    # Check for API keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not gemini_key:
        print("⚠️  Warning: GEMINI_API_KEY not found. AI features may not work.")
    else:
        print("✅ Gemini API key found")
    
    if not groq_key:
        print("⚠️  Warning: GROQ_API_KEY not found. YouTube transcription won't work.")
    else:
        print("✅ Groq API key found")
    
    print("="*50)
    
    # Start the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 