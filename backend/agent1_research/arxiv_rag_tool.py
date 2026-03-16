import arxiv
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import uuid

# Lazily initialized globals so import errors do not explode the whole app.
_EMBEDDING_MODEL = None
_CLIENT = None
_COLLECTION = None


def _get_embedding_model():
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as exc:
            print(f"[WARN] Failed to load embedding model: {exc}")
            _EMBEDDING_MODEL = None
    return _EMBEDDING_MODEL


def _get_collection():
    global _CLIENT, _COLLECTION
    if _COLLECTION is None:
        try:
            _CLIENT = chromadb.PersistentClient(path="./vector_store")
            _COLLECTION = _CLIENT.get_or_create_collection(name="research_papers")
        except Exception as exc:
            print(f"[WARN] Failed to initialize ChromaDB: {exc}")
            _COLLECTION = None
    return _COLLECTION


def search_arxiv(topic, max_results=20):
    """Search ArXiv for a topic, returning a list of paper dicts.

    Any API errors are logged and result in an empty list so that the
    calling pipeline can still proceed (with fewer signals).
    """
    try:
        search = arxiv.Search(
            query=topic,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )
    except Exception as exc:
        print(f"[WARN] Failed to create ArXiv search: {exc}")
        return []

    papers = []

    try:
        for result in search.results():
            papers.append(
                {
                    "id": str(uuid.uuid4()),
                    "title": result.title,
                    "abstract": result.summary,
                    "pdf_url": getattr(result, "pdf_url", ""),
                }
            )
    except Exception as exc:
        print(f"[WARN] Error while iterating ArXiv results: {exc}")

    return papers


def build_chunks(papers):
    chunks = []

    for p in papers:
        text = f"""
Title: {p.get('title', '')}

Abstract:
{p.get('abstract', '')}
"""

        chunks.append(
            {
                "id": p.get("id", str(uuid.uuid4())),
                "text": text,
                "metadata": {
                    "title": p.get("title", ""),
                    "pdf": p.get("pdf_url", ""),
                },
            }
        )

    return chunks


def store_chunks(chunks):
    model = _get_embedding_model()
    collection = _get_collection()

    if model is None or collection is None:
        print("[WARN] Skipping vector indexing (missing model or collection).")
        return

    for c in tqdm(chunks):
        try:
            embedding = model.encode(c["text"]).tolist()
            collection.add(
                ids=[c["id"]],
                embeddings=[embedding],
                documents=[c["text"]],
                metadatas=[c["metadata"]],
            )
        except Exception as exc:
            print(f"[WARN] Failed to store chunk {c.get('id')}: {exc}")


def retrieve_research(query, top_k=5):
    model = _get_embedding_model()
    collection = _get_collection()

    if model is None or collection is None:
        print("[WARN] Vector search unavailable — returning empty research set.")
        return []

    try:
        query_embedding = model.encode(query).tolist()
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    except Exception as exc:
        print(f"[WARN] ChromaDB query failed: {exc}")
        return []

    retrieved = []

    for doc, meta in zip(results.get("documents", [[]])[0], results.get("metadatas", [[]])[0]):
        retrieved.append(
            {
                "paper_title": meta.get("title", ""),
                "content": doc,
                "pdf": meta.get("pdf", ""),
            }
        )

    return retrieved


def arxiv_research_tool(query):
    """
    High-level helper used by the research agent.

    On any failure in the ArXiv/vector pipeline, this function will degrade
    gracefully and return an empty list rather than raising, so that the
    rest of the backend can continue to run.
    """
    papers = search_arxiv(query)
    if not papers:
        return []

    chunks = build_chunks(papers)
    if not chunks:
        return []

    store_chunks(chunks)

    return retrieve_research(query)