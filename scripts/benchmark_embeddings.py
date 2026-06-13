import time
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

# Technical concepts for benchmarking
TECHNICAL_DATA = [
    {
        "content": "The FTS5 virtual table in SQLite provides full-text search capabilities using an inverted index. It requires a trigger to keep the virtual table in sync with the source content table.",
        "summary": "SQLite FTS5 Full-Text Search and Triggers"
    },
    {
        "content": "Matryoshka Embeddings allow for variable-dimension vector representations where the most important information is stored in the first few dimensions, enabling efficient scaling.",
        "summary": "Matryoshka Embeddings Architecture"
    },
    {
        "content": "The 'stella_en_400M_v5' model uses a BERT-like architecture with 400 million parameters, optimized for high-retrieval accuracy in RAG systems.",
        "summary": "Stella 400M Model Specifications"
    },
    {
        "content": "In LangGraph, a StateGraph represents an agentic loop where nodes are functions and edges define the control flow based on the state's messages.",
        "summary": "LangGraph StateGraph and Agentic Loops"
    },
    {
        "content": "SQLAlchemy's sessionmaker provides a factory for Session objects, ensuring that database transactions are handled atomically and connections are pooled.",
        "summary": "SQLAlchemy Session Management"
    }
]

QUERIES = [
    "How to sync full-text search in SQLite?",
    "Agentic loops with state management",
    "High precision retrieval for RAG",
    "Variable dimension vector representations",
    "Database connection pooling and sessions"
]

def run_benchmark(model_name, label, model_kwargs=None):
    print(f"\n--- Benchmarking: {label} ({model_name}) ---")
    start_load = time.time()
    try:
        if "stella" in model_name.lower():
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(
                model_name, 
                trust_remote_code=True,
                device="cpu"
            )
            encode_fn = model.encode
        else:
            model = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs or {}
            )
            encode_fn = model.embed_query
        
        # Force load
        encode_fn("test")
    except Exception as e:
        print(f"Error loading {model_name}: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    end_load = time.time()
    print(f"Load Time: {end_load - start_load:.2f}s")

    # Measure indexing time
    start_idx = time.time()
    embeddings = [encode_fn(item["summary"]) for item in TECHNICAL_DATA]
    end_idx = time.time()
    avg_idx = (end_idx - start_idx) / len(TECHNICAL_DATA)
    print(f"Avg Indexing Time (per item): {avg_idx*1000:.2f}ms")

    # Measure retrieval quality (simulated)
    total_score = 0
    for i, query in enumerate(QUERIES):
        query_vec = encode_fn(query)
        # Calculate cosine similarity with the correct target
        target_vec = embeddings[i]
        similarity = np.dot(query_vec, target_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(target_vec))
        total_score += similarity
        print(f"Query: '{query}' -> Similarity: {similarity:.4f}")

    avg_score = total_score / len(QUERIES)
    print(f"Average Quality Score: {avg_score:.4f}")
    
    return {
        "load_time": end_load - start_load,
        "avg_idx": avg_idx,
        "avg_score": avg_score,
        "dims": len(embeddings[0])
    }

if __name__ == "__main__":
    results_minilm = run_benchmark("all-MiniLM-L6-v2", "MiniLM (Current)")
    
    # BGE Small is a very strong and stable alternative
    results_bge = run_benchmark("BAAI/bge-small-en-v1.5", "BGE Small (Alternative)")
    
    # Try Stella one last time with a fallback attempt if I can find a way, 
    # but for now let's focus on BGE vs MiniLM
    
    if results_minilm and results_bge:
        print("\n=== FINAL COMPARISON (MiniLM vs BGE) ===")
        print(f"MiniLM Dimensions: {results_minilm['dims']}")
        print(f"BGE Dimensions: {results_bge['dims']}")
        
        quality_gain = (results_bge['avg_score'] / results_minilm['avg_score'] - 1) * 100
        latency_penalty = (results_bge['avg_idx'] / results_minilm['avg_idx'] - 1) * 100
        
        print(f"Quality Gain: {quality_gain:+.2f}%")
        print(f"Latency Penalty: {latency_penalty:+.2f}%")
        
        if quality_gain > 5:
             print("\nRecommendation: PROCEED with BGE migration. Stable and high-quality.")
        else:
             print("\nRecommendation: DISCARD. No significant gain.")
