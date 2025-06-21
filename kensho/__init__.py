#!/usr/bin/env python3
"""
🌌 Kensho - Your Personal AI Mirror for Insight, Learning, and Awakening

A privacy-first, local AI learning assistant that helps you understand deeply,
not just memorize. Built with FastAPI, FAISS, Gemini, and Whisper.

"See through. Learn deeply. Own the mirror."
"""

__version__ = "1.0.0"
__author__ = "Kensho AI"
__description__ = "Privacy-first AI learning assistant for deep understanding"

from .document_processor import DocumentProcessor
from .vector_store import KenshoVectorStore
from .ai_assistant import KenshoAIAssistant
from .ui import KenshoUI, create_kensho_app

__all__ = [
    "DocumentProcessor",
    "KenshoVectorStore", 
    "KenshoAIAssistant",
    "KenshoUI",
    "create_kensho_app"
] 