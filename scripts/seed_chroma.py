import os
import uuid
from datetime import datetime, timezone

import chromadb
from google import genai


MASTER_KNOWLEDGE_PATH = "data/master_knowledge.md"
CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "summaries"
EMBEDDING_MODEL = "gemini-embedding-001"


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_genai_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY (or GOOGLE_API_KEY) is required.")
    return genai.Client(api_key=api_key)


def _extract_embedding_values(result):
    items = []
    if hasattr(result, "embeddings") and result.embeddings:
        items = result.embeddings
    elif hasattr(result, "embedding") and result.embedding:
        items = [result.embedding]
    else:
        raise ValueError("No embeddings found in response.")

    vectors = []
    for item in items:
        if isinstance(item, dict) and "values" in item:
            vectors.append(item["values"])
        elif hasattr(item, "values"):
            vectors.append(item.values)
        else:
            vectors.append(item)
    return vectors


def embed_texts(texts):
    client = get_genai_client()
    result = client.models.embed_content(model=EMBEDDING_MODEL, contents=texts)
    return _extract_embedding_values(result)


def main():
    master_text = read_file(MASTER_KNOWLEDGE_PATH)
    seed_summary = (
        "We should implement the summarizer pipeline and store relevant summaries "
        "in the vector database to keep the team aligned with goals."
    )

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    if collection.count() > 0:
        print("Chroma collection already has data; skipping seed.")
        return

    mk_embedding, summary_embedding = embed_texts([master_text, seed_summary])

    collection.add(
        ids=["master_knowledge_seed", str(uuid.uuid4())],
        documents=[master_text, seed_summary],
        embeddings=[mk_embedding, summary_embedding],
        metadatas=[
            {"source": "master_knowledge", "type": "seed"},
            {
                "source": "seed",
                "type": "summary",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ],
    )
    print("Seeded Chroma collection with master knowledge and sample summary.")


if __name__ == "__main__":
    main()
