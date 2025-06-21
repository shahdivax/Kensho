#!/usr/bin/env python3
"""
🌌 Kensho - Main Application Entry Point

Launch the Kensho AI learning assistant with beautiful Zen-inspired UI.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from kensho import create_kensho_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Main entry point for Kensho application."""
    
    parser = argparse.ArgumentParser(
        description="🌌 Kensho - Your Personal AI Mirror for Learning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                    # Launch with default settings
  python app.py --port 8080        # Launch on custom port
  python app.py --share            # Create public link
  python app.py --debug            # Enable debug mode

Environment Variables:
  GEMINI_API_KEY     - Your Gemini API key (required)
  GROQ_API_KEY       - Your Groq API key (for Whisper transcription)
  OPENAI_API_KEY     - Your OpenAI API key (alternative to Gemini)

"See through. Learn deeply. Own the mirror."
        """
    )
    
    parser.add_argument(
        "--host",
        default=os.getenv("KENSHO_HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("KENSHO_PORT", "7860")),
        help="Port to bind to (default: 7860)"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public link (useful for demos)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.getenv("KENSHO_DEBUG", "false").lower() == "true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--auth",
        nargs=2,
        metavar=("USERNAME", "PASSWORD"),
        help="Enable authentication with username and password"
    )
    
    args = parser.parse_args()
    
    # Check for required API keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not gemini_key and not openai_key:
        print("❌ Error: No AI API key found!")
        print("Please set either GEMINI_API_KEY or OPENAI_API_KEY in your environment.")
        print("You can copy env_example.txt to .env and fill in your keys.")
        sys.exit(1)
    
    if not groq_key:
        print("⚠️  Warning: GROQ_API_KEY not found.")
        print("YouTube video transcription will not be available.")
        print("Set GROQ_API_KEY in your environment to enable this feature.")
    
    # Create the Kensho app
    print("🌌 Initializing Kensho...")
    app = create_kensho_app()
    
    # Configure launch parameters
    launch_kwargs = {
        "server_name": args.host,
        "server_port": args.port,
        "share": args.share,
        "debug": args.debug,
        "show_error": args.debug,
        "quiet": not args.debug,
        "favicon_path": None,  # Could add a custom favicon
        "app_kwargs": {
            "title": "🌌 Kensho - AI Learning Mirror",
            "description": "Your personal AI mirror for deep learning and awakening"
        }
    }
    
    # Add authentication if specified
    if args.auth:
        launch_kwargs["auth"] = tuple(args.auth)
        print(f"🔐 Authentication enabled for user: {args.auth[0]}")
    
    # Print startup information
    print("\n" + "="*60)
    print("🌌 Kensho - AI Learning Mirror")
    print("="*60)
    print(f"🌐 Host: {args.host}")
    print(f"🚪 Port: {args.port}")
    print(f"🔗 Share: {'Yes' if args.share else 'No'}")
    print(f"🐛 Debug: {'Yes' if args.debug else 'No'}")
    print(f"🤖 AI Provider: {'Gemini' if gemini_key else 'OpenAI'}")
    print(f"🎤 Whisper: {'Available' if groq_key else 'Not available'}")
    print("="*60)
    print("💡 Ready to begin your learning journey!")
    print("📚 Upload a document, paste text, or provide a YouTube URL to start.")
    print("🧘‍♂️ Remember: Kensho is your mirror for deep understanding.")
    print("="*60)
    
    try:
        # Launch the application
        app.launch(**launch_kwargs)
    except KeyboardInterrupt:
        print("\n🌙 Kensho shutting down gracefully...")
        print("Thank you for using Kensho. May your learning journey continue!")
    except Exception as e:
        print(f"\n❌ Error launching Kensho: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 