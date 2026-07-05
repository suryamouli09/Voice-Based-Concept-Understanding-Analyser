def calculate_final_score(audio_features, filler_result, semantic_result):

    # ----------------------------
    # Semantic Score (0–100)
    # ----------------------------
    semantic_score = semantic_result["Similarity"]

    # ----------------------------
    # Speech Fluency Score
    # ----------------------------
    speech_rate = audio_features["Speech Rate"]
    pause_ratio = audio_features["Pause Ratio"]

    fluency_score = 100

    # Ideal speech rate: 110–170 WPM
    if speech_rate < 110:
        fluency_score -= (110 - speech_rate) * 0.3

    elif speech_rate > 170:
        fluency_score -= (speech_rate - 170) * 0.3

    # Penalize excessive pauses
    fluency_score -= pause_ratio * 50

    fluency_score = max(0, min(100, fluency_score))

    # ----------------------------
    # Communication Score
    # ----------------------------
    filler_ratio = filler_result["Filler Ratio"]

    communication_score = max(0, 100 - filler_ratio * 5)

    # ----------------------------
    # Final Score
    # ----------------------------
    final_score = (
        semantic_score * 0.60 +
        fluency_score * 0.25 +
        communication_score * 0.15
    )

    final_score = round(final_score, 2)

    # ----------------------------
    # Grade
    # ----------------------------
    if final_score >= 85:
        grade = "🟢 Excellent"

    elif final_score >= 70:
        grade = "🟡 Good"

    elif final_score >= 50:
        grade = "🟠 Moderate"

    else:
        grade = "🔴 Needs Improvement"

    return {
        "Semantic Score": round(semantic_score, 2),
        "Fluency Score": round(fluency_score, 2),
        "Communication Score": round(communication_score, 2),
        "Final Score": final_score,
        "Grade": grade
    }