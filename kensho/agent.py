import os
from functools import partial
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
# Checkpointer: we'll keep everything in-memory for now (no external DB needed).
from langgraph.checkpoint.memory import InMemorySaver  # Lightweight, no-DB checkpointer
from langgraph.prebuilt import create_react_agent
from kensho.ai_assistant import KenshoAIAssistant
from kensho.tools import (
    retrieve_session_docs,
    web_search,
    explain_concept as explain_concept_tool_fn,
    summarize_session as summarize_session_tool_fn,
)

# --------------------------- Additional Tool Classes ---------------------------
class ConceptExplainSchema(BaseModel):
    concept: str = Field(description="The concept or term the user wants explained.")


class ConceptExplainTool(BaseTool):
    name: str = "explain_concept"
    description: str = (
        "Provides an in-depth explanation of a concept using both the uploaded "
        "documents and general knowledge."
    )
    args_schema: type[BaseModel] = ConceptExplainSchema
    session_id: str

    def _run(self, concept: str) -> str:
        return explain_concept_tool_fn.invoke({"concept": concept, "session_id": self.session_id})

    async def _arun(self, concept: str) -> str:
        return self._run(concept)


class SessionSummarySchema(BaseModel):
    summary_type: str = Field(
        default="key_points",
        description="Type of summary: 'comprehensive', 'key_points', or 'executive'.",
    )


class SessionSummaryTool(BaseTool):
    name: str = "summarize_session"
    description: str = (
        "Creates a summary of the user's uploaded documents in the chosen style."
    )
    args_schema: type[BaseModel] = SessionSummarySchema
    session_id: str

    def _run(self, summary_type: str = "key_points") -> str:
        return summarize_session_tool_fn.invoke({"summary_type": summary_type, "session_id": self.session_id})

    async def _arun(self, summary_type: str = "key_points") -> str:
        return self._run(summary_type)

# Initialize the base assistant to get the system prompt
base_assistant = KenshoAIAssistant()
system_prompt_text = base_assistant._get_rag_system_prompt()

# --- Agent-Specific LLM Initialization ---
# The agent requires a LangChain ChatModel that supports .bind_tools(),
# so we create a new instance here instead of using the one from KenshoAIAssistant,
# which might be a base client for other purposes.
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

if gemini_api_key:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_api_key, temperature=0)
elif openai_api_key:
    llm = ChatOpenAI(model="gpt-4o", api_key=openai_api_key, temperature=0)
else:
    raise ValueError("Could not find OPENAI_API_KEY or GEMINI_API_KEY in environment.")
# --- End LLM Initialization ---


# --- New Tool Definition ---
class SessionRetrieverSchema(BaseModel):
    query: str = Field(description="The search query to find relevant documents in the user's uploaded material.")

class SessionRetrieverTool(BaseTool):
    name: str = "retrieve_session_docs"
    description: str = (
        "Searches the content of the documents uploaded in the current session "
        "to find answers to the user's question. Use this to answer questions "
        "about the specific material the user provided."
    )
    args_schema: type[BaseModel] = SessionRetrieverSchema
    session_id: str

    def _run(self, query: str) -> str:
        """Use the tool."""
        # The original tool is already decorated, so we call its invoke method.
        return retrieve_session_docs.invoke({"query": query, "session_id": self.session_id})

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        # In a real production system, the underlying search should be async.
        # For now, we'll just wrap the synchronous version.
        return self._run(query)
# --- End New Tool Definition ---

# Define the tools, binding the session_id to the retriever
def get_tools_for_session(session_id: str):
    """Factory to create a list of tools with a specific session_id."""
    session_retriever = SessionRetrieverTool(session_id=session_id)
    concept_explainer = ConceptExplainTool(session_id=session_id)
    doc_summarizer = SessionSummaryTool(session_id=session_id)
    return [session_retriever, concept_explainer, doc_summarizer, web_search]

def build_prompt(system_message_text: str):
    """Factory to create a prompt-building function with a given system message.
    The extra guidance block nudges the LLM to actually CALL the tools when they are useful.
    """
    TOOL_GUIDANCE = (
        "\n\nTOOL INSTRUCTIONS:\n"
        "You have access to FOUR tools and should decide when to call them:\n"
        "1. retrieve_session_docs(query: str) – Quickly pull passages from the user's uploaded documents.\n"
        "2. explain_concept(concept: str) – Teach or clarify a concept in depth.\n"
        "3. summarize_session(summary_type: str='key_points') – Produce a concise summary of the overall material.\n"
        "4. web_search(query: str) – Look up fresh information on the public web.\n"
        "If you need extra information, think step-by-step, then CALL the appropriate tool with the minimal\n"
        "query needed. After receiving the tool\'s result (Observation), continue the reasoning loop until you\n"
        "can provide a final, well-cited answer."
    )

    def prompt_builder(state: dict, config: dict | None = None):
        """Builds the prompt messages, combining system prompt with chat history."""
        return [
            {
                "role": "system",
                "content": system_message_text + TOOL_GUIDANCE,
            },
            *state["messages"],
        ]

    return prompt_builder

# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------
def create_agent_executor(session_id: str):
    """
    Creates a new LangGraph agent executor for a given session.
    Each agent has its own set of tools bound to its specific session_id.
    """
    # Use a lightweight in-memory checkpointer. This avoids async context
    # issues with AsyncSqliteSaver and keeps per-session memory alive while
    # the server process is running. (Persistence across restarts can be
    # added later with Postgres/Redis/etc.)
    checkpointer = InMemorySaver()

    tools = get_tools_for_session(session_id)
    
    # Use the prebuilt create_react_agent
    # This creates a graph that can reason about which tool to call, and can keep state.
    # The checkpointer handles saving and loading the conversation history.

    # The new API requires a prompt builder function instead of a static system_message
    prompt_builder = build_prompt(system_prompt_text)

    agent_executor = create_react_agent(
        model=llm,
        tools=tools,
        prompt=prompt_builder,
        checkpointer=checkpointer,
    )
    
    return agent_executor

# We will maintain a dictionary of agent executors, one for each session
# In a production environment, you might not want to hold all these in memory
agent_executors: dict = {}

def get_agent_for_session(session_id: str):
    """
    Retrieves an existing agent executor for a session or creates a new one.
    """
    if session_id not in agent_executors:
        print(f"✨ Creating new agent for session: {session_id}")
        agent_executors[session_id] = create_agent_executor(session_id)
    
    return agent_executors[session_id] 