import os
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, List, TypedDict

import chromadb
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langgraph.graph import END, START, StateGraph


DEFAULT_MASTER_KNOWLEDGE_PATH = "data/master_knowledge.md"
DEFAULT_CHROMA_PATH = "data/chroma"
DEFAULT_COLLECTION = "summaries"
DEFAULT_RELEVANCE_THRESHOLD = 0.18
DEFAULT_SUMMARY_MODEL = "gemini-2.5-flash"
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"


class SummaryState(TypedDict, total=False):
    transcript: str
    summary: str
    relevance: str
    score: float
    redirect: str


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _get_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY (or GOOGLE_API_KEY) is required.")
    return api_key


def embed_texts(texts: List[str], model: str = DEFAULT_EMBEDDING_MODEL) -> List[List[float]]:
    embeddings = GoogleGenerativeAIEmbeddings(model=model, google_api_key=_get_api_key())
    return embeddings.embed_documents(texts)


def generate_summary(transcript: str, model: str = DEFAULT_SUMMARY_MODEL) -> str:
    llm = ChatGoogleGenerativeAI(model=model, google_api_key=_get_api_key(), temperature=0.2, max_output_tokens=160)
    prompt = (
        "Summarize the transcript in 3 concise bullet points. "
        "Keep it short and factual."
    )
    response = llm.invoke(f"{prompt}\n\nTranscript:\n{transcript}")
    return (response.content or "").strip()


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if
 len(a) != len(b):
        raise ValueError("Embedding dimensions must match.")
    return sum(x * y for x, y in zip(a, b))


def relevance_check(summary: str, master_knowledge_text: str, model: str) -> float:
    summary_emb, mk_emb = embed_texts([summary, master_knowledge_text], model=model)
    return cosine_similarity(summary_emb, mk_emb)


def _get_collection(chroma_path: str, collection_name: str):
    client = chromadb.PersistentClient(path=chroma_path)
    return client.get_or_create_collection(name=collection_name)


def _seed_collection_if_empty(collection, master_knowledge_text: str, model: str) -> None:
    if collection.count() > 0:
        return
    mk_embedding = embed_texts([master_knowledge_text], model=model)[0]
    collection.add(
        ids=["master_knowledge_seed"],
        documents=[master_knowledge_text],
        embeddings=[mk_embedding],
        metadatas=[{"source": "master_knowledge", "type": "seed"}],
    )


def _summarize_node(
    master_knowledge_path: str,
    chroma_path: str,
    collection_name: str,
    relevance_threshold: float,
    embedding_model: str,
    summary_model: str,
):
    def _node(state: SummaryState) -> SummaryState:
        if not os.path.exists(master_knowledge_path):
            raise FileNotFoundError(
                f"Master knowledge not found: {master_knowledge_path}"
            )

        transcript = state.get("transcript", "")
        master_knowledge_text = _read_file(master_knowledge_path)
        summary = generate_summary(transcript, model=summary_model)
        score = relevance_check(summary, master_knowledge_text, model=embedding_model)

        relevance = "relevant" if score >= relevance_threshold else "off_track"
        redirect = ""
        if relevance == "off_track":
            redirect = (
                "This seems off-track. Please align discussion with the master knowledge goals."
            )

        if relevance == "relevant":
            collection = _get_collection(chroma_path, collection_name)
            _seed_collection_if_empty(
                collection, master_knowledge_text, model=embedding_model
            )
            summary_embedding = embed_texts([summary], model=embedding_model)[0]
            collection.add(
                ids=[str(uuid.uuid4())],
                documents=[summary],
                embeddings=[summary_embedding],
                metadatas=[
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "source": "summarizer_agent",
                        "type": "summary",
                    }
                ],
            )

        return {
            "summary": summary,
            "relevance": relevance,
            "score": score,
            "redirect": redirect,
        }

    return _node


def build_graph(
    master_knowledge_path: str = DEFAULT_MASTER_KNOWLEDGE_PATH,
    chroma_path: str = DEFAULT_CHROMA_PATH,
    collection_name: str = DEFAULT_COLLECTION,
    relevance_threshold: float = DEFAULT_RELEVANCE_THRESHOLD,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    summary_model: str = DEFAULT_SUMMARY_MODEL,
):
    graph = StateGraph(SummaryState)
    graph.add_node(
        "summarize",
        _summarize_node(
            master_knowledge_path=master_knowledge_path,
            chroma_path=chroma_path,
            collection_name=collection_name,
            relevance_threshold=relevance_threshold,
            embedding_model=embedding_model,
            summary_model=summary_model,
        ),
    )
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()


def handle(
    transcript: str,
    master_knowledge_path: str = DEFAULT_MASTER_KNOWLEDGE_PATH,
    chroma_path: str = DEFAULT_CHROMA_PATH,
    collection_name: str = DEFAULT_COLLECTION,
    relevance_threshold: float = DEFAULT_RELEVANCE_THRESHOLD,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    summary_model: str = DEFAULT_SUMMARY_MODEL,
) -> Dict[str, str]:
    app = build_graph(
        master_knowledge_path=master_knowledge_path,
        chroma_path=chroma_path,
        collection_name=collection_name,
        relevance_threshold=relevance_threshold,
        embedding_model=embedding_model,
        summary_model=summary_model,
    )
    return app.invoke({"transcript": transcript})


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m agents.summarizer_agent \"<transcript text>\"")
        sys.exit(1)

    output = handle(sys.argv[1])
    print(json.dumps(output, indent=2))
