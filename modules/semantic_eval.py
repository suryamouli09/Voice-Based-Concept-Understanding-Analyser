import streamlit as st
from sentence_transformers import SentenceTransformer, util

@st.cache_resource(show_spinner="Loading Sentence-BERT Semantic Encoder...")
def _load_sentence_model():
    """Load and cache SentenceTransformer model."""
    return SentenceTransformer("all-MiniLM-L6-v2")

def semantic_similarity(user_text: str, reference_text: str) -> dict:
    """
    Computes cosine similarity between user's spoken explanation and benchmark text.
    """
    if not user_text.strip():
        return {
            "Similarity": 0.0,
            "Level": "Insufficient Explanation"
        }

    model = _load_sentence_model()

    emb1 = model.encode(user_text, convert_to_tensor=True)
    emb2 = model.encode(reference_text, convert_to_tensor=True)

    raw_score = util.cos_sim(emb1, emb2).item()
    similarity = max(0.0, min(100.0, round(float(raw_score) * 100, 2)))

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