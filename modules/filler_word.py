import re

FILLER_WORDS = [
    "um",
    "uh",
    "like",
    "actually",
    "basically",
    "okay",
    "ok",
    "you know",
    "so",
    "well",
    "hmm"
]


def analyze_filler_words(transcript):

    text = transcript.lower()

    total_words = len(re.findall(r"\b\w+\b", text))

    detected = {}

    filler_count = 0

    for word in FILLER_WORDS:

        pattern = r"\b" + re.escape(word) + r"\b"

        count = len(re.findall(pattern, text))

        if count > 0:
            detected[word] = count
            filler_count += count

    if total_words > 0:
        filler_ratio = (filler_count / total_words) * 100
    else:
        filler_ratio = 0

    return {
        "Total Words": total_words,
        "Filler Count": filler_count,
        "Filler Ratio": round(filler_ratio, 2),
        "Detected Fillers": detected
    }