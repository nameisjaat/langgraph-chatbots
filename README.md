# Chatbot / RAG / LangGraph Experiments

Learning project built with LangChain, LangGraph and OpenAI (`gpt-4o-mini`).

## Contents

| File | What it is |
|------|------------|
| `chatbot.ipynb` | Basic LangGraph chatbot with conversation memory (`MemorySaver`) |
| `langgraph_backend.py`, `langgraph_database_backend.py` | Chatbot backend as scripts; the database version persists chats in SQLite (`chatbot.db`) |
| `rag.ipynb` | RAG over CMS / Medicare PDFs: loader, splitter, FAISS, retriever tool, tool-calling agent |
| `blog_generator.ipynb` | Multi-step blog writer: router, web research (Tavily), planner, parallel section workers, reducer that saves a `.md` file |
| `*.pdf` | Source documents for the RAG notebook |

## Setup

1. Create and activate a virtual environment (`python -m venv .venv`).
2. Install: `pip install ipykernel langchain langchain-openai langchain-community langchain-text-splitters langgraph faiss-cpu pypdf python-dotenv tavily-python`
3. Create a `.env` file in this folder:
   ```
   OPENAI_API_KEY=...
   TAVILY_API_KEY=...
   ```
4. In VS Code, select the `.venv` kernel for each notebook.

## What I learned

### Environment
- A notebook runs on whichever kernel is selected. `ModuleNotFoundError` usually means the kernel isn't the venv where the packages live.
- A Windows venv (`Scripts/`) can't be used from WSL (Linux). Pick one and stay with it.
- Restart the kernel after changing a class or function. Old definitions, and graphs compiled from them, stay loaded.
- Never commit `.env`. Keep it in `.gitignore`.

### LangChain
- In `langchain` 1.x, `langchain.text_splitter` is gone. Use `langchain_text_splitters`.
- `PyPDFLoader` takes one file. Loop over files and combine the documents. Metadata (`source`, `page_label`) enables citations.
- `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)` then `FAISS.from_documents(...)` then `.as_retriever(search_kwargs={'k': 4})`.
- Persist the FAISS index with `save_local` and `load_local`. Don't re-embed on every run.

### LangGraph
- Nodes read from and return updates to the state. A node that ignores `state['messages']` makes the LLM see nothing. (My `messages = ['messages']` bug.)
- `graph.compile()` needs the parentheses. Display with `chatbot.get_graph().draw_mermaid_png()`.
- A checkpointer (`MemorySaver`) needs `config={'configurable': {'thread_id': ...}}` on every call. The same ID continues a chat; a new ID starts a fresh one.
- `Send` fans work out to parallel workers. They finish in any order, so carry an ID with each result and sort in the reducer.
- RAG as a tool: `bind_tools` + `ToolNode` + `tools_condition` lets the model decide when to retrieve.

### Pydantic / structured output
- `from __future__ import annotations` turns annotations into strings and caused "`Plan` is not fully defined" in notebooks. Avoid it.
- Every type used in a model must be imported (`Literal` was missing).
- A misspelled `Field` argument (`desctiption`) is silently ignored.
- Prompts and schemas must agree on field names and limits. If a prompt mentions `blog_kind` but the model has no such field, the code later crashes with `AttributeError`.

### Files
- On Windows, a colon in a filename creates an NTFS alternate data stream. The file looks empty and the content is hidden. Slugify titles: `re.sub(r"[^a-z0-9]+", "_", title.lower())`.

### From prototype to production
Missing from these notebooks: evaluation set, hybrid search and reranking, section-aware chunking, grounding / citation prompts, tracing, error handling, and an API layer.
