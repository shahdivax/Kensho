
import os
from typing import List, Dict
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from kensho.vector_store import KenshoVectorStore
from kensho.ai_assistant import KenshoAIAssistant
import json

# Initialize components that the tools will use
vector_store = KenshoVectorStore()
web_search_tool = DuckDuckGoSearchRun()

# Initialize AI assistant
ai_assistant = KenshoAIAssistant()

@tool
def retrieve_session_docs(query: str, session_id: str) -> str:
    """
    Searches the content of the documents uploaded in the current session
    to find answers to the user's question.
    Use this to answer questions about the specific material the user provided.
    """
    print(f"🛠️  EXECUTING: retrieve_session_docs(query='{query}', session_id='{session_id}')")
    # All vector data lives under sessions/<id>/ (index, metadata). No *_vectors suffix needed to query.
    session_dir = os.path.join("sessions", session_id)
    if not os.path.isdir(session_dir):
        return "This session has no stored documents yet. Upload a PDF / text / YouTube transcript first."

    try:
        # 1️⃣  Semantic search via FAISS embeddings
        # Prefer the session_id param so KenshoVectorStore resolves paths internally.
        context_chunks = vector_store.search(query, session_id=session_id, top_k=5)
        # print(f"🔍 Semantic search results: {context_chunks}")
        # 2️⃣  Keyword fallback – if semantic search finds nothing, scan all chunks for substrings
        if not context_chunks:
            all_chunks = vector_store.get_all_chunks(os.path.join(session_dir, "vector_index.faiss"))
            lowered_query = query.lower()
            keyword_hits = [c for c in all_chunks if lowered_query in c['text'].lower()]
            # Sort hits by length proximity (shorter chunks first) to surface concise matches
            keyword_hits = sorted(keyword_hits, key=lambda c: len(c['text']))[:5]
            context_chunks = keyword_hits
        # print(f"🔍 Keyword search results: {context_chunks}")
        if not context_chunks:
            # Final fallback: maybe FAISS index hasn't been built yet. Try loading raw chunks file.
            session_id = os.path.basename(session_dir).replace('_vectors', '')
            chunks_path = os.path.join('sessions', session_id, 'chunk_metadata.json')
            if os.path.exists(chunks_path):
                try:
                    with open(chunks_path, 'r') as f:
                        raw_chunks = json.load(f)
                    lowered_query = query.lower()
                    raw_hits = [c for c in raw_chunks if lowered_query in c.get('text', '').lower()]
                    raw_hits = sorted(raw_hits, key=lambda c: len(c.get('text', '')))[:5]
                    context_chunks = raw_hits
                except Exception as e:
                    print(f"❌ Error loading raw chunks fallback: {e}")

        if not context_chunks:
            return "No relevant information found in the documents for this query."

        # Prepare context for the response
        context_text = "\n\n".join([chunk['text'] for chunk in context_chunks])
        return context_text
    except Exception as e:
        print(f"❌ Error in retrieve_session_docs: {e}")
        return f"An error occurred while searching the documents: {str(e)}"

@tool
def web_search(query: str) -> str:
    """
    Performs a web search to find up-to-date information or answers to
    general knowledge questions when the user's documents are not sufficient.
    """
    print(f"🛠️  EXECUTING: web_search(query='{query}')")
    try:
        return web_search_tool.run(query)
    except Exception as e:
        print(f"❌ Error in web_search: {e}")
        return f"An error occurred during the web search: {str(e)}"

@tool
def explain_concept(concept: str, session_id: str) -> str:
    """
    Provides an in-depth, tutorial-style explanation of a concept.
    It first looks for relevant context in the user’s uploaded documents and then
    blends that with broader knowledge so the learner gets a clear,
    well-structured answer.
    """
    print(f"🛠️  EXECUTING: explain_concept(concept='{concept}', session_id='{session_id}')")
    try:
        # Retrieve relevant chunks for context (up to 5)
        context_chunks = vector_store.search(concept, session_id=session_id, top_k=5)

        result = ai_assistant.explain_concept(concept, context_chunks or [], explanation_style="simple")
        return result.get('explanation', 'No explanation generated.')
    except Exception as e:
        print(f"❌ Error in explain_concept: {e}")
        return f"An error occurred while explaining the concept: {str(e)}"


@tool
def summarize_session(summary_type: str, session_id: str) -> str:
    """
    Generates a summary of the entire set of documents in the current session.
    summary_type can be 'comprehensive', 'key_points', or 'executive'.
    """
    print(f"🛠️  EXECUTING: summarize_session(summary_type='{summary_type}', session_id='{session_id}')")
    try:
        # Load all chunks for the session
        session_dir = f"sessions/{session_id}"
        vector_store_path = f"{session_dir}_vectors"
        if not os.path.exists(vector_store_path):
            return "Vector store for this session not found. The user has likely not uploaded any documents yet."

        chunks = vector_store.get_all_chunks(vector_store_path)
        if not chunks:
            return "No document content available to summarize."

        full_text = "\n\n".join([c['text'] for c in chunks])
        summary_result = ai_assistant.generate_summary(full_text, summary_type=summary_type, max_length=500)
        return summary_result.get('summary', 'No summary generated.')
    except Exception as e:
        print(f"❌ Error in summarize_session: {e}")
        return f"An error occurred while generating the summary: {str(e)}"


# Update the master tool registry
all_tools = [
    retrieve_session_docs,
    web_search,
    explain_concept,
    summarize_session,
] 