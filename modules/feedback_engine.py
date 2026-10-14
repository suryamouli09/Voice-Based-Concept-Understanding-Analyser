import re

def generate_feedback(score_result: dict, filler_result: dict, audio_features: dict, transcript: str = "", reference_text: str = "") -> dict:
    """
    Generates intelligent diagnostic feedback, strengths, recommendations,
    and missing key conceptual terms.
    """
    strengths = []
    suggestions = []
    
    semantic_score = score_result.get("Semantic Score", 0.0)
    fluency_score = score_result.get("Fluency Score", 0.0)
    speech_rate = audio_features.get("Speech Rate", 0.0)
    pause_ratio = audio_features.get("Pause Ratio", 0.0)
    filler_count = filler_result.get("Filler Count", 0)
    filler_ratio = filler_result.get("Filler Ratio", 0.0)
    detected_fillers = filler_result.get("Detected Fillers", {})

    # 1. Conceptual Feedback
    if semantic_score >= 85:
        strengths.append("Exceptional semantic precision: Your explanation closely mirrored core theoretical principles.")
    elif semantic_score >= 70:
        strengths.append("Solid conceptual grasp: Core definition elements were effectively addressed.")
    elif semantic_score >= 50:
        suggestions.append("Deepen conceptual coverage: Incorporate formal terminology and underlying mechanics rather than high-level analogies.")
    else:
        suggestions.append("Review foundational concepts: Key definitions and characteristics were omitted.")

    # 2. Key Terms Extraction & Gap Analysis
    matched_keywords = []
    missed_keywords = []
    if reference_text:
        # Extract important words (>4 characters, non-stopwords)
        stopwords = {"about", "above", "after", "again", "against", "because", "before", "being", "below", "between", "during", "further", "having", "other", "should", "their", "there", "these", "through", "under", "which", "while", "would", "where", "without"}
        ref_words = set(re.findall(r"\b[a-zA-Z]{5,}\b", reference_text.lower())) - stopwords
        user_words = set(re.findall(r"\b[a-zA-Z]{5,}\b", transcript.lower()))

        matched_keywords = sorted(list(ref_words.intersection(user_words)))
        missed_keywords = sorted(list(ref_words - user_words))[:6]

    # 3. Speech Rate & Pace Feedback
    if 115 <= speech_rate <= 165:
        strengths.append(f"Balanced speaking cadence ({speech_rate:.0f} WPM): Ideal for technical comprehension.")
    elif speech_rate < 115 and speech_rate > 0:
        suggestions.append(f"Increase articulation tempo: Current pace ({speech_rate:.0f} WPM) is slower than the optimal 120-160 WPM range.")
    elif speech_rate > 165:
        suggestions.append(f"Pace regulation needed: Your rate ({speech_rate:.0f} WPM) may cause listeners to miss nuanced technical points.")

    # 4. Hesitations & Pauses
    if pause_ratio > 0.35:
        suggestions.append(f"Reduce prolonged silences: {pause_ratio*100:.0f}% of your audio duration was silent or paused.")
    elif pause_ratio < 0.10 and len(transcript.split()) > 10:
        suggestions.append("Incorporate deliberate pauses between key points to give listeners time to digest concepts.")
    else:
        strengths.append("Natural breathing pauses and sentence structure transitions.")

    # 5. Filler Words Feedback
    if filler_count == 0:
        strengths.append("Outstanding verbal polish: Zero common filler words or verbal crutches detected.")
    elif filler_ratio <= 3.0:
        strengths.append(f"Minimal filler word usage ({filler_ratio:.1f}%): Maintained high professional clarity.")
    else:
        top_fillers = [f"'{w}' ({c}x)" for w, c in detected_fillers.items()][:3]
        suggestions.append(f"Filter verbal crutches: Frequent use of {', '.join(top_fillers)}. Try taking a silent breath instead.")

    # Fallback guarantees
    if not strengths:
        strengths.append("Clear audio delivery with audible acoustic signal.")
    if not suggestions:
        suggestions.append("Continue practicing with diverse concept domains to build versatility.")

    return {
        "strengths": strengths,
        "suggestions": suggestions,
        "matched_keywords": matched_keywords,
        "missed_keywords": missed_keywords
    }