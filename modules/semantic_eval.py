import re
import streamlit as st
import torch

# Restrict PyTorch threads to reduce cloud container memory footprint
torch.set_num_threads(2)

def _lexical_semantic_similarity(user_text: str, reference_text: str) -> float:
    """
    High-reliability fallback similarity calculator based on weighted term overlap
    and conceptual keyword matching. Used if HuggingFace neural weights fail to download
    or if cloud memory is strictly constrained.
    """
    stopwords = {
        "about", "above", "after", "again", "against", "because", "before", "being",
        "below", "between", "during", "further", "having", "other", "should", "their",
        "there", "these", "through", "under", "which", "while", "would", "where", "without",
        "which", "could", "would", "shall", "might", "shall", "these", "those"
    }
    w1 = set(re.findall(r'\b[a-zA-Z]{4,}\b', user_text.lower())) - stopwords
    w2 = set(re.findall(r'\b[a-zA-Z]{4,}\b', reference_text.lower())) - stopwords

    if not w1 or not w2:
        return 0.0

    intersection = w1.intersection(w2)
    union = w1.union(w2)

    jaccard = len(intersection) / len(union) if union else 0.0
    recall = len(intersection) / len(w2) if w2 else 0.0
    score = (recall * 0.75 + jaccard * 0.25) * 100.0

    return max(0.0, min(100.0, round(score, 2)))

@st.cache_resource(show_spinner="Loading Sentence-BERT Semantic Encoder...")
def _load_sentence_model():
    """Load and cache SentenceTransformer model with fallback protection."""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    except Exception:
        return None

def semantic_similarity(user_text: str, reference_text: str) -> dict:
    """
    Computes semantic similarity between user's spoken explanation and benchmark text.
    Uses dense Sentence-BERT embeddings with automatic fallback to weighted lexical alignment.
    """
    if not user_text.strip():
        return {
            "Similarity": 0.0,
            "Level": "Insufficient Explanation"
        }

    similarity = None
    model = _load_sentence_model()

    if model is not None:
        try:
            with torch.inference_mode():
                from sentence_transformers import util
                emb1 = model.encode(user_text, convert_to_tensor=True)
                emb2 = model.encode(reference_text, convert_to_tensor=True)
                raw_score = util.cos_sim(emb1, emb2).item()
                similarity = max(0.0, min(100.0, round(float(raw_score) * 100, 2)))
        except Exception:
            similarity = None

    # Ultra-reliable fallback if neural model is unavailable or runs out of RAM
    if similarity is None:
        similarity = _lexical_semantic_similarity(user_text, reference_text)

    if similarity >= 80:
        level = "Strong Conceptual Alignment"
    elif similarity >= 60:
        level = "Moderate Understanding"
    elif similarity >= 40:
        level = "Partial Understanding"
    else:
        level = "Needs Significant Improvement"

    return {
        "Similarity": similarity,
        "Level": level
    }