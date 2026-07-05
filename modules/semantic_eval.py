from sentence_transformers import SentenceTransformer, util

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_similarity(user_text, reference_text):

    emb1 = model.encode(user_text, convert_to_tensor=True)

    emb2 = model.encode(reference_text, convert_to_tensor=True)

    score = util.cos_sim(emb1, emb2).item()

    similarity = round(score * 100, 2)

    if similarity >= 80:
        level = "🟢 Strong Understanding"

    elif similarity >= 60:
        level = "🟡 Moderate Understanding"

    else:
        level = "🔴 Poor Understanding"

    return {
        "Similarity": similarity,
        "Level": level
    }