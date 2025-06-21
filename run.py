#!/usr/bin/env python3
"""
🌌 Kensho - Quick Run Script
Simple script to launch Kensho with sensible defaults for development.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Quick launch for development."""
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found!")
        print("Creating .env from template...")
        
        # Copy from template
        template_file = Path("env_example.txt")
        if template_file.exists():
            with open(template_file, 'r') as f:
                template_content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(template_content)
            
            print("✅ Created .env file")
            print("🔑 Please edit .env and add your API keys:")
            print("   - GEMINI_API_KEY (required)")
            print("   - GROQ_API_KEY (for YouTube transcription)")
            print("   - OPENAI_API_KEY (alternative to Gemini)")
            print()
            print("Then run: python run.py")
            return
        else:
            print("❌ Template file not found. Please create .env manually.")
            return
    
    # Import and run the app
    try:
        from app import main as app_main
        print("🌌 Launching Kensho in development mode...")
        
        # Set development flags
        os.environ["KENSHO_DEBUG"] = "true"
        
        # Override sys.argv for development
        sys.argv = ["app.py", "--debug", "--host", "127.0.0.1"]
        
        app_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error launching Kensho: {e}")

if __name__ == "__main__":
    main() 