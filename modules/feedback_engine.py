def generate_feedback(score_result, filler_result):

    strengths = []

    suggestions = []

    if score_result["Semantic Score"] >= 80:
        strengths.append("Strong conceptual understanding.")
    else:
        suggestions.append("Explain the concept with more key ideas.")

    if filler_result["Filler Ratio"] < 3:
        strengths.append("Very few filler words.")
    else:
        suggestions.append("Reduce filler words like 'um' and 'uh'.")

    if score_result["Fluency Score"] >= 80:
        strengths.append("Good speaking fluency.")
    else:
        suggestions.append("Maintain a more consistent speaking pace.")

    return strengths, suggestions