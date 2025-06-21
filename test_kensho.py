#!/usr/bin/env python3
"""
🌌 Kensho - Basic Functionality Test
Simple test to verify installation and core functionality.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from kensho import DocumentProcessor, KenshoVectorStore, KenshoAIAssistant
        print("✅ Core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_document_processor():
    """Test document processing functionality."""
    print("🧪 Testing document processor...")
    
    try:
        from kensho import DocumentProcessor
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = DocumentProcessor(sessions_dir=temp_dir)
            
            # Test text processing
            test_text = "This is a test document for Kensho. It contains some sample text to verify the processing functionality."
            session_id, full_text, chunks = processor.process_text(test_text, "test_document")
            
            assert session_id is not None
            assert full_text == test_text
            assert len(chunks) > 0
            assert chunks[0]['text'] == test_text
            
            print("✅ Document processor working correctly")
            return True
            
    except Exception as e:
        print(f"❌ Document processor error: {e}")
        return False

def test_vector_store():
    """Test vector store functionality."""
    print("🧪 Testing vector store...")
    
    try:
        from kensho import KenshoVectorStore
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = KenshoVectorStore(sessions_dir=temp_dir)
            
            # Create test chunks
            test_chunks = [
                {
                    'id': 0,
                    'text': 'Machine learning is a subset of artificial intelligence.',
                    'type': 'text',
                    'source': 'test',
                    'source_info': {},
                    'chunk_index': 0,
                    'total_chunks': 2
                },
                {
                    'id': 1,
                    'text': 'Deep learning uses neural networks with multiple layers.',
                    'type': 'text',
                    'source': 'test',
                    'source_info': {},
                    'chunk_index': 1,
                    'total_chunks': 2
                }
            ]
            
            # Test index building
            success = vector_store.build_index("test_session", test_chunks)
            assert success, "Failed to build index"
            
            # Test searching
            results = vector_store.search("test_session", "What is machine learning?", top_k=1)
            assert len(results) > 0, "No search results returned"
            assert 'machine learning' in results[0]['text'].lower()
            
            print("✅ Vector store working correctly")
            return True
            
    except Exception as e:
        print(f"❌ Vector store error: {e}")
        return False

def test_ai_assistant():
    """Test AI assistant functionality (without API calls)."""
    print("🧪 Testing AI assistant...")
    
    try:
        from kensho import KenshoAIAssistant
        
        # Just test initialization
        assistant = KenshoAIAssistant()
        
        # Test helper methods
        test_chunks = [
            {
                'id': 0,
                'text': 'Test content for AI assistant',
                'source_info': {'page': 1}
            }
        ]
        
        context = assistant._prepare_context(test_chunks)
        assert 'Test content' in context
        assert '[source: page 1]' in context
        
        print("✅ AI assistant initialized correctly")
        return True
        
    except Exception as e:
        print(f"❌ AI assistant error: {e}")
        return False

def test_environment():
    """Test environment setup."""
    print("🧪 Testing environment...")
    
    # Check for API keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not gemini_key and not openai_key:
        print("⚠️  No AI API keys found (GEMINI_API_KEY or OPENAI_API_KEY)")
        print("   This is OK for testing, but you'll need API keys to run Kensho")
        return True
    
    if gemini_key:
        print("✅ Gemini API key found")
    
    if openai_key:
        print("✅ OpenAI API key found")
        
    if groq_key:
        print("✅ Groq API key found")
    else:
        print("⚠️  No Groq API key found (YouTube transcription will not work)")
    
    return True

def main():
    """Run all tests."""
    print("🌌 Kensho - Running Basic Tests")
    print("=" * 50)
    
    tests = [
        test_environment,
        test_imports,
        test_document_processor,
        test_vector_store,
        test_ai_assistant
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"🧪 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Kensho is ready to use.")
        print("Run 'python app.py' or 'python run.py' to start the application.")
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        print("Try: pip install -r requirements.txt")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 