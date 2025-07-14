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
                       chat_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Answer a question using RAG with citation-aware responses, maintaining conversation history.

        Args:
            question: User's question
            context_chunks: Relevant chunks from vector search
            chat_history: Previous messages in the conversation for context

        Returns:
            Dict with answer, sources, and confidence
        """
        try:
            # Prepare context
            context_text = self._prepare_context(context_chunks)

            # Create system prompt
            system_prompt = self._get_rag_system_prompt()

            # Build conversation history for the model
            messages = []
            if chat_history:
                for entry in chat_history[-5:]: # Use last 5 turns
                    messages.append({"role": "user", "content": entry["user_message"]})
                    messages.append({"role": "assistant", "content": entry["ai_response"]})

            # Create user prompt
            user_prompt = f"""
            Here is the relevant context from the document(s):
            ---
            CONTEXT:
            {context_text}
            ---
            Based on the context and our conversation so far, please answer my question.

            QUESTION: {question}
            """
            messages.append({"role": "user", "content": user_prompt})

            # Generate response
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=0.5, # Slightly more creative for tutoring
                max_tokens=1500
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
                       explanation_style: str = "simple",
                       chat_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Explain a specific concept using document context and general knowledge.

        Args:
            concept: The concept to explain
            context_chunks: Relevant chunks from vector search for context
            explanation_style: The style of explanation (e.g., "simple", "detailed", "analogy")
            chat_history: Previous messages in the conversation for context

        Returns:
            A dictionary with the explanation.
        """
        try:
            context_text = self._prepare_context(context_chunks)

            system_prompt = self._get_rag_system_prompt() # Re-use the tutor persona

            # Build conversation history for the model
            messages = []
            if chat_history:
                for entry in chat_history[-5:]:
                    messages.append({"role": "user", "content": entry["user_message"]})
                    messages.append({"role": "assistant", "content": entry["ai_response"]})

            user_prompt = f"""
            Relevant document context:
            ---
            {context_text}
            ---
            I need to understand a concept better.

            CONCEPT: {concept}
            EXPLANATION STYLE: {explanation_style}

            Please explain this concept to me. Use the document context as a primary source, but also draw on your general knowledge to provide a comprehensive and easy-to-understand explanation. If the context is sparse, rely more on your general knowledge but mention that the document has limited information.
            """
            messages.append({"role": "user", "content": user_prompt})

            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=0.6,
                max_tokens=1200
            )

            explanation = response.choices[0].message.content

            return {
                'explanation': explanation,
                'style': explanation_style,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'explanation': f"Sorry, I encountered an error while trying to explain '{concept}': {str(e)}",
                'style': explanation_style,
                'timestamp': datetime.now().isoformat()
            }


    # Helper methods
    
    def _prepare_context(self, chunks: List[Dict]) -> str:
        """Prepare context string from chunks, including metadata."""
        if not chunks:
            return "No specific context from the document was found for this query."
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
        """Get the system prompt for the AI tutor."""
        return """
        You are 'Kensho', a friendly and knowledgeable AI Tutor. Your goal is to help users understand their documents and learn new concepts.

        Your personality:
        - Patient, encouraging, and adaptive.
        - You break down complex topics into simple, digestible pieces.
        - You ask clarifying questions to check for understanding and guide the user's learning.
        - You can be a bit informal and use emojis to make learning more engaging.

        How you'll answer:
        1.  **Use the Provided CONTEXT First**: Incorporate relevant excerpts from the documents the user uploaded to ground your answer, but you no longer need to insert explicit citation tags.
        2.  **Bring in General Knowledge When Needed**: If the CONTEXT is sparse or the question goes beyond it, add helpful background from your broader knowledge. Preface these parts with phrases like "From my general knowledge..." so the learner knows the origin.
        3.  **Stay Conversational**: Weave your replies into the ongoing chat, referencing earlier turns so the conversation feels continuous and natural.
        4.  **Guide, Don't Just Answer**: Coach the learner. Break complex ideas into steps, ask clarifying questions, and suggest next learning actions.
        5.  **Be Honest About Uncertainty**: If you're not sure, say so plainly and propose follow-up steps (e.g., "We could look this up with a web search tool").
        """
    
    def _get_summary_system_prompt(self, summary_type: str) -> str:
        """Get the system prompt for generating summaries."""
        if summary_type == "comprehensive":
            prompt = """
            You are a meticulous academic assistant. Your task is to create a comprehensive, detailed summary of the provided text.
            - Capture all main arguments, key evidence, and conclusions.
            - Preserve the original nuance and tone.
            - Organize the summary logically with clear paragraphs.
            - Mention any important figures, data, or examples.
            """
        elif summary_type == "key_points":
            prompt = """
            You are a productivity expert. Your task is to extract the most critical key points from the text and present them as a concise bulleted list.
            - Each bullet point should represent a single, core idea.
            - Start each point with a strong action verb if possible.
            - Focus on actionable insights, main findings, or critical definitions.
            """
        else:  # executive
            prompt = """
            You are a strategy consultant briefing a busy executive. Your task is to provide a short, high-level executive summary.
            - Start with a one-sentence summary of the main outcome or conclusion.
            - Briefly cover the core problem, methodology, and key findings.
            - Focus on the "so what?" – the implications and strategic importance.
            - Keep it concise and to the point.
            """
        return prompt
    
    def _extract_sources_from_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Extract unique sources from a list of chunks."""
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
        
        # Remove duplicates
        unique_sources = {}
        for source in sources:
            key = (source['type'], source['source'])
            if key not in unique_sources:
                unique_sources[key] = source
        
        return list(unique_sources.values())
    
    def _extract_citations_from_answer(self, answer: str) -> List[str]:
        """Extract [source: ...] citations from the AI's answer."""
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
        if not text:
            return []

        try:
            system_prompt = "You are an expert at identifying key themes. Extract the main topics from the text below. Return a JSON list of strings."
            user_prompt = f"TEXT: {text[:4000]}\n\nTOPICS:"

            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            # The response is expected to be a JSON object like {"topics": ["topic1", "topic2"]}
            data = json.loads(response.choices[0].message.content)
            return data.get("topics", [])
            
        except Exception:
            # Fallback for models that don't support JSON mode well or other errors
            # Simple regex as a fallback
            topics = re.findall(r'"(.*?)"', text)
            return list(set(topics))[:5] # Return up to 5 unique topics

    def _parse_flashcards_response(self, response_text: str) -> List[Dict]:
        """Parse the AI's response to extract flashcards, resiliently."""
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
        """Parse the AI's response to extract quiz questions, resiliently."""
        try:
            # The response should be a JSON object with a "questions" key
            # which is a list of question objects.
            quiz_data = json.loads(response_text)
            if isinstance(quiz_data, dict) and "questions" in quiz_data:
                return quiz_data
            else:
                # Handle cases where the JSON is just the list itself
                return {"questions": quiz_data}
        except json.JSONDecodeError:
            # Fallback for malformed JSON
            print("⚠️ Warning: Failed to decode JSON from quiz response. Using fallback.")
            return {"questions": [{"question": "Error parsing quiz data.", "options": [], "answer": ""}]} 