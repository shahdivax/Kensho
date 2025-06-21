# 🔧 Installation Guide

This guide provides detailed installation instructions for Kensho AI Learning Assistant.

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Internet**: Required for AI API calls

### Software Requirements
- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **Git**: Latest version
- **FFmpeg**: For audio/video processing

## Platform-Specific Installation

### Windows

1. **Install Python**
   ```bash
   # Download from python.org or use winget
   winget install Python.Python.3.12
   ```

2. **Install Node.js**
   ```bash
   # Download from nodejs.org or use winget
   winget install OpenJS.NodeJS
   ```

3. **Install FFmpeg**
   ```bash
   # Using chocolatey (recommended)
   choco install ffmpeg
   
   # Or download from https://ffmpeg.org/download.html
   # Add to PATH manually
   ```

4. **Install Git**
   ```bash
   winget install Git.Git
   ```

### macOS

1. **Install Homebrew** (if not installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Dependencies**
   ```bash
   brew install python@3.12 node ffmpeg git
   ```

### Linux (Ubuntu/Debian)

1. **Update Package Manager**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Dependencies**
   ```bash
   sudo apt install -y python3.12 python3.12-venv python3-pip nodejs npm ffmpeg git build-essential
   ```

### Linux (CentOS/RHEL)

1. **Enable EPEL Repository**
   ```bash
   sudo dnf install epel-release
   sudo dnf config-manager --set-enabled crb
   ```

2. **Install Dependencies**
   ```bash
   sudo dnf install -y python3.12 python3-pip nodejs npm ffmpeg git gcc gcc-c++ make
   ```

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/shahdivax/Kensho.git
cd kensho
```

### 2. Python Environment Setup

**Create Virtual Environment:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

**Install Python Dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Environment Configuration

```bash
# Copy environment template
cp env_example.txt .env
```

Edit the `.env` file with your API keys:
```env
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Optional Configuration
PORT=8000
HOST=0.0.0.0
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Verify Installation

```bash
# Test Python environment
python -c "import fastapi, uvicorn; print('Backend dependencies OK')"

# Test frontend
cd frontend
npm run build
cd ..
```

## Getting API Keys

### Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Add to your `.env` file

### Groq API Key

1. Go to [Groq Console](https://console.groq.com/keys)
2. Sign up or sign in
3. Click "Create API Key"
4. Copy the generated key
5. Add to your `.env` file

## Troubleshooting

### Common Issues

**Python Version Issues:**
```bash
# Check Python version
python --version

# If using older Python, install 3.10+
# Windows: Download from python.org
# macOS: brew install python@3.12
# Linux: sudo apt install python3.12
```

**Node.js Version Issues:**
```bash
# Check Node.js version
node --version

# If using older Node.js, update
# Windows: winget install OpenJS.NodeJS
# macOS: brew install node
# Linux: sudo apt install nodejs npm
```

**FFmpeg Issues:**
```bash
# Test FFmpeg installation
ffmpeg -version

# If not found, reinstall
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

**Permission Issues (Linux/macOS):**
```bash
# If pip install fails with permissions
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

**Virtual Environment Issues:**
```bash
# If venv creation fails
python -m pip install --upgrade pip
python -m pip install virtualenv
python -m virtualenv venv
```

### Environment Variables

If you're having issues with environment variables:

1. **Check file existence:**
   ```bash
   ls -la .env
   ```

2. **Verify content:**
   ```bash
   cat .env
   ```

3. **Export manually (temporary):**
   ```bash
   export GEMINI_API_KEY="your_key_here"
   export GROQ_API_KEY="your_key_here"
   ```

### Port Conflicts

If port 8000 is already in use:

1. **Find what's using the port:**
   ```bash
   # Windows:
   netstat -ano | findstr :8000
   
   # macOS/Linux:
   lsof -i :8000
   ```

2. **Use different port:**
   ```bash
   # In .env file
   PORT=8080
   
   # Or start with different port
   python api_server.py --port 8080
   ```

## Development Setup

For development, you may want additional tools:

### Code Editor Setup

**VS Code Extensions:**
- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Docker

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

### Testing Setup

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Docker Installation (Alternative)

If you prefer Docker:

1. **Install Docker:**
   - Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - macOS: `brew install --cask docker`
   - Linux: Follow [Docker docs](https://docs.docker.com/engine/install/)

2. **Build and run:**
   ```bash
   docker build -t kensho .
   docker run -p 7860:7860 -e GEMINI_API_KEY=your_key -e GROQ_API_KEY=your_key kensho
   ```

## Next Steps

After successful installation:

1. **Start the application** - See [Quick Start](../README.md#quick-start)
2. **Read the usage guide** - Check [SETUP.md](SETUP.md)
3. **Deploy to production** - See [README_HUGGINGFACE.md](README_HUGGINGFACE.md)

## Support

If you encounter issues not covered here:

1. Check our [FAQ](FAQ.md)
2. Search [GitHub Issues](https://github.com/yourusername/kensho/issues)
3. Create a [new issue](https://github.com/yourusername/kensho/issues/new) with:
   - Your operating system
   - Python/Node.js versions
   - Full error message
   - Steps to reproduce 