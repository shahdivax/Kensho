#!/usr/bin/env python3
"""
Kensho AI Assistant Module
Handles RAG-based QA, summarization, flashcard generation, and quiz creation.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# AI services
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class KenshoAIAssistant:
    """AI-powered assistant for learning and content generation."""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize AI clients
        if self.gemini_api_key:
            self.gemini_client = OpenAI(
                api_key=self.gemini_api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Default model selection
        self.default_model = "gemini-2.0-flash" if self.gemini_api_key else "gpt-4o-mini"
        self.client = self.gemini_client if self.gemini_api_key else self.openai_client
    
    def answer_question(self, question: str, context_chunks: List[Dict], 
                       session_metadata: Dict = None) -> Dict[str, Any]:
        """
        Answer a question using RAG with citation-aware responses.
        
        Args:
            question: User's question
            context_chunks: Relevant chunks from vector search
            session_metadata: Session metadata for context
            
        Returns:
            Dict with answer, sources, and confidence
        """
        try:
            # Prepare context
            context_text = self._prepare_context(context_chunks)
            
            # Create system prompt
            system_prompt = self._get_rag_system_prompt()
            
            # Create user prompt
            user_prompt = f"""
            Based on the following context from the document, please answer the question.
            
            CONTEXT:
            {context_text}
            
            QUESTION: {question}
            
            Please provide a comprehensive answer based on the context provided. 
            Include specific citations using the format [source: page X] or [timestamp: MM:SS] when referencing information.
            If the context doesn't contain enough information to fully answer the question, 
            please indicate what information is missing.
            """
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Extract citations and sources
            sources = self._extract_sources_from_chunks(context_chunks)
            citations = self._extract_citations_from_answer(answer)
            
            # Calculate confidence based on context relevance
            confidence = self._calculate_confidence(context_chunks, question)
            
            return {
                'answer': answer,
                'sources': sources,
                'citations': citations,
                'confidence': confidence,
                'context_chunks_used': len(context_chunks),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'answer': f"Error generating answer: {str(e)}",
                'sources': [],
                'citations': [],
                'confidence': 0.0,
                'context_chunks_used': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_summary(self, full_text: str, summary_type: str = "comprehensive", 
                        max_length: int = 500) -> Dict[str, Any]:
        """
        Generate different types of summaries from the full text.
        
        Args:
            full_text: Complete document text
            summary_type: Type of summary (comprehensive, key_points, executive)
            max_length: Maximum length in words
            
        Returns:
            Dict with summary and metadata
        """
        try:
            # Create system prompt based on summary type
            system_prompt = self._get_summary_system_prompt(summary_type)
            
            # Create user prompt
            user_prompt = f"""
            Please create a {summary_type} summary of the following text.
            Keep the summary under {max_length} words and maintain the key insights and important details.
            
            TEXT TO SUMMARIZE:
            {full_text[:8000]}  # Limit input to prevent token overflow
            """
            
            # Generate summary
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )
            
            summary = response.choices[0].message.content
            
            # Extract key topics
            topics = self._extract_key_topics(summary)
            
            return {
                'summary': summary,
                'type': summary_type,
                'word_count': len(summary.split()),
                'key_topics': topics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'summary': f"Error generating summary: {str(e)}",
                'type': summary_type,
                'word_count': 0,
                'key_topics': [],
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_flashcards(self, chunks: List[Dict], num_cards: int = 10) -> List[Dict]:
        """
        Generate flashcards from document chunks using Bloom's taxonomy.
        
        Args:
            chunks: Document chunks to generate flashcards from
            num_cards: Number of flashcards to generate
            
        Returns:
            List of flashcard dictionaries
        """
        try:
            # Select diverse chunks for flashcard generation
            selected_chunks = self._select_diverse_chunks(chunks, num_cards)
            
            # Prepare content for flashcard generation
            content = "\n\n".join([chunk['text'] for chunk in selected_chunks])
            
            system_prompt = """
            You are an expert educator creating flashcards based on Bloom's taxonomy.
            Create flashcards that test different levels of understanding:
            - Remember: Basic recall of facts
            - Understand: Comprehension of concepts
            - Apply: Using knowledge in new situations
            - Analyze: Breaking down information
            - Evaluate: Making judgments
            - Create: Producing new ideas
            
            Format each flashcard as JSON with 'question', 'answer', 'difficulty', and 'bloom_level' fields.
            Make questions clear, specific, and educational.
            """
            
            user_prompt = f"""
            Based on the following content, create {num_cards} educational flashcards.
            Vary the difficulty and cognitive levels according to Bloom's taxonomy.
            
            CONTENT:
            {content[:6000]}  # Limit content to prevent token overflow
            
            Return the flashcards as a JSON array.
            """
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            # Parse flashcards from response
            flashcards = self._parse_flashcards_response(response.choices[0].message.content)
            
            # Add metadata to each flashcard
            for i, card in enumerate(flashcards):
                card['id'] = i + 1
                card['created_at'] = datetime.now().isoformat()
                card['source_chunks'] = [chunk['id'] for chunk in selected_chunks]
            
            return flashcards
            
        except Exception as e:
            return [{
                'id': 1,
                'question': f"Error generating flashcards: {str(e)}",
                'answer': "Please try again or check your content.",
                'difficulty': "error",
                'bloom_level': "error",
                'created_at': datetime.now().isoformat(),
                'source_chunks': []
            }]
    
    def generate_quiz(self, chunks: List[Dict], num_questions: int = 5, 
                     difficulty: str = "mixed") -> Dict[str, Any]:
        """
        Generate a multiple-choice quiz from document chunks.
        
        Args:
            chunks: Document chunks to generate quiz from
            num_questions: Number of questions to generate
            difficulty: Quiz difficulty (easy, medium, hard, mixed)
            
        Returns:
            Dict with quiz questions and metadata
        """
        try:
            # Select diverse chunks for quiz generation
            selected_chunks = self._select_diverse_chunks(chunks, num_questions)
            
            # Prepare content for quiz generation
            content = "\n\n".join([chunk['text'] for chunk in selected_chunks])
            
            system_prompt = f"""
            You are an expert educator creating a multiple-choice quiz.
            Create {num_questions} questions with {difficulty} difficulty level.
            
            Each question should have:
            - A clear, specific question
            - 4 multiple choice options
            - One correct answer
            - A detailed explanation of why the answer is correct
            
            Format as JSON with 'question', 'options', 'correct_answer', 'explanation', and 'difficulty' fields.
            """
            
            user_prompt = f"""
            Based on the following content, create a {num_questions}-question multiple-choice quiz.
            
            CONTENT:
            {content[:6000]}  # Limit content to prevent token overflow
            
            Return the quiz as a JSON object with a 'questions' array.
            """
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse quiz from response
            quiz_data = self._parse_quiz_response(response.choices[0].message.content)
            
            # Add metadata
            quiz_data['metadata'] = {
                'created_at': datetime.now().isoformat(),
                'difficulty': difficulty,
                'num_questions': num_questions,
                'source_chunks': [chunk['id'] for chunk in selected_chunks]
            }
            
            return quiz_data
            
        except Exception as e:
            return {
                'questions': [{
                    'question': f"Error generating quiz: {str(e)}",
                    'options': ["A) Please try again", "B) Check your content", "C) Verify API keys", "D) Contact support"],
                    'correct_answer': "A",
                    'explanation': "There was an error generating the quiz. Please try again.",
                    'difficulty': "error"
                }],
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'difficulty': difficulty,
                    'num_questions': 1,
                    'source_chunks': []
                }
            }
    
    def explain_concept(self, concept: str, context_chunks: List[Dict], 
                       explanation_style: str = "simple") -> Dict[str, Any]:
        """
        Provide detailed explanation of a concept based on context.
        
        Args:
            concept: Concept to explain
            context_chunks: Relevant context chunks
            explanation_style: Style of explanation (simple, detailed, analogical)
            
        Returns:
            Dict with explanation and examples
        """
        try:
            context_text = self._prepare_context(context_chunks)
            
            style_prompts = {
                "simple": "Explain this concept in simple, easy-to-understand terms.",
                "detailed": "Provide a comprehensive, detailed explanation with technical depth.",
                "analogical": "Use analogies and real-world examples to explain this concept."
            }
            
            system_prompt = f"""
            You are an expert educator and explainer. {style_prompts.get(explanation_style, style_prompts['simple'])}
            Use the provided context to give accurate, well-structured explanations.
            Include examples when helpful and cite sources when referencing specific information.
            """
            
            user_prompt = f"""
            Based on the following context, please explain the concept: "{concept}"
            
            CONTEXT:
            {context_text}
            
            Provide a clear explanation that helps deepen understanding of this concept.
            """
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            explanation = response.choices[0].message.content
            
            return {
                'concept': concept,
                'explanation': explanation,
                'style': explanation_style,
                'sources': self._extract_sources_from_chunks(context_chunks),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'concept': concept,
                'explanation': f"Error generating explanation: {str(e)}",
                'style': explanation_style,
                'sources': [],
                'timestamp': datetime.now().isoformat()
            }
    
    # Helper methods
    
    def _prepare_context(self, chunks: List[Dict]) -> str:
        """Prepare context text from chunks with source information."""
        context_parts = []
        for chunk in chunks:
            source_info = ""
            if 'source_info' in chunk and chunk['source_info']:
                if 'page' in chunk['source_info']:
                    source_info = f"[source: page {chunk['source_info']['page']}]"
                elif 'timestamp' in chunk['source_info']:
                    source_info = f"[timestamp: {chunk['source_info']['timestamp']}]"
            
            context_parts.append(f"{source_info}\n{chunk['text']}")
        
        return "\n\n".join(context_parts)
    
    def _get_rag_system_prompt(self) -> str:
        """Get system prompt for RAG-based question answering."""
        return """
        You are Kensho, a mindful AI learning assistant. Your purpose is to help users gain deep understanding, not just surface-level answers.
        
        When answering questions:
        - Provide accurate, well-reasoned responses based on the given context
        - Include specific citations when referencing information
        - If the context is insufficient, clearly state what information is missing
        - Encourage deeper thinking by suggesting related questions or concepts to explore
        - Maintain a tone that is wise, encouraging, and focused on genuine learning
        
        Remember: You are a mirror for insight, not just an information retrieval system.
        """
    
    def _get_summary_system_prompt(self, summary_type: str) -> str:
        """Get system prompt for different summary types."""
        prompts = {
            "comprehensive": "Create a comprehensive summary that captures all key points and important details.",
            "key_points": "Extract and summarize only the most important key points and main ideas.",
            "executive": "Create an executive summary focused on actionable insights and key takeaways."
        }
        
        base_prompt = """
        You are Kensho, a mindful AI learning assistant. Create summaries that promote deep understanding.
        Focus on insights, connections between ideas, and the broader significance of the content.
        """
        
        return base_prompt + "\n" + prompts.get(summary_type, prompts["comprehensive"])
    
    def _extract_sources_from_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Extract source information from chunks."""
        sources = []
        for chunk in chunks:
            source = {
                'chunk_id': chunk.get('id', 0),
                'type': chunk.get('type', 'unknown'),
                'source': chunk.get('source', 'unknown')
            }
            
            if 'source_info' in chunk and chunk['source_info']:
                source.update(chunk['source_info'])
            
            sources.append(source)
        
        return sources
    
    def _extract_citations_from_answer(self, answer: str) -> List[str]:
        """Extract citations from the answer text."""
        citations = []
        
        # Look for page citations
        page_citations = re.findall(r'\[source: page (\d+)\]', answer)
        citations.extend([f"page {page}" for page in page_citations])
        
        # Look for timestamp citations
        time_citations = re.findall(r'\[timestamp: (\d{2}:\d{2})\]', answer)
        citations.extend([f"timestamp {time}" for time in time_citations])
        
        return list(set(citations))  # Remove duplicates
    
    def _calculate_confidence(self, chunks: List[Dict], question: str) -> float:
        """Calculate confidence score based on context relevance."""
        if not chunks:
            return 0.0
        
        # Simple confidence calculation based on similarity scores
        similarity_scores = [chunk.get('similarity_score', 0.0) for chunk in chunks]
        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
        
        # Normalize to 0-1 range (assuming similarity scores are already normalized)
        confidence = min(max(avg_similarity, 0.0), 1.0)
        
        return round(confidence, 2)
    
    def _select_diverse_chunks(self, chunks: List[Dict], num_items: int) -> List[Dict]:
        """Select diverse chunks for content generation."""
        if len(chunks) <= num_items:
            return chunks
        
        # Simple selection: take chunks with highest similarity scores
        # and distribute them across the document
        sorted_chunks = sorted(chunks, key=lambda x: x.get('similarity_score', 0.0), reverse=True)
        
        # Take top chunks but try to distribute across different parts
        selected = []
        chunk_indices = [chunk.get('chunk_index', 0) for chunk in sorted_chunks]
        
        for chunk in sorted_chunks:
            if len(selected) < num_items:
                selected.append(chunk)
        
        return selected[:num_items]
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from text using simple keyword extraction."""
        # Simple topic extraction - in a real implementation, you might use NLP libraries
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Filter and count
        topic_counts = {}
        for word in words:
            if len(word) > 3:  # Filter short words
                topic_counts[word] = topic_counts.get(word, 0) + 1
        
        # Return top topics
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:10]]
    
    def _parse_flashcards_response(self, response_text: str) -> List[Dict]:
        """Parse flashcards from AI response."""
        try:
            # Try to parse as JSON
            if response_text.strip().startswith('['):
                return json.loads(response_text)
            
            # Look for JSON array in the response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Fallback: create a single error card
            return [{
                'question': "Error parsing flashcards",
                'answer': "Please try generating flashcards again.",
                'difficulty': "error",
                'bloom_level': "error"
            }]
            
        except Exception:
            return [{
                'question': "Error parsing flashcards",
                'answer': "Please try generating flashcards again.",
                'difficulty': "error",
                'bloom_level': "error"
            }]
    
    def _parse_quiz_response(self, response_text: str) -> Dict:
        """Parse quiz from AI response."""
        try:
            # Try to parse as JSON
            if response_text.strip().startswith('{'):
                return json.loads(response_text)
            
            # Look for JSON object in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Fallback: create error quiz
            return {
                'questions': [{
                    'question': "Error parsing quiz",
                    'options': ["A) Try again", "B) Check content", "C) Verify setup", "D) Contact support"],
                    'correct_answer': "A",
                    'explanation': "There was an error parsing the quiz. Please try again.",
                    'difficulty': "error"
                }]
            }
            
        except Exception:
            return {
                'questions': [{
                    'question': "Error parsing quiz",
                    'options': ["A) Try again", "B) Check content", "C) Verify setup", "D) Contact support"],
                    'correct_answer': "A",
                    'explanation': "There was an error parsing the quiz. Please try again.",
                    'difficulty': "error"
                }]
            } 