# 🌌 Kensho - Production Setup Guide

This guide explains how to set up and run the new production-ready Kensho with Next.js frontend and FastAPI backend.

## 🏗️ Architecture

- **Frontend**: Next.js 15 + TypeScript + ShadCN UI + Tailwind CSS
- **Backend**: FastAPI + Python
- **AI**: Gemini 2.0 Flash / OpenAI GPT-4
- **Vector Store**: FAISS (local)
- **Transcription**: Groq Whisper

## 🚀 Quick Start

### 1. Environment Setup

Copy the environment file and add your API keys:

```bash
cp env_example.txt .env
```

Edit `.env` with your API keys:
```
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Backend Setup

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
python start_api.py
```

The API will be available at:
- **Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3. Frontend Setup

Navigate to the frontend directory:
```bash
cd frontend
```

Install Node.js dependencies:
```bash
npm install
```

Start the Next.js development server:
```bash
npm run dev
```

The frontend will be available at:
- **App**: http://localhost:3000

## 🎨 Features

### ✨ Beautiful UI
- **Zen-inspired design** with cosmic aesthetics
- **Responsive layout** that works on desktop and mobile
- **Smooth animations** and hover effects
- **Dark theme** optimized for focus and mindfulness

### 🧠 AI-Powered Learning
- **PDF document processing** with page-aware citations
- **YouTube video transcription** using Whisper AI
- **Text input processing** for articles and notes
- **RAG-based Q&A** with semantic search
- **Multi-level summaries** (comprehensive, key points, executive)
- **Bloom's taxonomy flashcards** for different learning levels
- **Adaptive quizzes** with difficulty selection

### 🔐 Privacy-First
- **Local processing** - all data stays on your machine
- **Session-based** - no persistent user tracking
- **File-based storage** - no external databases required
- **Open source** - inspect and modify as needed

## 📁 Project Structure

```
Kensho/
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   │   ├── components/      # React components
│   │   │   └── lib/             # Utilities and API functions
│   │   ├── package.json
│   │   └── tailwind.config.js
│   ├── kensho/                  # Python backend modules
│   │   ├── ai_assistant.py      # AI/LLM integration
│   │   ├── document_processor.py # PDF/text/video processing
│   │   ├── vector_store.py      # FAISS vector storage
│   │   └── ui.py               # Original Gradio UI (deprecated)
│   ├── api_server.py           # FastAPI server
│   ├── start_api.py           # API startup script
│   ├── app.py                 # Original Gradio app (deprecated)
│   └── requirements.txt       # Python dependencies
```

## 🔧 Development

### Backend Development

The FastAPI server supports hot reload:
```bash
python start_api.py
```

### Frontend Development

The Next.js server supports hot reload:
```bash
cd frontend && npm run dev
```

### API Testing

Visit the interactive API documentation:
http://localhost:8000/docs

## 🚀 Production Deployment

### Backend Production

Use Gunicorn for production:
```bash
pip install gunicorn
gunicorn api_server:app --bind 0.0.0.0:8000 --workers 4
```

### Frontend Production

Build the Next.js app:
```bash
cd frontend
npm run build
npm start
```

### Docker Deployment

Use the existing Docker setup (update needed for new architecture):
```bash
docker-compose up
```

## 🔗 API Endpoints

### Session Management
- `POST /sessions/new` - Create new session
- `GET /sessions/{session_id}` - Get session info

### Content Upload
- `POST /upload/pdf` - Upload PDF document
- `POST /upload/text` - Process text input
- `POST /upload/youtube` - Process YouTube video

### AI Features
- `POST /chat` - Chat with AI about content
- `POST /summary` - Generate summaries
- `POST /flashcards` - Generate flashcards
- `POST /quiz` - Generate quiz questions
- `POST /export` - Export session data

### Utilities
- `GET /health` - Health check
- `GET /` - API info

## 🧘‍♂️ Philosophy

The new architecture maintains Kensho's core philosophy:

- **See through** - Clean, distraction-free interface
- **Learn deeply** - AI-powered insights and understanding
- **Own the mirror** - Full control over your data and learning

## 🤝 Migration from Gradio

The new setup is designed to eventually replace the Gradio interface. Key improvements:

- **Better performance** - Faster loading and interactions
- **Modern UI** - Professional, production-ready interface
- **Scalability** - Easier to extend and customize
- **Mobile support** - Responsive design works on all devices
- **API-first** - Clean separation between frontend and backend

## 🐛 Troubleshooting

### Common Issues

1. **Node.js not found**: Make sure Node.js is installed and in your PATH
2. **API connection errors**: Ensure both frontend and backend are running
3. **Missing API keys**: Check that your `.env` file has the required keys
4. **Port conflicts**: Change ports in the startup scripts if needed

### Getting Help

- Check the API documentation at http://localhost:8000/docs
- Review the browser console for frontend errors
- Check the terminal output for backend errors
- Ensure all dependencies are installed correctly

---

**Ready to begin your mindful learning journey with the new Kensho! 🌌** 