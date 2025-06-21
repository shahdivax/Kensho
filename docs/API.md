# 🔌 API Documentation

This document describes the Kensho FastAPI backend endpoints and how to use them.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: Your deployed URL

## Authentication

Currently, Kensho uses API keys set via environment variables. No per-request authentication is required.

## Endpoints Overview

### Session Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sessions/new` | POST | Create a new learning session |
| `/sessions/{session_id}` | GET | Get session information and stats |

### Content Upload

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload/pdf` | POST | Upload and process PDF document |
| `/upload/text` | POST | Process text input |
| `/upload/youtube` | POST | Process YouTube video |

### Interaction

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send chat message about content |
| `/summary` | POST | Generate content summary |
| `/flashcards` | POST | Generate flashcards |
| `/quiz` | POST | Generate quiz questions |
| `/export` | POST | Export session data |

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with API info |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |

## Detailed Endpoints

### Session Management

#### Create Session
```http
POST /sessions/new
```

**Response:**
```json
{
  "session_id": "session_20240101_120000_abcd1234",
  "session": {
    "id": "session_20240101_120000_abcd1234",
    "created_at": "2024-01-01T12:00:00.000000",
    "documents": [],
    "chat_history": [],
    "summaries": [],
    "flashcards": [],
    "quizzes": [],
    "vector_store_path": null
  }
}
```

#### Get Session Info
```http
GET /sessions/{session_id}
```

**Response:**
```json
{
  "session": {
    "id": "session_20240101_120000_abcd1234",
    "created_at": "2024-01-01T12:00:00.000000",
    "documents": [...],
    "chat_history": [...],
    "summaries": [...],
    "flashcards": [...],
    "quizzes": [...]
  },
  "stats": {
    "documents": 1,
    "pages": 10,
    "chunks": 45,
    "chat_messages": 5,
    "summaries": 2,
    "flashcards": 15,
    "quizzes": 1
  }
}
```

### Content Upload

#### Upload PDF
```http
POST /upload/pdf
Content-Type: multipart/form-data
```

**Parameters:**
- `file`: PDF file (multipart/form-data)
- `session_id`: Session ID (form field, optional)

**Response:**
```json
{
  "session_id": "session_20240101_120000_abcd1234",
  "document": {
    "filename": "document.pdf",
    "type": "pdf",
    "pages": 10,
    "chunks": 45,
    "processed_at": "2024-01-01T12:00:00.000000",
    "vector_store_path": "sessions/session_20240101_120000_abcd1234_vectors"
  },
  "message": "Successfully processed document.pdf"
}
```

#### Upload Text
```http
POST /upload/text
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Your text content here...",
  "session_id": "session_20240101_120000_abcd1234"
}
```

**Response:**
```json
{
  "session_id": "session_20240101_120000_abcd1234",
  "document": {
    "type": "text",
    "length": 1500,
    "chunks": 8,
    "processed_at": "2024-01-01T12:00:00.000000",
    "vector_store_path": "sessions/session_20240101_120000_abcd1234_vectors"
  },
  "message": "Successfully processed text input"
}
```

#### Upload YouTube Video
```http
POST /upload/youtube
Content-Type: application/json
```

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "session_id": "session_20240101_120000_abcd1234"
}
```

**Response:**
```json
{
  "session_id": "session_20240101_120000_abcd1234",
  "document": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "type": "youtube",
    "title": "Video Title",
    "chunks": 25,
    "processed_at": "2024-01-01T12:00:00.000000",
    "vector_store_path": "sessions/session_20240101_120000_abcd1234_vectors"
  },
  "message": "Successfully processed YouTube video"
}
```

### Interaction

#### Chat
```http
POST /chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "What is the main topic of this document?",
  "session_id": "session_20240101_120000_abcd1234"
}
```

**Response:**
```json
{
  "response": "The main topic of this document is...",
  "sources": [
    {"page": 1, "chunk_id": "chunk_001"},
    {"page": 3, "chunk_id": "chunk_015"}
  ],
  "confidence": 0.95,
  "chat_history": [
    {
      "timestamp": "2024-01-01T12:00:00.000000",
      "user_message": "What is the main topic?",
      "ai_response": "The main topic is...",
      "sources": [...],
      "confidence": 0.95
    }
  ]
}
```

#### Generate Summary
```http
POST /summary
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "session_20240101_120000_abcd1234",
  "summary_type": "comprehensive",
  "max_length": 500
}
```

**Response:**
```json
{
  "summary": "This document discusses...",
  "word_count": 450,
  "key_topics": ["AI", "Machine Learning", "Education"],
  "summary_type": "comprehensive"
}
```

#### Generate Flashcards
```http
POST /flashcards
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "session_20240101_120000_abcd1234",
  "num_cards": 10
}
```

**Response:**
```json
{
  "flashcards": [
    {
      "front": "What is machine learning?",
      "back": "A subset of AI that enables computers to learn without explicit programming",
      "level": "understanding",
      "tags": ["AI", "ML", "concepts"]
    }
  ],
  "total_cards": 10,
  "session_id": "session_20240101_120000_abcd1234"
}
```

#### Generate Quiz
```http
POST /quiz
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "session_20240101_120000_abcd1234",
  "num_questions": 5,
  "difficulty": "mixed"
}
```

**Response:**
```json
{
  "questions": [
    {
      "question": "What is the primary goal of machine learning?",
      "options": [
        "To replace human intelligence",
        "To enable computers to learn from data",
        "To create robots",
        "To solve mathematical equations"
      ],
      "correct_answer": "To enable computers to learn from data",
      "difficulty": "medium",
      "explanation": "Machine learning focuses on enabling computers to learn patterns from data..."
    }
  ],
  "total_questions": 5,
  "difficulty": "mixed"
}
```

### Export

#### Export Session
```http
POST /export
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "session_20240101_120000_abcd1234",
  "export_options": ["summaries", "chat", "flashcards"]
}
```

**Response:**
- Returns a ZIP file download with exported content

## Error Handling

### Error Response Format
```json
{
  "error": "Error description",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Session/resource not found |
| 500 | Internal Server Error |

### Common Errors

**Session not found:**
```json
{
  "error": "Session not found",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**No document uploaded:**
```json
{
  "error": "No document uploaded for this session",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Invalid file type:**
```json
{
  "error": "Only PDF files are supported",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

## Rate Limits

Currently, no rate limits are enforced, but consider implementing them for production use:

- **Chat**: 60 requests per minute
- **Upload**: 10 requests per minute
- **Generation**: 30 requests per minute

## SDK Examples

### Python
```python
import requests

# Create session
response = requests.post("http://localhost:8000/sessions/new")
session = response.json()
session_id = session["session_id"]

# Upload PDF
with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {"session_id": session_id}
    response = requests.post(
        "http://localhost:8000/upload/pdf",
        files=files,
        data=data
    )

# Chat
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What is this document about?",
        "session_id": session_id
    }
)
answer = response.json()["response"]
```

### JavaScript
```javascript
// Create session
const response = await fetch('http://localhost:8000/sessions/new', {
  method: 'POST'
});
const session = await response.json();
const sessionId = session.session_id;

// Upload PDF
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('session_id', sessionId);

const uploadResponse = await fetch('http://localhost:8000/upload/pdf', {
  method: 'POST',
  body: formData
});

// Chat
const chatResponse = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What is this document about?',
    session_id: sessionId
  })
});
const answer = await chatResponse.json();
```

## WebSocket Support

Currently not implemented, but planned for future versions to support:
- Real-time processing updates
- Live chat streaming
- Progress notifications

## Versioning

The API follows semantic versioning. Current version: **v1.0.0**

Future versions will maintain backward compatibility or provide migration guides.

## Support

For API-related questions:
1. Check the interactive docs at `/docs`
2. Review this documentation
3. Create an issue on GitHub
4. Join our Discord for real-time help 