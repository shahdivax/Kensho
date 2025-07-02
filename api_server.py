#!/usr/bin/env python3
"""
🌌 Kensho FastAPI Server

Production-ready API server for the Kensho AI learning assistant.
Provides endpoints for document processing, chat, summaries, flashcards, and more.
"""

import os
import json
import tempfile
import zipfile
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from pathlib import Path
import re
import shutil

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

# Import Kensho modules
from kensho.document_processor import DocumentProcessor
from kensho.vector_store import KenshoVectorStore
from kensho.ai_assistant import KenshoAIAssistant

# Initialize FastAPI app
app = FastAPI(
    title="🌌 Kensho API",
    description="AI-powered learning assistant API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Kensho components
doc_processor = DocumentProcessor()
vector_store = KenshoVectorStore()
ai_assistant = KenshoAIAssistant()

# In-memory session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}

# Pydantic models for request/response
class TextInput(BaseModel):
    text: str
    session_id: str

class YouTubeInput(BaseModel):
    url: str
    session_id: str

class ChatMessage(BaseModel):
    message: str
    session_id: str

class SummaryRequest(BaseModel):
    session_id: str
    summary_type: str = "comprehensive"
    max_length: int = 500

class FlashcardRequest(BaseModel):
    session_id: str
    num_cards: int = 10

class QuizRequest(BaseModel):
    session_id: str
    num_questions: int = 5
    difficulty: str = "mixed"

class ExportRequest(BaseModel):
    session_id: str
    export_options: List[str]

class MindMapRequest(BaseModel):
    session_id: str

# Utility functions
def generate_session_id() -> str:
    """Generate a unique session ID."""
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

def get_session(session_id: str) -> Dict[str, Any]:
    """Get session data or create new session."""
    if session_id not in sessions:
        sessions[session_id] = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'documents': [],
            'chat_history': [],
            'summaries': [],
            'flashcards': [],
            'quizzes': [],
            'vector_store_path': None
        }
    return sessions[session_id]

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "🌌 Kensho API Server",
        "description": "AI-powered learning assistant",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/sessions/new")
async def create_session():
    """Create a new learning session."""
    session_id = generate_session_id()
    session = get_session(session_id)
    return {"session_id": session_id, "session": session}

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session information."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session": session,
        "stats": {
            "documents": len(session['documents']),
            "pages": sum(doc.get('pages', 0) for doc in session['documents']),
            "chunks": sum(doc.get('chunks', 0) for doc in session['documents']),
            "chat_messages": len(session['chat_history']),
            "summaries": len(session['summaries']),
            "flashcards": len(session['flashcards']),
            "quizzes": len(session['quizzes'])
        }
    }

@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...), session_id: str = Form(None)):
    """Upload and process a PDF document."""
    if not session_id:
        session_id = generate_session_id()
        print(f"📄 Generated new session ID: {session_id}")
    else:
        print(f"📄 Using existing session ID: {session_id}")
    
    session = get_session(session_id)
    print(f"📄 Session data before upload: {len(session.get('documents', []))} documents")
    
    try:
        print(f"📄 Starting PDF upload: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            print(f"❌ Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        print(f"📄 Saved temporary file: {tmp_file_path} ({len(content)} bytes)")
        
        # Process the PDF - returns (session_id, full_text, chunks)
        print(f"📄 Processing PDF with document processor...")
        doc_session_id, full_text, chunks = doc_processor.process_pdf(tmp_file_path)
        print(f"📄 PDF processing complete. Session: {doc_session_id}, Text length: {len(full_text)}, Chunks: {len(chunks)}")
        
        # Count pages from the full text
        page_count = len(re.findall(r'\[source: page \d+\]', full_text))
        print(f"📄 Found {page_count} pages in PDF")
        
        # Store in vector database
        vector_store_path = f"sessions/{session_id}_vectors"
        print(f"📄 Creating vector store at: {vector_store_path}")
        vector_store.create_index(chunks, vector_store_path)
        print(f"✅ Vector store created successfully")
        
        # Update session
        document_info = {
            'filename': file.filename,
            'type': 'pdf',
            'pages': page_count,
            'chunks': len(chunks),
            'processed_at': datetime.now().isoformat(),
            'vector_store_path': vector_store_path
        }
        
        session['documents'].append(document_info)
        session['vector_store_path'] = vector_store_path
        
        print(f"📄 Session updated. Documents: {len(session['documents'])}")
        print(f"📄 Document info: {document_info}")
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        print(f"📄 Cleaned up temporary file: {tmp_file_path}")
        
        result = {
            "session_id": session_id,
            "document": document_info,
            "message": f"Successfully processed {file.filename}"
        }
        
        print(f"✅ PDF upload complete: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        error_msg = f"Error processing PDF: {str(e)}"
        print(f"❌ PDF Error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/upload/text")
async def upload_text(input_data: TextInput):
    """Process text input."""
    session = get_session(input_data.session_id)
    
    try:
        # Process the text - returns (session_id, full_text, chunks)
        doc_session_id, full_text, chunks = doc_processor.process_text(input_data.text)
        
        # Store in vector database
        vector_store_path = f"sessions/{input_data.session_id}_vectors"
        vector_store.create_index(chunks, vector_store_path)
        
        # Update session
        document_info = {
            'type': 'text',
            'length': len(input_data.text),
            'chunks': len(chunks),
            'processed_at': datetime.now().isoformat(),
            'vector_store_path': vector_store_path
        }
        
        session['documents'].append(document_info)
        session['vector_store_path'] = vector_store_path
        
        return {
            "session_id": input_data.session_id,
            "document": document_info,
            "message": "Successfully processed text input"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@app.post("/upload/youtube")
async def upload_youtube(input_data: YouTubeInput, background_tasks: BackgroundTasks):
    """Process YouTube video (transcription)."""
    session = get_session(input_data.session_id)
    
    try:
        print(f"🎥 Starting YouTube processing for URL: {input_data.url}")
        
        # Validate YouTube URL
        if not any(domain in input_data.url.lower() for domain in ['youtube.com', 'youtu.be']):
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Process YouTube video - this is a generator, we need to handle it differently
        final_result = None
        last_progress = 0
        
        for progress, status, data in doc_processor.process_youtube_video(input_data.url):
            print(f"🎥 Progress: {progress}% - {status}")
            last_progress = progress
            
            if progress == 100 and isinstance(data, dict):
                final_result = data
                break
            elif progress == 100 and isinstance(data, str) and "Error" in status:
                raise Exception(data if data else status)
        
        if not final_result:
            raise Exception(f"Failed to process YouTube video. Last progress: {last_progress}%")
        
        print(f"🎥 Processing complete. Got {len(final_result.get('chunks', []))} chunks")
        
        chunks = final_result['chunks']
        transcript = final_result['transcript']
        
        # Store in vector database
        vector_store_path = f"sessions/{input_data.session_id}_vectors"
        print(f"🎥 Creating vector store at: {vector_store_path}")
        print(f"🎥 Session ID for vector store: {input_data.session_id}")
        vector_store.create_index(chunks, vector_store_path)
        print(f"✅ Vector store created successfully")
        
        # Update session
        document_info = {
            'url': input_data.url,
            'type': 'youtube',
            'title': 'YouTube Video',  # We could extract this from the URL later
            'chunks': len(chunks),
            'processed_at': datetime.now().isoformat(),
            'vector_store_path': vector_store_path
        }
        
        session['documents'].append(document_info)
        session['vector_store_path'] = vector_store_path
        
        print(f"🎥 Successfully processed YouTube video: {len(chunks)} chunks created")
        
        return {
            "session_id": input_data.session_id,
            "document": document_info,
            "transcript": transcript,
            "message": "Successfully processed YouTube video"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_message = f"Error processing YouTube video: {str(e)}"
        print(f"❌ YouTube Error: {error_message}")
        raise HTTPException(status_code=500, detail=error_message)

@app.post("/chat")
async def chat(message: ChatMessage):
    """Chat with the AI about uploaded content."""
    session = get_session(message.session_id)
    
    if not session['vector_store_path']:
        raise HTTPException(status_code=400, detail="No document uploaded for this session")
    
    try:
        # Search for relevant context
        context_chunks = vector_store.search(
            message.message, 
            session['vector_store_path'], 
            top_k=5
        )
        
        # Generate AI response
        response = ai_assistant.answer_question(
            message.message, 
            context_chunks, 
            session
        )
        
        # Store in chat history
        chat_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': message.message,
            'ai_response': response['answer'],
            'sources': response['sources'],
            'confidence': response['confidence']
        }
        
        session['chat_history'].append(chat_entry)
        
        return {
            "response": response['answer'],
            "sources": response['sources'],
            "confidence": response['confidence'],
            "chat_history": session['chat_history'][-10:]  # Return last 10 messages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(message: ChatMessage):
    """Stream chat response tokens for real-time UI updates (Gemini or OpenAI)."""
    session = get_session(message.session_id)

    if not session["vector_store_path"]:
        raise HTTPException(status_code=400, detail="No document uploaded for this session")

    # Retrieve relevant context for the query
    context_chunks = vector_store.search(
        message.message,
        session["vector_store_path"],
        top_k=5
    )

    # Build prompts
    context_text = ai_assistant._prepare_context(context_chunks)
    system_prompt = ai_assistant._get_rag_system_prompt()
    user_prompt = f"""
    Based on the following context from the document, please answer the question.

    CONTEXT:
    {context_text}

    QUESTION: {message.message}

    Provide a comprehensive answer that cites sources like [source: page X] or [timestamp: MM:SS].
    If context is insufficient, say what's missing.
    """

    # Helper to persist chat entry after full answer is obtained
    def persist_chat(answer_text: str, sources: list, confidence: float):
        chat_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": message.message,
            "ai_response": answer_text.strip(),
            "sources": sources,
            "confidence": confidence,
        }
        session["chat_history"].append(chat_entry)

    async def fallback_stream():
        """Generate full answer then yield tokens one-by-one (works for any model)."""
        response = ai_assistant.answer_question(message.message, context_chunks, session)
        answer_text = response["answer"]
        async def gen():
            accumulated = ""
            for tok in answer_text.split():
                accumulated += tok + " "
                yield tok + " "
                await asyncio.sleep(0)
            persist_chat(accumulated, response["sources"], response["confidence"])
        return StreamingResponse(gen(), media_type="text/plain")

    # Try native streaming first
    try:
        client = ai_assistant.client
        stream = client.chat.completions.create(
            model=ai_assistant.default_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            stream=True
        )

        def native_stream_gen():
            answer_parts = []
            for chunk in stream:
                # OpenAI-compatible chunks
                delta = None
                if hasattr(chunk, "choices") and chunk.choices:
                    delta = chunk.choices[0].delta.content or ""
                # Gemini-compatible (text) – fall back to 'text' attribute if present
                if delta is None and hasattr(chunk, "text"):
                    delta = getattr(chunk, "text") or ""
                if not delta:
                    continue
                answer_parts.append(delta)
                yield delta
            full_answer = "".join(answer_parts)
            persist_chat(full_answer, ai_assistant._extract_sources_from_chunks(context_chunks), ai_assistant._calculate_confidence(context_chunks, message.message))

        return StreamingResponse(native_stream_gen(), media_type="text/plain")

    except Exception as streaming_error:
        # Native streaming failed – log for debugging and fallback to tokenised streaming
        print(f"⚠️ Native streaming unavailable, falling back. Reason: {streaming_error}")
        return await fallback_stream()

@app.post("/summary")
async def generate_summary(request: SummaryRequest):
    """Generate a summary of the uploaded content."""
    session = get_session(request.session_id)
    
    if not session['documents']:
        raise HTTPException(status_code=400, detail="No document uploaded for this session")
    
    try:
        # Get the full text from the first document (simplified)
        # In a real implementation, you might want to combine all documents
        vector_store_path = session['vector_store_path']
        chunks = vector_store.get_all_chunks(vector_store_path)
        full_text = "\n\n".join([chunk['text'] for chunk in chunks])
        
        # Generate summary
        summary_result = ai_assistant.generate_summary(
            full_text, 
            request.summary_type, 
            request.max_length
        )
        
        # Store summary
        summary_entry = {
            'type': request.summary_type,
            'content': summary_result['summary'],
            'word_count': summary_result['word_count'],
            'key_topics': summary_result['key_topics'],
            'generated_at': datetime.now().isoformat()
        }
        
        session['summaries'].append(summary_entry)
        
        return summary_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@app.post("/flashcards")
async def generate_flashcards(request: FlashcardRequest):
    """Generate flashcards from the uploaded content."""
    session = get_session(request.session_id)
    
    if not session['vector_store_path']:
        raise HTTPException(status_code=400, detail="No document uploaded for this session")
    
    try:
        # Get chunks for flashcard generation
        chunks = vector_store.get_all_chunks(session['vector_store_path'])
        
        # Generate flashcards
        flashcards = ai_assistant.generate_flashcards(chunks, request.num_cards)
        
        # Store flashcards
        flashcard_set = {
            'cards': flashcards,
            'generated_at': datetime.now().isoformat(),
            'num_cards': len(flashcards)
        }
        
        session['flashcards'].append(flashcard_set)
        
        return {
            "flashcards": flashcards,
            "total_cards": len(flashcards),
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating flashcards: {str(e)}")

@app.post("/quiz")
async def generate_quiz(request: QuizRequest):
    """Generate a quiz from the uploaded content."""
    session = get_session(request.session_id)
    
    if not session['vector_store_path']:
        raise HTTPException(status_code=400, detail="No document uploaded for this session")
    
    try:
        # Get chunks for quiz generation
        chunks = vector_store.get_all_chunks(session['vector_store_path'])
        
        # Generate quiz
        quiz_result = ai_assistant.generate_quiz(
            chunks, 
            request.num_questions, 
            request.difficulty
        )
        
        # Store quiz
        quiz_entry = {
            'questions': quiz_result['questions'],
            'difficulty': request.difficulty,
            'generated_at': datetime.now().isoformat(),
            'num_questions': len(quiz_result['questions'])
        }
        
        session['quizzes'].append(quiz_entry)
        
        return quiz_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")

@app.post("/mindmap")
async def generate_mindmap(request: MindMapRequest):
    """Generate a mind map from the uploaded content."""
    session = get_session(request.session_id)
    
    if not session['vector_store_path']:
        raise HTTPException(status_code=400, detail="No document uploaded for this session")
    
    try:
        # Get chunks for mind map generation
        chunks = vector_store.get_all_chunks(session['vector_store_path'])
        full_text = "\n\n".join([chunk['text'] for chunk in chunks])
        
        # Generate mind map using AI assistant
        response = ai_assistant.client.chat.completions.create(
            model=ai_assistant.default_model,
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert educator creating mind maps. Output MUST be a pure markdown bullet list using hyphens ('-') for each node, with exactly two leading spaces per indent level. Do NOT include any quotes (\"), parentheses ( ), code fences, numbering, or additional punctuation that could break parsing. Each logical concept should be on its own line. Follow this hierarchy guidelines:
                    - Top-level themes as primary branches
                    - Subtopics as secondary branches
                    - Key details as tertiary branches
                    Only provide the bullet list – no headings, introductions, or extra commentary."""
                },
                {
                    "role": "user", 
                    "content": f"Create a comprehensive mind map from this content:\n\n{full_text}"
                }
            ],
            temperature=0.3
        )
        
        mindmap_content = response.choices[0].message.content
        
        # Store mind map in session (you could add this if needed)
        mindmap_entry = {
            'content': mindmap_content,
            'generated_at': datetime.now().isoformat()
        }
        
        return {
            "mindmap": mindmap_content,
            "session_id": request.session_id,
            "generated_at": mindmap_entry['generated_at']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating mind map: {str(e)}")

@app.post("/export")
async def export_session(request: ExportRequest):
    """Export session data in various formats."""
    session = get_session(request.session_id)
    
    try:
        temp_dir = tempfile.mkdtemp()
        export_files = []

        try:
            # Export summaries as Markdown
            if 'summaries' in request.export_options and session['summaries']:
                summary_file = os.path.join(temp_dir, 'summaries.md')
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write("# Kensho Session Summaries\n\n")
                    for i, summary in enumerate(session['summaries'], 1):
                        f.write(f"## Summary {i} ({summary['type']})\n\n")
                        f.write(f"{summary['content']}\n\n")
                        f.write(f"**Key Topics:** {', '.join(summary['key_topics'])}\n\n")
                        f.write("---\n\n")
                export_files.append(summary_file)

            # Export chat history as JSON
            if 'chat' in request.export_options and session['chat_history']:
                chat_file = os.path.join(temp_dir, 'chat_history.json')
                with open(chat_file, 'w', encoding='utf-8') as f:
                    json.dump(session['chat_history'], f, indent=2, ensure_ascii=False)
                export_files.append(chat_file)

            # Export flashcards as CSV
            if 'flashcards' in request.export_options and session['flashcards']:
                flashcard_file = os.path.join(temp_dir, 'flashcards.csv')
                with open(flashcard_file, 'w', encoding='utf-8') as f:
                    f.write("Front,Back,Level,Tags\n")
                    for card_set in session['flashcards']:
                        for card in card_set['cards']:
                            f.write(f'"{card["front"]}","{card["back"]}","{card["level"]}","{",".join(card.get("tags", []))}"\n')
                export_files.append(flashcard_file)

            # Create ZIP file
            zip_handle = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            zip_path = zip_handle.name
            zip_handle.close()

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in export_files:
                    zipf.write(file_path, os.path.basename(file_path))

                # Add session metadata
                metadata = {
                    'session_id': request.session_id,
                    'created_at': session['created_at'],
                    'exported_at': datetime.now().isoformat(),
                    'documents': session['documents'],
                    'stats': {
                        'total_documents': len(session['documents']),
                        'chat_messages': len(session['chat_history']),
                        'summaries': len(session['summaries']),
                        'flashcards': sum(len(fs['cards']) for fs in session['flashcards']),
                        'quizzes': len(session['quizzes'])
                    }
                }

                zipf.writestr('session_metadata.json', json.dumps(metadata, indent=2))

            # Return the ZIP file and clean it up afterwards
            from starlette.background import BackgroundTask

            return FileResponse(
                zip_path,
                media_type='application/zip',
                filename=f'kensho_session_{request.session_id}.zip',
                background=BackgroundTask(lambda: os.remove(zip_path))
            )
        finally:
            # Clean the temp dir holding intermediate export files
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting session: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

# Main entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="🌌 Kensho FastAPI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print("🌌 Starting Kensho FastAPI Server...")
    print(f"📍 Server: http://{args.host}:{args.port}")
    print(f"📚 API Docs: http://{args.host}:{args.port}/docs")
    print("🧘‍♂️ Ready for mindful learning!")
    
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    ) 