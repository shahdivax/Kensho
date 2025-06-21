#!/usr/bin/env python3
"""
🌌 Kensho - Setup Script
Automated setup and configuration for Kensho AI Learning Assistant.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print the Kensho banner."""
    banner = """
🌌 ═══════════════════════════════════════════════════════════════════════════════
                            Kensho Setup
                   Your Personal AI Mirror for Learning
    
    "See through. Learn deeply. Own the mirror."
═══════════════════════════════════════════════════════════════════════════════ 🌌
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Kensho requires Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("   Please try: pip install -r requirements.txt")
        return False

def setup_environment():
    """Set up environment variables."""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    template_file = Path("env_example.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not template_file.exists():
        print("❌ Template file not found")
        return False
    
    # Copy template to .env
    shutil.copy(template_file, env_file)
    print("✅ Created .env file from template")
    
    # Prompt for API keys
    print("\n🔑 API Key Configuration")
    print("─" * 40)
    print("Kensho needs at least one AI API key to function:")
    print("1. Gemini API (recommended) - Free tier available")
    print("2. OpenAI API (alternative) - Paid service")
    print("3. Groq API (for YouTube) - Free tier available")
    print()
    
    # Read current .env content
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    # Ask for Gemini API key
    gemini_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
    if gemini_key:
        env_content = env_content.replace("your_gemini_api_key_here", gemini_key)
        print("✅ Gemini API key configured")
    
    # Ask for Groq API key
    groq_key = input("Enter your Groq API key (or press Enter to skip): ").strip()
    if groq_key:
        env_content = env_content.replace("your_groq_api_key_here", groq_key)
        print("✅ Groq API key configured")
    
    # Ask for OpenAI API key if no Gemini key
    if not gemini_key:
        openai_key = input("Enter your OpenAI API key (required if no Gemini key): ").strip()
        if openai_key:
            env_content = env_content.replace("your_openai_api_key_here", openai_key)
            print("✅ OpenAI API key configured")
        else:
            print("⚠️  No AI API key configured. You'll need to add one manually.")
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    return True

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    
    directories = ["sessions", "data", "exports"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    return True

def run_tests():
    """Run basic functionality tests."""
    print("🧪 Running basic tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_kensho.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n🎉 Setup Complete!")
    print("═" * 50)
    print("Next steps:")
    print("1. 🚀 Launch Kensho:")
    print("   python app.py")
    print("   or")
    print("   python run.py")
    print()
    print("2. 🌐 Open your browser to:")
    print("   http://localhost:7860")
    print()
    print("3. 📚 Upload a document or paste text to start learning!")
    print()
    print("🔗 Useful commands:")
    print("   python app.py --help          # See all options")
    print("   python app.py --share         # Create public link")
    print("   python test_kensho.py         # Run tests")
    print()
    print("📖 For more information, see README.md")
    print("🐛 Report issues: https://github.com/your-username/kensho/issues")
    print()
    print("🧘‍♂️ Remember: Kensho is your mirror for deep understanding.")
    print("═" * 50)

def main():
    """Main setup function."""
    print_banner()
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Creating directories", create_directories),
        ("Running tests", run_tests)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            print("Please check the error messages above and try again.")
            return False
    
    print_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1) 