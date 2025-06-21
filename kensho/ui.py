#!/usr/bin/env python3
"""
Kensho UI Module
Beautiful, Zen-inspired Gradio interface for the AI learning assistant.
"""

import os
import json
import tempfile
import zipfile
from typing import List, Dict, Any, Optional, Tuple
import gradio as gr
import pandas as pd

from .document_processor import DocumentProcessor
from .vector_store import KenshoVectorStore
from .ai_assistant import KenshoAIAssistant


class KenshoUI:
    """Zen-inspired UI for Kensho AI learning assistant."""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.vector_store = KenshoVectorStore()
        self.ai_assistant = KenshoAIAssistant()
        self.current_session = None
        
        # Custom CSS for Zen aesthetic
        self.css = """
        /* Kensho Zen Aesthetic */
        :root {
            --kensho-void: #0f0f1a;
            --kensho-white: #ffffff;
            --kensho-clarity: #6dd3ff;
            --kensho-warmth: #ffaa88;
            --kensho-subtle: #2a2a3a;
        }
        
        .gradio-container {
            background: linear-gradient(135deg, var(--kensho-void) 0%, #1a1a2e 100%);
            color: var(--kensho-white);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .kensho-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(45deg, var(--kensho-clarity), var(--kensho-warmth));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 300;
            letter-spacing: 0.1em;
        }
        
        .kensho-tagline {
            text-align: center;
            color: var(--kensho-clarity);
            font-size: 1.1rem;
            margin-bottom: 2rem;
            opacity: 0.8;
        }
        
        .kensho-card {
            background: rgba(42, 42, 58, 0.6);
            border: 1px solid rgba(109, 211, 255, 0.2);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .kensho-card:hover {
            border-color: rgba(109, 211, 255, 0.5);
            box-shadow: 0 8px 32px rgba(109, 211, 255, 0.1);
        }
        
        .kensho-button {
            background: linear-gradient(45deg, var(--kensho-clarity), var(--kensho-warmth));
            border: none;
            border-radius: 8px;
            color: var(--kensho-void);
            font-weight: 600;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
        }
        
        .kensho-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(109, 211, 255, 0.3);
        }
        
        .kensho-tab {
            background: var(--kensho-subtle);
            border-color: rgba(109, 211, 255, 0.3);
            color: var(--kensho-white);
        }
        
        .kensho-tab.selected {
            background: var(--kensho-clarity);
            color: var(--kensho-void);
        }
        
        .kensho-chat-user {
            background: linear-gradient(45deg, var(--kensho-clarity), rgba(109, 211, 255, 0.8));
            color: var(--kensho-void);
            border-radius: 18px 18px 4px 18px;
            padding: 1rem;
            margin: 0.5rem 0;
            max-width: 80%;
            margin-left: auto;
        }
        
        .kensho-chat-assistant {
            background: rgba(42, 42, 58, 0.8);
            color: var(--kensho-white);
            border: 1px solid rgba(109, 211, 255, 0.3);
            border-radius: 18px 18px 18px 4px;
            padding: 1rem;
            margin: 0.5rem 0;
            max-width: 80%;
        }
        
        .kensho-flashcard {
            background: var(--kensho-subtle);
            border: 2px solid var(--kensho-clarity);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .kensho-flashcard:hover {
            transform: rotateY(5deg);
            box-shadow: 0 12px 40px rgba(109, 211, 255, 0.2);
        }
        
        .kensho-progress {
            background: var(--kensho-subtle);
            border-radius: 10px;
            overflow: hidden;
            height: 8px;
        }
        
        .kensho-progress-bar {
            background: linear-gradient(90deg, var(--kensho-clarity), var(--kensho-warmth));
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .kensho-insight-panel {
            background: rgba(255, 170, 136, 0.1);
            border-left: 4px solid var(--kensho-warmth);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
        }
        
        .kensho-citation {
            background: rgba(109, 211, 255, 0.1);
            color: var(--kensho-clarity);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
            margin: 0 0.2rem;
        }
        """
    
    def create_interface(self) -> gr.Blocks:
        """Create the main Gradio interface."""
        
        with gr.Blocks(css=self.css, title="🌌 Kensho - AI Learning Mirror", theme=gr.themes.Soft()) as interface:
            
            # Header
            gr.HTML("""
            <div class="kensho-header">
                🌌 Kensho
            </div>
            <div class="kensho-tagline">
                Your personal AI mirror for deep learning and awakening
            </div>
            """)
            
            # Session state
            session_state = gr.State(None)
            
            with gr.Row():
                with gr.Column(scale=1):
                    # Left sidebar - Upload and Navigation
                    with gr.Group():
                        gr.HTML("<h3 style='color: #6dd3ff; text-align: center;'>📁 Knowledge Ingestion</h3>")
                        
                        # Upload options
                        with gr.Tabs():
                            with gr.Tab("📄 PDF Upload"):
                                pdf_file = gr.File(
                                    label="Upload PDF Document",
                                    file_types=[".pdf"],
                                    elem_classes=["kensho-card"]
                                )
                                pdf_upload_btn = gr.Button(
                                    "Process PDF",
                                    elem_classes=["kensho-button"],
                                    variant="primary"
                                )
                            
                            with gr.Tab("📝 Text Input"):
                                text_input = gr.Textbox(
                                    label="Paste your text here",
                                    lines=10,
                                    placeholder="Enter text to learn from...",
                                    elem_classes=["kensho-card"]
                                )
                                text_upload_btn = gr.Button(
                                    "Process Text",
                                    elem_classes=["kensho-button"],
                                    variant="primary"
                                )
                            
                            with gr.Tab("🎥 YouTube Video"):
                                youtube_url = gr.Textbox(
                                    label="YouTube URL",
                                    placeholder="https://youtube.com/watch?v=...",
                                    elem_classes=["kensho-card"]
                                )
                                youtube_upload_btn = gr.Button(
                                    "Process Video",
                                    elem_classes=["kensho-button"],
                                    variant="primary"
                                )
                        
                        # Processing status
                        processing_status = gr.HTML("")
                        processing_progress = gr.HTML("")
                
                with gr.Column(scale=3):
                    # Main content area
                    with gr.Tabs() as main_tabs:
                        
                        # Summary Tab
                        with gr.Tab("📜 Summary", id="summary"):
                            with gr.Group():
                                gr.HTML("<h3 style='color: #6dd3ff;'>📜 Document Summary</h3>")
                                
                                with gr.Row():
                                    summary_type = gr.Dropdown(
                                        choices=["comprehensive", "key_points", "executive"],
                                        value="comprehensive",
                                        label="Summary Type"
                                    )
                                    generate_summary_btn = gr.Button(
                                        "Generate Summary",
                                        elem_classes=["kensho-button"]
                                    )
                                
                                summary_output = gr.Markdown(
                                    label="Summary",
                                    elem_classes=["kensho-card"]
                                )
                                
                                with gr.Row():
                                    simplify_btn = gr.Button("Simplify", size="sm")
                                    deepen_btn = gr.Button("Explain Deeper", size="sm")
                        
                        # Chat Tab
                        with gr.Tab("💬 Chat", id="chat"):
                            with gr.Group():
                                gr.HTML("<h3 style='color: #6dd3ff;'>💬 Ask Questions</h3>")
                                
                                chatbot = gr.Chatbot(
                                    label="Kensho Assistant",
                                    elem_classes=["kensho-card"],
                                    height=400
                                )
                                
                                with gr.Row():
                                    chat_input = gr.Textbox(
                                        label="Your Question",
                                        placeholder="Ask me anything about your document...",
                                        scale=4
                                    )
                                    chat_send_btn = gr.Button(
                                        "Send",
                                        elem_classes=["kensho-button"],
                                        scale=1
                                    )
                                
                                with gr.Row():
                                    cite_sources_btn = gr.Button("Cite Sources", size="sm")
                                    ask_why_btn = gr.Button("Why does this matter?", size="sm")
                                    voice_input_btn = gr.Button("🎤 Voice", size="sm")
                        
                        # Flashcards Tab
                        with gr.Tab("🧩 Flashcards", id="flashcards"):
                            with gr.Group():
                                gr.HTML("<h3 style='color: #6dd3ff;'>🧩 Study Flashcards</h3>")
                                
                                with gr.Row():
                                    num_flashcards = gr.Slider(
                                        minimum=5,
                                        maximum=20,
                                        value=10,
                                        step=1,
                                        label="Number of Flashcards"
                                    )
                                    generate_flashcards_btn = gr.Button(
                                        "Generate Flashcards",
                                        elem_classes=["kensho-button"]
                                    )
                                
                                # Flashcard display
                                flashcard_display = gr.HTML(
                                    """
                                    <div class="kensho-flashcard">
                                        <div style="font-size: 1.2rem;">
                                            Generate flashcards to start studying
                                        </div>
                                    </div>
                                    """,
                                    elem_classes=["kensho-card"]
                                )
                                
                                # Flashcard controls
                                with gr.Row():
                                    prev_card_btn = gr.Button("← Previous", size="sm")
                                    flip_card_btn = gr.Button("🔄 Flip Card", elem_classes=["kensho-button"])
                                    next_card_btn = gr.Button("Next →", size="sm")
                                
                                with gr.Row():
                                    know_it_btn = gr.Button("✅ I know this", variant="secondary")
                                    review_btn = gr.Button("🔄 Need to review", variant="secondary")
                                
                                # Progress
                                flashcard_progress = gr.HTML("")
                        
                        # Quiz Tab
                        with gr.Tab("📝 Quiz", id="quiz"):
                            with gr.Group():
                                gr.HTML("<h3 style='color: #6dd3ff;'>📝 Test Your Knowledge</h3>")
                                
                                with gr.Row():
                                    num_questions = gr.Slider(
                                        minimum=3,
                                        maximum=10,
                                        value=5,
                                        step=1,
                                        label="Number of Questions"
                                    )
                                    quiz_difficulty = gr.Dropdown(
                                        choices=["easy", "medium", "hard", "mixed"],
                                        value="mixed",
                                        label="Difficulty"
                                    )
                                    generate_quiz_btn = gr.Button(
                                        "Generate Quiz",
                                        elem_classes=["kensho-button"]
                                    )
                                
                                # Quiz display
                                quiz_display = gr.HTML(
                                    """
                                    <div class="kensho-card">
                                        <h4>Ready to test your knowledge?</h4>
                                        <p>Generate a quiz to begin.</p>
                                    </div>
                                    """
                                )
                                
                                # Quiz controls
                                quiz_controls = gr.HTML("", visible=False)
                                quiz_results = gr.HTML("", visible=False)
                        
                        # Export Tab
                        with gr.Tab("📁 Export", id="export"):
                            with gr.Group():
                                gr.HTML("<h3 style='color: #6dd3ff;'>📁 Export Your Session</h3>")
                                
                                export_options = gr.CheckboxGroup(
                                    choices=[
                                        "Summary (.md)",
                                        "Q&A History (.json)",
                                        "Flashcards (.csv)",
                                        "Vector Index (.faiss)",
                                        "Full Session Bundle (.zip)"
                                    ],
                                    value=["Summary (.md)", "Q&A History (.json)"],
                                    label="What to Export"
                                )
                                
                                export_btn = gr.Button(
                                    "📦 Download Session",
                                    elem_classes=["kensho-button"],
                                    variant="primary"
                                )
                                
                                export_file = gr.File(
                                    label="Download Ready",
                                    visible=False
                                )
                
                with gr.Column(scale=1):
                    # Right sidebar - Assistant Insights
                    with gr.Group():
                        gr.HTML("<h3 style='color: #ffaa88; text-align: center;'>🧘‍♂️ Insights</h3>")
                        
                        insights_panel = gr.HTML(
                            """
                            <div class="kensho-insight-panel">
                                <p><strong>💡 Welcome to Kensho</strong></p>
                                <p>Upload a document to begin your learning journey.</p>
                                <p>I'll guide you with insights and suggestions along the way.</p>
                            </div>
                            """,
                            elem_classes=["kensho-card"]
                        )
                        
                        # Session info
                        session_info = gr.HTML("")
            
            # Event handlers
            self._setup_event_handlers(
                pdf_file, pdf_upload_btn, text_input, text_upload_btn,
                youtube_url, youtube_upload_btn, processing_status, processing_progress,
                session_state, summary_type, generate_summary_btn, summary_output,
                chatbot, chat_input, chat_send_btn, num_flashcards, generate_flashcards_btn,
                flashcard_display, flip_card_btn, prev_card_btn, next_card_btn,
                num_questions, quiz_difficulty, generate_quiz_btn, quiz_display,
                export_options, export_btn, export_file, insights_panel, session_info
            )
        
        return interface
    
    def _setup_event_handlers(self, *components):
        """Setup all event handlers for the interface."""
        (pdf_file, pdf_upload_btn, text_input, text_upload_btn,
         youtube_url, youtube_upload_btn, processing_status, processing_progress,
         session_state, summary_type, generate_summary_btn, summary_output,
         chatbot, chat_input, chat_send_btn, num_flashcards, generate_flashcards_btn,
         flashcard_display, flip_card_btn, prev_card_btn, next_card_btn,
         num_questions, quiz_difficulty, generate_quiz_btn, quiz_display,
         export_options, export_btn, export_file, insights_panel, session_info) = components
        
        # PDF upload
        pdf_upload_btn.click(
            fn=self.process_pdf,
            inputs=[pdf_file, session_state],
            outputs=[session_state, processing_status, insights_panel, session_info]
        )
        
        # Text upload
        text_upload_btn.click(
            fn=self.process_text,
            inputs=[text_input, session_state],
            outputs=[session_state, processing_status, insights_panel, session_info]
        )
        
        # YouTube upload
        youtube_upload_btn.click(
            fn=self.process_youtube,
            inputs=[youtube_url, session_state],
            outputs=[session_state, processing_status, processing_progress, insights_panel, session_info]
        )
        
        # Summary generation
        generate_summary_btn.click(
            fn=self.generate_summary,
            inputs=[session_state, summary_type],
            outputs=[summary_output, insights_panel]
        )
        
        # Chat
        chat_send_btn.click(
            fn=self.chat_response,
            inputs=[chat_input, chatbot, session_state],
            outputs=[chatbot, chat_input, insights_panel]
        )
        
        chat_input.submit(
            fn=self.chat_response,
            inputs=[chat_input, chatbot, session_state],
            outputs=[chatbot, chat_input, insights_panel]
        )
        
        # Flashcards
        generate_flashcards_btn.click(
            fn=self.generate_flashcards,
            inputs=[session_state, num_flashcards],
            outputs=[flashcard_display, insights_panel]
        )
        
        # Quiz
        generate_quiz_btn.click(
            fn=self.generate_quiz,
            inputs=[session_state, num_questions, quiz_difficulty],
            outputs=[quiz_display, insights_panel]
        )
        
        # Export
        export_btn.click(
            fn=self.export_session,
            inputs=[session_state, export_options],
            outputs=[export_file, insights_panel]
        )
    
    # Processing methods
    
    def process_pdf(self, pdf_file, session_state):
        """Process uploaded PDF file."""
        if not pdf_file:
            return session_state, "❌ Please upload a PDF file.", self._get_error_insights(), ""
        
        try:
            session_id, full_text, chunks = self.doc_processor.process_pdf(pdf_file.name)
            
            # Build vector index
            self.vector_store.build_index(session_id, chunks)
            
            session_data = {
                'id': session_id,
                'type': 'pdf',
                'source': pdf_file.name,
                'chunks': chunks,
                'full_text': full_text
            }
            
            status = f"✅ PDF processed successfully! Session ID: `{session_id}`"
            insights = self._get_success_insights(session_data)
            info = self._get_session_info(session_data)
            
            return session_data, status, insights, info
            
        except Exception as e:
            error_msg = f"❌ Error processing PDF: {str(e)}"
            return session_state, error_msg, self._get_error_insights(), ""
    
    def process_text(self, text_input, session_state):
        """Process text input."""
        if not text_input or not text_input.strip():
            return session_state, "❌ Please enter some text.", self._get_error_insights(), ""
        
        try:
            session_id, full_text, chunks = self.doc_processor.process_text(text_input)
            
            # Build vector index
            self.vector_store.build_index(session_id, chunks)
            
            session_data = {
                'id': session_id,
                'type': 'text',
                'source': 'text_input',
                'chunks': chunks,
                'full_text': full_text
            }
            
            status = f"✅ Text processed successfully! Session ID: `{session_id}`"
            insights = self._get_success_insights(session_data)
            info = self._get_session_info(session_data)
            
            return session_data, status, insights, info
            
        except Exception as e:
            error_msg = f"❌ Error processing text: {str(e)}"
            return session_state, error_msg, self._get_error_insights(), ""
    
    def process_youtube(self, youtube_url, session_state):
        """Process YouTube video with progress updates."""
        if not youtube_url or not youtube_url.strip():
            return session_state, "❌ Please enter a YouTube URL.", "", self._get_error_insights(), ""
        
        try:
            # This would need to be implemented as a generator for real-time updates
            # For now, we'll simulate the process
            
            status = "🎥 Processing YouTube video..."
            progress = '<div class="kensho-progress"><div class="kensho-progress-bar" style="width: 10%;"></div></div>'
            
            # In a real implementation, you'd use the generator from document_processor
            # For now, we'll create a simple placeholder
            
            session_data = {
                'id': 'youtube_demo',
                'type': 'youtube',
                'source': youtube_url,
                'chunks': [],
                'full_text': "YouTube processing would happen here..."
            }
            
            final_status = f"✅ YouTube video processed! Session ID: `youtube_demo`"
            final_progress = '<div class="kensho-progress"><div class="kensho-progress-bar" style="width: 100%;"></div></div>'
            insights = self._get_success_insights(session_data)
            info = self._get_session_info(session_data)
            
            return session_data, final_status, final_progress, insights, info
            
        except Exception as e:
            error_msg = f"❌ Error processing YouTube video: {str(e)}"
            return session_state, error_msg, "", self._get_error_insights(), ""
    
    def generate_summary(self, session_state, summary_type):
        """Generate summary of the document."""
        if not session_state:
            return "❌ Please upload a document first.", self._get_error_insights()
        
        try:
            summary_result = self.ai_assistant.generate_summary(
                session_state['full_text'], 
                summary_type=summary_type
            )
            
            summary_md = f"""
            ## {summary_type.title()} Summary
            
            {summary_result['summary']}
            
            ---
            
            **Key Topics:** {', '.join(summary_result['key_topics'][:5])}
            
            **Word Count:** {summary_result['word_count']} words
            """
            
            insights = f"""
            <div class="kensho-insight-panel">
                <p><strong>📝 Summary Generated</strong></p>
                <p>Type: {summary_type.title()}</p>
                <p>Key topics identified: {len(summary_result['key_topics'])}</p>
                <p><em>Try asking specific questions about these topics!</em></p>
            </div>
            """
            
            return summary_md, insights
            
        except Exception as e:
            error_msg = f"❌ Error generating summary: {str(e)}"
            return error_msg, self._get_error_insights()
    
    def chat_response(self, message, chat_history, session_state):
        """Handle chat interactions."""
        if not session_state:
            error_response = "❌ Please upload a document first to start chatting."
            chat_history.append([message, error_response])
            return chat_history, "", self._get_error_insights()
        
        if not message or not message.strip():
            return chat_history, "", self._get_current_insights(session_state)
        
        try:
            # Search for relevant chunks
            relevant_chunks = self.vector_store.search(session_state['id'], message, top_k=5)
            
            # Generate response
            response_data = self.ai_assistant.answer_question(
                message, relevant_chunks, session_state
            )
            
            # Format response with citations
            response_text = response_data['answer']
            if response_data['citations']:
                citations_text = " | ".join([f"<span class='kensho-citation'>{cite}</span>" for cite in response_data['citations']])
                response_text += f"\n\n**Sources:** {citations_text}"
            
            chat_history.append([message, response_text])
            
            insights = f"""
            <div class="kensho-insight-panel">
                <p><strong>💬 Question Answered</strong></p>
                <p>Confidence: {response_data['confidence']:.1%}</p>
                <p>Sources used: {response_data['context_chunks_used']}</p>
                <p><em>Want to explore deeper? Try asking "Why is this important?"</em></p>
            </div>
            """
            
            return chat_history, "", insights
            
        except Exception as e:
            error_response = f"❌ Error generating response: {str(e)}"
            chat_history.append([message, error_response])
            return chat_history, "", self._get_error_insights()
    
    def generate_flashcards(self, session_state, num_cards):
        """Generate flashcards for studying."""
        if not session_state:
            return "❌ Please upload a document first.", self._get_error_insights()
        
        try:
            flashcards = self.ai_assistant.generate_flashcards(
                session_state['chunks'], 
                num_cards=num_cards
            )
            
            if flashcards:
                # Display first flashcard
                first_card = flashcards[0]
                card_html = f"""
                <div class="kensho-flashcard" onclick="this.querySelector('.card-back').style.display = this.querySelector('.card-back').style.display === 'none' ? 'block' : 'none';">
                    <div class="card-front">
                        <h3>Question</h3>
                        <p style="font-size: 1.1rem; margin: 1rem 0;">{first_card['question']}</p>
                        <small>Click to reveal answer</small>
                    </div>
                    <div class="card-back" style="display: none;">
                        <h3>Answer</h3>
                        <p style="font-size: 1.1rem; margin: 1rem 0;">{first_card['answer']}</p>
                        <small>Difficulty: {first_card.get('difficulty', 'N/A')} | Level: {first_card.get('bloom_level', 'N/A')}</small>
                    </div>
                </div>
                """
                
                insights = f"""
                <div class="kensho-insight-panel">
                    <p><strong>🧩 Flashcards Ready</strong></p>
                    <p>Generated {len(flashcards)} cards</p>
                    <p>Mix of cognitive levels for deep learning</p>
                    <p><em>Use the flip and navigation buttons to study!</em></p>
                </div>
                """
                
                return card_html, insights
            else:
                return "❌ No flashcards generated. Please try again.", self._get_error_insights()
                
        except Exception as e:
            error_msg = f"❌ Error generating flashcards: {str(e)}"
            return error_msg, self._get_error_insights()
    
    def generate_quiz(self, session_state, num_questions, difficulty):
        """Generate quiz for testing knowledge."""
        if not session_state:
            return "❌ Please upload a document first.", self._get_error_insights()
        
        try:
            quiz_data = self.ai_assistant.generate_quiz(
                session_state['chunks'], 
                num_questions=num_questions,
                difficulty=difficulty
            )
            
            if quiz_data and 'questions' in quiz_data:
                # Display first question
                first_q = quiz_data['questions'][0]
                
                quiz_html = f"""
                <div class="kensho-card">
                    <h3>Question 1 of {len(quiz_data['questions'])}</h3>
                    <p style="font-size: 1.1rem; margin: 1rem 0;"><strong>{first_q['question']}</strong></p>
                    
                    <div style="margin: 1rem 0;">
                        <div style="margin: 0.5rem 0; padding: 0.5rem; background: rgba(109, 211, 255, 0.1); border-radius: 6px; cursor: pointer;">
                            A) {first_q['options'][0] if len(first_q['options']) > 0 else 'Option A'}
                        </div>
                        <div style="margin: 0.5rem 0; padding: 0.5rem; background: rgba(109, 211, 255, 0.1); border-radius: 6px; cursor: pointer;">
                            B) {first_q['options'][1] if len(first_q['options']) > 1 else 'Option B'}
                        </div>
                        <div style="margin: 0.5rem 0; padding: 0.5rem; background: rgba(109, 211, 255, 0.1); border-radius: 6px; cursor: pointer;">
                            C) {first_q['options'][2] if len(first_q['options']) > 2 else 'Option C'}
                        </div>
                        <div style="margin: 0.5rem 0; padding: 0.5rem; background: rgba(109, 211, 255, 0.1); border-radius: 6px; cursor: pointer;">
                            D) {first_q['options'][3] if len(first_q['options']) > 3 else 'Option D'}
                        </div>
                    </div>
                    
                    <p><small>Difficulty: {first_q.get('difficulty', difficulty)}</small></p>
                </div>
                """
                
                insights = f"""
                <div class="kensho-insight-panel">
                    <p><strong>📝 Quiz Ready</strong></p>
                    <p>{len(quiz_data['questions'])} questions</p>
                    <p>Difficulty: {difficulty}</p>
                    <p><em>Take your time and think deeply about each answer!</em></p>
                </div>
                """
                
                return quiz_html, insights
            else:
                return "❌ No quiz generated. Please try again.", self._get_error_insights()
                
        except Exception as e:
            error_msg = f"❌ Error generating quiz: {str(e)}"
            return error_msg, self._get_error_insights()
    
    def export_session(self, session_state, export_options):
        """Export session data in various formats."""
        if not session_state:
            return None, self._get_error_insights()
        
        try:
            # Create temporary directory for export files
            temp_dir = tempfile.mkdtemp()
            files_to_zip = []
            
            session_id = session_state['id']
            
            # Export summary
            if "Summary (.md)" in export_options:
                summary_result = self.ai_assistant.generate_summary(session_state['full_text'])
                summary_path = os.path.join(temp_dir, f"{session_id}_summary.md")
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Kensho Session Summary\n\n")
                    f.write(f"**Session ID:** {session_id}\n")
                    f.write(f"**Type:** {session_state['type']}\n")
                    f.write(f"**Source:** {session_state['source']}\n\n")
                    f.write(f"## Summary\n\n{summary_result['summary']}\n\n")
                    f.write(f"## Key Topics\n\n")
                    for topic in summary_result['key_topics']:
                        f.write(f"- {topic}\n")
                files_to_zip.append(summary_path)
            
            # Export flashcards
            if "Flashcards (.csv)" in export_options:
                flashcards = self.ai_assistant.generate_flashcards(session_state['chunks'])
                csv_path = os.path.join(temp_dir, f"{session_id}_flashcards.csv")
                
                df = pd.DataFrame(flashcards)
                df.to_csv(csv_path, index=False)
                files_to_zip.append(csv_path)
            
            # Create zip file
            zip_path = os.path.join(temp_dir, f"kensho_session_{session_id}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in files_to_zip:
                    zipf.write(file_path, os.path.basename(file_path))
            
            insights = f"""
            <div class="kensho-insight-panel">
                <p><strong>📦 Export Ready</strong></p>
                <p>Session: {session_id}</p>
                <p>Files: {len(files_to_zip)} items</p>
                <p><em>Your learning journey is preserved!</em></p>
            </div>
            """
            
            return zip_path, insights
            
        except Exception as e:
            error_msg = f"❌ Error exporting session: {str(e)}"
            return None, self._get_error_insights()
    
    # Helper methods for UI insights
    
    def _get_success_insights(self, session_data):
        """Get insights panel content for successful processing."""
        return f"""
        <div class="kensho-insight-panel">
            <p><strong>✨ Document Processed</strong></p>
            <p>Type: {session_data['type'].upper()}</p>
            <p>Chunks: {len(session_data['chunks'])}</p>
            <p><em>Ready to explore! Try generating a summary or asking questions.</em></p>
        </div>
        """
    
    def _get_error_insights(self):
        """Get insights panel content for errors."""
        return """
        <div class="kensho-insight-panel">
            <p><strong>⚠️ Something went wrong</strong></p>
            <p>Please check your input and try again.</p>
            <p><em>Remember: Kensho learns from your content to guide you.</em></p>
        </div>
        """
    
    def _get_current_insights(self, session_state):
        """Get current insights based on session state."""
        if not session_state:
            return """
            <div class="kensho-insight-panel">
                <p><strong>🌱 Ready to Begin</strong></p>
                <p>Upload a document to start your learning journey.</p>
                <p><em>Kensho will adapt to your content and learning style.</em></p>
            </div>
            """
        
        return f"""
        <div class="kensho-insight-panel">
            <p><strong>🧠 Session Active</strong></p>
            <p>Document: {session_state['type']}</p>
            <p>Ready for questions, summaries, or study materials.</p>
            <p><em>What would you like to explore next?</em></p>
        </div>
        """
    
    def _get_session_info(self, session_data):
        """Get session information display."""
        return f"""
        <div class="kensho-card" style="margin-top: 1rem;">
            <h4 style="color: #6dd3ff;">📊 Session Info</h4>
            <p><strong>ID:</strong> {session_data['id']}</p>
            <p><strong>Type:</strong> {session_data['type'].upper()}</p>
            <p><strong>Chunks:</strong> {len(session_data['chunks'])}</p>
            <p><strong>Text Length:</strong> {len(session_data['full_text'])} chars</p>
        </div>
        """


def create_kensho_app():
    """Create and return the Kensho Gradio application."""
    kensho_ui = KenshoUI()
    return kensho_ui.create_interface() 