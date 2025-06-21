# 🌌 Kensho - Hugging Face Deployment Guide

This guide will help you deploy Kensho on Hugging Face Spaces using Docker.

## Prerequisites

1. **Hugging Face Account**: Create an account at [huggingface.co](https://huggingface.co)
2. **API Keys**: You'll need:
   - Gemini API key (for AI features)
   - Groq API key (for fast inference)

## Step-by-Step Deployment

### 1. Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Configure your space:
   - **Name**: `kensho-ai-learning`
   - **License**: `MIT`
   - **Space SDK**: `Docker`
   - **Visibility**: `Public` (or Private if preferred)

### 2. Clone Your Space

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/kensho-ai-learning
cd kensho-ai-learning
```

### 3. Copy Files to Your Space

Copy all files from this repository to your cloned space directory:

```bash
# Copy all files except .git
cp -r /path/to/kensho/* ./
```

### 4. Create Environment Configuration

Create a `.env` file in your space root:

```env
# AI API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# App Configuration
PYTHONPATH=/app
PYTHONUNBUFFERED=1
PORT=7860
HOST=0.0.0.0
```

### 5. Configure Space Secrets

Instead of using a `.env` file, it's more secure to use Hugging Face Spaces secrets:

1. Go to your Space settings
2. Click on "Repository secrets"
3. Add these secrets:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `GROQ_API_KEY`: Your Groq API key

### 6. Create Space Configuration

Create `README.md` in your space root:

```markdown
---
title: Kensho AI Learning Assistant
emoji: 🌌
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# 🌌 Kensho - AI Learning Assistant

An intelligent learning companion that helps you understand and interact with your documents, PDFs, and YouTube videos using advanced AI.

## Features

- 📄 **PDF Processing**: Upload and analyze PDF documents
- 🎥 **YouTube Integration**: Extract insights from YouTube videos
- 💬 **Interactive Chat**: Ask questions about your content
- 📝 **Smart Summaries**: Generate comprehensive summaries
- 🧩 **Flashcards**: Create study cards automatically
- 📊 **Quizzes**: Test your knowledge with generated questions

## Usage

1. Upload a PDF document or paste a YouTube URL
2. Wait for processing to complete
3. Start chatting with the AI about your content
4. Generate summaries, flashcards, and quizzes

## Technology Stack

- **Backend**: FastAPI + Python
- **Frontend**: Next.js + React
- **AI**: Gemini & Groq APIs
- **Vector Database**: ChromaDB
- **Deployment**: Docker on Hugging Face Spaces
```

### 7. Push to Your Space

```bash
git add .
git commit -m "Initial deployment of Kensho AI Learning Assistant"
git push
```

### 8. Monitor Deployment

1. Go to your Space page
2. Check the "Logs" tab to monitor the build process
3. Once built, your app will be available at: `https://huggingface.co/spaces/YOUR_USERNAME/kensho-ai-learning`

## Environment Variables

The app expects these environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `GROQ_API_KEY` | Groq API key | Yes |
| `PORT` | Port to run on (default: 7860) | No |
| `HOST` | Host to bind to (default: 0.0.0.0) | No |

## API Keys Setup

### Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your Hugging Face Space secrets

### Groq API Key
1. Go to [Groq Console](https://console.groq.com/keys)
2. Create a new API key
3. Copy the key to your Hugging Face Space secrets

## Troubleshooting

### Common Issues

1. **Build fails**: Check that all dependencies are in `requirements.txt`
2. **API errors**: Verify your API keys are set correctly in Space secrets
3. **Frontend not loading**: Ensure nginx is configured properly
4. **Memory issues**: Consider using smaller models or increase Space hardware

### Logs

Monitor your app logs in the Hugging Face Space interface:
- Build logs show Docker build process
- Runtime logs show application output
- Error logs help debug issues

## Hardware Requirements

For optimal performance, consider upgrading your Space hardware:
- **CPU**: Basic (free tier) should work for light usage
- **GPU**: Not required for this application
- **Memory**: 2GB+ recommended for better performance

## Support

If you encounter issues:
1. Check the logs in your Hugging Face Space
2. Verify API keys are set correctly
3. Ensure all files are copied properly
4. Check the Dockerfile syntax

## Security Notes

- Never commit API keys to your repository
- Use Hugging Face Spaces secrets for sensitive data
- Consider making your Space private if handling sensitive documents
- API keys are only used server-side and never exposed to users

---

Enjoy your AI-powered learning experience! 🌌✨ 