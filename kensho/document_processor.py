#!/usr/bin/env python3
"""
Kensho Document Processing Module
Handles PDF, text, and YouTube video ingestion with clean parsing and metadata extraction.
"""

import os
import re
import hashlib
import tempfile
from typing import List, Dict, Any, Optional, Tuple, Generator
from pathlib import Path
import json

# PDF and text processing
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Audio processing
from pydub import AudioSegment
import yt_dlp

# AI services
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq
from tqdm import tqdm

load_dotenv()


class DocumentProcessor:
    """Handles document ingestion, processing, and chunking for Kensho."""
    
    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = sessions_dir
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Initialize AI clients
        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
        
        if self.gemini_api_key:
            self.gemini_client = OpenAI(
                api_key=self.gemini_api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        os.makedirs(sessions_dir, exist_ok=True)
        print(f"💾 Sessions directory ready: {os.path.abspath(sessions_dir)}")
    
    def create_session_id(self, content: str) -> str:
        """Create a unique session ID based on content hash."""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def process_pdf(self, pdf_path: str) -> Tuple[str, str, List[Dict]]:
        """
        Process PDF file and extract clean text with metadata.
        
        Returns:
            Tuple of (session_id, full_text, chunks_with_metadata)
        """
        try:
            print(f"📄 Starting PDF processing for: {pdf_path}")
            
            doc = fitz.open(pdf_path)
            print(f"📄 PDF opened successfully. Pages: {len(doc)}")
            
            full_text = ""
            page_texts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Clean text - remove headers, footers, page numbers
                cleaned_text = self._clean_pdf_text(text)
                
                if cleaned_text.strip():
                    page_texts.append({
                        'page': page_num + 1,
                        'text': cleaned_text
                    })
                    full_text += f"\n[source: page {page_num + 1}]\n{cleaned_text}\n"
                
                print(f"📄 Processed page {page_num + 1}/{len(doc)}")
            
            doc.close()
            print(f"📄 Text extraction complete. Total length: {len(full_text)} characters, Pages with content: {len(page_texts)}")
            
            # Create temporary session ID for internal processing only
            print(f"📄 Creating temporary session ID for processing...")
            temp_session_id = self.create_session_id(full_text)
            print(f"📄 Temporary session ID created: {temp_session_id}")
            
            # Chunk the text
            print(f"📄 Creating chunks...")
            chunks = self._chunk_text_with_metadata(full_text, "pdf", pdf_path)
            print(f"📄 Created {len(chunks)} chunks")
            
            # Note: Don't save session data here as it will be handled by the API
            # The API will manage the session data using the correct session ID
            
            print(f"✅ PDF processing complete: {temp_session_id}, {len(full_text)} chars, {len(chunks)} chunks")
            return temp_session_id, full_text, chunks
            
        except Exception as e:
            error_msg = f"Error processing PDF: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def process_text(self, text: str, source_name: str = "text_input") -> Tuple[str, str, List[Dict]]:
        """
        Process raw text input.
        
        Returns:
            Tuple of (session_id, full_text, chunks_with_metadata)
        """
        try:
            # Create temporary session ID for internal processing only
            temp_session_id = self.create_session_id(text)
            
            # Chunk the text
            chunks = self._chunk_text_with_metadata(text, "text", source_name)
            
            # Note: Don't save session data here as it will be handled by the API
            # The API will manage the session data using the correct session ID
            
            return temp_session_id, text, chunks
            
        except Exception as e:
            raise Exception(f"Error processing text: {str(e)}")
    
    def process_youtube_video(self, url: str) -> Generator[Tuple[int, str, str], None, None]:
        """
        Process YouTube video with progress updates.
        
        Yields:
            Tuple of (progress_percentage, status_message, current_data)
        """
        try:
            print(f"🎥 Starting YouTube processing for: {url}")
            video_id = self._extract_video_id(url)
            print(f"🎥 Extracted video ID: {video_id}")
            yield 5, "Extracting video information...", ""
            
            # Download audio
            yield 10, "Downloading video audio...", ""
            audio_file = self._download_youtube_audio(video_id)
            
            if not audio_file:
                error_msg = "Failed to download video audio. This could be due to:\n1. Invalid YouTube URL\n2. Video is private or restricted\n3. Network connectivity issues\n4. Missing FFmpeg installation"
                print(f"❌ {error_msg}")
                yield 100, f"Error: {error_msg}", ""
                return
            
            print(f"✅ Audio downloaded successfully: {audio_file}")
            
            # Transcribe with progress
            yield 20, "Starting transcription...", ""
            
            transcript = ""
            transcription_error = False
            
            for progress, partial_transcript in self._transcribe_with_progress(audio_file):
                # Scale progress to 20-90 range
                scaled_progress = 20 + (progress * 0.7)
                yield scaled_progress, f"Transcribing: {progress:.1f}%", partial_transcript
                
                if "Error" in partial_transcript:
                    transcription_error = True
                    print(f"❌ Transcription error: {partial_transcript}")
                    yield 100, f"Error: {partial_transcript}", ""
                    return
                
                transcript = partial_transcript
            
            if not transcript or len(transcript.strip()) < 10:
                error_msg = "No transcript generated. The video might be silent or in a language not supported by the transcription service."
                print(f"❌ {error_msg}")
                yield 100, f"Error: {error_msg}", ""
                return
            
            print(f"✅ Transcription complete. Length: {len(transcript)} characters")
            
            # Process transcript
            yield 95, "Processing transcript...", transcript
            
            # Create chunks without creating a new session ID
            chunks = self._chunk_text_with_metadata(transcript, "youtube", url)
            
            print(f"✅ Created {len(chunks)} chunks from transcript")
            
            # Note: Don't save session data here as it will be handled by the API
            # The API will manage the session data using the correct session ID
            
            yield 100, "Processing complete!", {
                'transcript': transcript,
                'chunks': chunks
            }
            
        except Exception as e:
            error_msg = f"Error processing video: {str(e)}"
            print(f"❌ {error_msg}")
            yield 100, f"Error: {error_msg}", ""
    
    def _clean_pdf_text(self, text: str) -> str:
        """Clean PDF text by removing headers, footers, and page numbers."""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip likely headers/footers (very short lines at start/end)
            if len(line) < 10:
                continue
            
            # Skip page numbers
            if re.match(r'^\d+$', line):
                continue
            
            # Skip common header/footer patterns
            if re.match(r'^(page|chapter|\d+/\d+)', line.lower()):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _chunk_text_with_metadata(self, text: str, doc_type: str, source: str) -> List[Dict]:
        """Chunk text and add metadata for citations."""
        chunks = self.text_splitter.split_text(text)
        
        chunks_with_metadata = []
        for i, chunk in enumerate(chunks):
            # Extract source information from chunk if available
            source_info = self._extract_source_info(chunk)
            
            chunk_data = {
                'id': i,
                'text': chunk,
                'type': doc_type,
                'source': source,
                'source_info': source_info,
                'chunk_index': i,
                'total_chunks': len(chunks)
            }
            chunks_with_metadata.append(chunk_data)
        
        return chunks_with_metadata
    
    def _extract_source_info(self, chunk: str) -> Dict:
        """Extract source information from chunk text."""
        source_info = {}
        
        # Look for page references
        page_match = re.search(r'\[source: page (\d+)\]', chunk)
        if page_match:
            source_info['page'] = int(page_match.group(1))
        
        # Look for timestamp references
        time_match = re.search(r'\[timestamp: (\d{2}:\d{2})\]', chunk)
        if time_match:
            source_info['timestamp'] = time_match.group(1)
        
        return source_info
    
    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from URL."""
        patterns = [
            r"youtu\.be\/([^\/\?]+)",
            r"youtube\.com\/watch\?v=([^&]+)",
            r"youtube\.com\/embed\/([^\/\?]+)",
            r"youtube\.com\/v\/([^\/\?]+)",
            r"youtube\.com\/shorts\/([^\/\?]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return url  # Assume it's already a video ID
    
    def _download_youtube_audio(self, video_id: str) -> Optional[str]:
        """Download YouTube video audio."""
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"🎥 Downloading audio from: {video_url}")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            output_template = os.path.join(temp_dir, f"{video_id}.%(ext)s")
            
            # Try multiple audio extraction strategies
            ydl_opts_list = [
                # First try: with ffmpeg post-processing
                {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'outtmpl': output_template,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'quiet': True,
                    'no_warnings': True
                },
                # Second try: direct audio download without post-processing
                {
                    'format': 'bestaudio/best',
                    'outtmpl': output_template,
                    'quiet': True,
                    'no_warnings': True
                },
                # Third try: any available format
                {
                    'format': 'worst',
                    'outtmpl': output_template,
                    'quiet': True,
                    'no_warnings': True
                }
            ]
            
            for i, ydl_opts in enumerate(ydl_opts_list):
                try:
                    print(f"🎥 Attempt {i+1}: Trying audio extraction strategy")
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    
                    # Find any downloaded audio file
                    audio_extensions = ['.mp3', '.m4a', '.webm', '.ogg', '.wav']
                    audio_files = []
                    
                    for ext in audio_extensions:
                        files = [f for f in os.listdir(temp_dir) if f.endswith(ext)]
                        audio_files.extend([os.path.join(temp_dir, f) for f in files])
                    
                    if audio_files:
                        print(f"✅ Successfully downloaded: {audio_files[0]}")
                        return audio_files[0]
                        
                except Exception as e:
                    print(f"❌ Strategy {i+1} failed: {str(e)}")
                    continue
            
            print(f"❌ All download strategies failed for video: {video_id}")
            return None
            
        except Exception as e:
            print(f"❌ Error downloading YouTube audio: {str(e)}")
            return None
    
    def _transcribe_with_progress(self, audio_file: str) -> Generator[Tuple[float, str], None, None]:
        """Transcribe audio with progress updates."""
        try:
            file_size = os.path.getsize(audio_file)
            max_chunk_size = 25 * 1024 * 1024  # 25MB limit for Groq
            
            if file_size <= max_chunk_size:
                # Small file - transcribe directly
                yield 50, "Processing audio..."
                transcript = self._transcribe_with_groq(audio_file)
                yield 100, transcript
                return
            
            # Large file - split into chunks
            yield 10, "Splitting large audio file..."
            
            audio = AudioSegment.from_file(audio_file)
            bytes_per_ms = file_size / len(audio)
            max_chunk_duration = int(max_chunk_size / bytes_per_ms)
            
            chunks = [audio[i:i+max_chunk_duration] 
                     for i in range(0, len(audio), max_chunk_duration)]
            
            transcripts = []
            
            for i, chunk in enumerate(chunks):
                progress = 10 + (i / len(chunks) * 80)
                yield progress, f"Transcribing chunk {i+1}/{len(chunks)}..."
                
                # Export chunk to temporary file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    chunk_path = temp_file.name
                
                chunk.export(chunk_path, format="mp3")
                
                # Transcribe chunk
                chunk_transcript = self._transcribe_with_groq(chunk_path)
                transcripts.append(chunk_transcript)
                
                # Clean up
                os.unlink(chunk_path)
                
                # Yield current combined transcript
                current_transcript = " ".join(transcripts)
                yield progress, current_transcript
            
            final_transcript = " ".join(transcripts)
            yield 100, final_transcript
            
        except Exception as e:
            yield 100, f"Error transcribing audio: {str(e)}"
    
    def _transcribe_with_groq(self, audio_file: str) -> str:
        """Transcribe audio using Groq Whisper."""
        try:
            print(f"🎤 Starting Groq transcription for: {audio_file}")
            file_size = os.path.getsize(audio_file)
            print(f"🎤 Audio file size: {file_size / (1024*1024):.2f} MB")
            
            if file_size > 25 * 1024 * 1024:  # 25MB limit
                return f"Error: Audio file too large ({file_size / (1024*1024):.2f} MB). Maximum size is 25MB."
            
            with open(audio_file, "rb") as file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file), file.read()),
                    model="whisper-large-v3",
                )
            
            result_text = transcription.text.strip()
            print(f"✅ Transcription successful. Length: {len(result_text)} characters")
            return result_text
            
        except Exception as e:
            error_msg = f"Error transcribing with Groq: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def _save_session_data(self, session_id: str, data: Dict):
        """Save session data to files."""
        session_dir = os.path.join(self.sessions_dir, session_id)
        
        # Create session directory if it doesn't exist
        os.makedirs(session_dir, exist_ok=True)
        print(f"💾 Created session directory: {session_dir}")
        
        # Save metadata
        metadata_path = os.path.join(session_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump({
                'session_id': session_id,
                'type': data['type'],
                'source': data['source'],
                'created_at': str(Path().resolve()),
                'chunk_count': len(data['chunks'])
            }, f, indent=2)
        print(f"💾 Saved metadata to: {metadata_path}")
        
        # Save full text
        full_text_path = os.path.join(session_dir, "full_text.txt")
        with open(full_text_path, "w", encoding="utf-8") as f:
            f.write(data['full_text'])
        print(f"💾 Saved full text to: {full_text_path}")
        
        # Save chunks
        chunks_path = os.path.join(session_dir, "chunks.json")
        with open(chunks_path, "w") as f:
            json.dump(data['chunks'], f, indent=2)
        print(f"💾 Saved {len(data['chunks'])} chunks to: {chunks_path}")
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """Load session data from files."""
        session_dir = os.path.join(self.sessions_dir, session_id)
        
        if not os.path.exists(session_dir):
            return None
        
        try:
            # Load metadata
            with open(os.path.join(session_dir, "metadata.json"), "r") as f:
                metadata = json.load(f)
            
            # Load full text
            with open(os.path.join(session_dir, "full_text.txt"), "r", encoding="utf-8") as f:
                full_text = f.read()
            
            # Load chunks
            with open(os.path.join(session_dir, "chunks.json"), "r") as f:
                chunks = json.load(f)
            
            return {
                'metadata': metadata,
                'full_text': full_text,
                'chunks': chunks
            }
            
        except Exception as e:
            print(f"Error loading session {session_id}: {str(e)}")
            return None
    
    def list_sessions(self) -> List[Dict]:
        """List all available sessions."""
        sessions = []
        
        if not os.path.exists(self.sessions_dir):
            return sessions
        
        for session_id in os.listdir(self.sessions_dir):
            session_path = os.path.join(self.sessions_dir, session_id)
            if os.path.isdir(session_path):
                metadata_path = os.path.join(session_path, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                        sessions.append(metadata)
                    except:
                        continue
        
        return sorted(sessions, key=lambda x: x.get('created_at', ''), reverse=True) 