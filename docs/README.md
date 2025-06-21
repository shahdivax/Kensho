# 📚 Kensho Documentation

Welcome to the Kensho AI Learning Assistant documentation! Here you'll find everything you need to install, use, and deploy Kensho.

## 🚀 Getting Started

- **[Installation Guide](INSTALLATION.md)** - Detailed setup instructions for all platforms
- **[Setup Guide](SETUP.md)** - Original setup documentation with examples
- **[Features Overview](FEATURES.md)** - Comprehensive guide to all Kensho capabilities

## 🔧 Technical Documentation

- **[API Documentation](API.md)** - Complete API reference with examples
- **[Hugging Face Deployment](README_HUGGINGFACE.md)** - Deploy to Hugging Face Spaces

## 📖 Quick Reference

### Installation Summary
```bash
# Clone repository
git clone https://github.com/shahdivax/Kensho.git
cd kensho

# Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd frontend && npm install && cd ..

# Configure environment
cp env_example.txt .env
# Edit .env with your API keys

# Start application
python start_api.py  # Backend
npm run dev --prefix frontend  # Frontend
```

### Quick Links

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🛠️ Development

### Project Structure
```
kensho/
├── 🎨 frontend/          # Next.js React frontend
├── 🧠 kensho/           # Core Python modules
├── 🐳 docker/           # Docker configuration
├── 📚 docs/             # Documentation (you are here)
├── 🔧 api_server.py     # FastAPI backend
├── 📋 requirements.txt   # Python dependencies
└── 🐳 Dockerfile        # Container configuration
```

### Core Technologies

- **Backend**: FastAPI + Python 3.10+
- **Frontend**: Next.js 15 + React 19
- **AI**: Google Gemini + Groq APIs
- **Vector Store**: ChromaDB
- **UI**: Tailwind CSS + Radix UI

## 🌍 Deployment Options

| Platform | Guide | Difficulty | Cost |
|----------|-------|------------|------|
| **Hugging Face** | [README_HUGGINGFACE.md](README_HUGGINGFACE.md) | Easy | Free |
| **Local Docker** | [Installation Guide](INSTALLATION.md#docker-installation-alternative) | Medium | Free |
| **Vercel + Railway** | Coming soon | Medium | Free tier |
| **AWS/GCP/Azure** | Coming soon | Hard | Paid |

## 🆘 Need Help?

1. **Check the docs** - Start with the relevant guide above
2. **Search issues** - Look for existing solutions
3. **API reference** - Use the interactive docs at `/docs`
4. **Create issue** - If you can't find an answer
5. **Join Discord** - For real-time community help

## 🎯 Common Use Cases

### For Students
- Process textbooks and lecture notes
- Generate study materials (flashcards, summaries)
- Ask questions about complex topics
- Prepare for exams with AI-generated quizzes

### For Researchers  
- Analyze academic papers and reports
- Extract key insights from literature
- Generate citations and references
- Collaborate on research findings

### For Professionals
- Process training materials and documentation
- Analyze meeting recordings and transcripts
- Create knowledge bases from company documents
- Generate summaries for executive reviews

## 🔄 Update Guide

To update Kensho to the latest version:

```bash
# Pull latest changes
git pull origin main

# Update Python dependencies
pip install -r requirements.txt

# Update frontend dependencies
cd frontend && npm install && cd ..

# Rebuild if using Docker
docker build -t kensho .
```

## 📝 Contributing

We welcome contributions! See our [Contributing Guide](../CONTRIBUTING.md) for:

- Code style guidelines
- Development setup
- Testing procedures
- Pull request process

## 📄 License

Kensho is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

<div align="center">

**Made with 🧘‍♂️ for mindful learning**

[Main README](../README.md) • [GitHub](https://github.com/yourusername/kensho) • [Discord](https://discord.gg/kensho)

</div> 