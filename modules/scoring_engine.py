def calculate_final_score(audio_features: dict, filler_result: dict, semantic_result: dict) -> dict:
    """
    Synthesizes multi-modal metrics into a cohesive conceptual understanding score:
    - Semantic Alignment (60% weight): Core concept correctness and depth
    - Fluency & Pace (25% weight): Optimal rate (115-165 WPM) & healthy pauses
    - Articulation Clarity (15% weight): Absence of distracting filler words
    """
    # 1. Semantic Match
    semantic_score = float(semantic_result.get("Similarity", 0.0))

    # 2. Speaking Fluency
    speech_rate = float(audio_features.get("Speech Rate", 0.0))
    pause_ratio = float(audio_features.get("Pause Ratio", 0.0))

    fluency_score = 100.0

    # Ideal speaking pace for technical explanations: 115 - 165 WPM
    if speech_rate < 115:
        fluency_score -= (115 - speech_rate) * 0.35
    elif speech_rate > 165:
        fluency_score -= (speech_rate - 165) * 0.35

    # Penalize excessive pauses (e.g. silence > 25% of total audio)
    if pause_ratio > 0.25:
        fluency_score -= (pause_ratio - 0.25) * 60.0

    fluency_score = max(0.0, min(100.0, fluency_score))

    # 3. Communication Clarity
    filler_ratio = float(filler_result.get("Filler Ratio", 0.0))
    # Deduct 6 points per 1% filler ratio
    communication_score = max(0.0, min(100.0, 100.0 - (filler_ratio * 6.0)))

    # Weighted Overall Score
    final_score = (
        semantic_score * 0.60 +
        fluency_score * 0.25 +
        communication_score * 0.15
    )
    final_score = round(max(0.0, min(100.0, final_score)), 1)

    # Performance Tier (Clean ASCII strings to prevent Windows cp1252 charmap encoding errors)
    if final_score >= 85:
        tier = "Advanced Mastery"
    elif final_score >= 70:
        tier = "Competent Understanding"
    elif final_score >= 50:
        tier = "Developing Understanding"
    else:
        tier = "Needs Foundational Focus"

    return {
        "Semantic Score": round(semantic_score, 1),
        "Fluency Score": round(fluency_score, 1),
        "Communication Score": round(communication_score, 1),
        "Final Score": final_score,
        "Grade": tier,
        "Tier": tier
    }