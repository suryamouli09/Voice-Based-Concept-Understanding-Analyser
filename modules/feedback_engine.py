import re

TOPIC_PROMPTS = {
    "Machine Learning": [
        "1. Define Machine Learning in 1-2 clear sentences without using buzzwords.",
        "2. Explain how algorithms improve through experience and pattern recognition.",
        "3. State one practical difference between traditional rules-based programming and ML."
    ],
    "Cloud Computing": [
        "1. State the fundamental definition of Cloud Computing and the on-demand model.",
        "2. Name 3 core resource categories delivered (compute, storage, databases, networking).",
        "3. Explain why scalability and cost-efficiency make the cloud valuable for enterprises."
    ],
    "Artificial Intelligence": [
        "1. Define Artificial Intelligence and what distinguishes it from standard software.",
        "2. Explain the cognitive processes simulated (learning, reasoning, problem solving, decision making).",
        "3. Provide a real-world example of AI in autonomous systems or natural language."
    ],
    "Data Science": [
        "1. What 3 core disciplines intersect to form Data Science?",
        "2. Describe the end-to-end journey from raw data to actionable business insights.",
        "3. How does machine learning fit into the data science workflow?"
    ],
    "Operating System": [
        "1. What is an Operating System and what is its primary role in computer architecture?",
        "2. Name the 3 critical resources managed by an OS (CPU/Processes, Memory, Storage/Files).",
        "3. Explain how the OS acts as an intermediary bridge between user applications and bare hardware."
    ]
}

TOPIC_COACHING = {
    "Machine Learning": {
        "pitch": "Machine Learning is a subset of AI where systems learn to perform tasks and recognize patterns directly from historical data, improving their accuracy over time without explicit hardcoded instructions.",
        "analogy": "Think of teaching a child to recognize cats: instead of writing a million rules about fur and whiskers, you show them thousands of pictures of cats until their brain learns the visual pattern.",
        "mistakes": "Avoid saying 'ML is just an if-else statement' or confusing Machine Learning with general Artificial Intelligence."
    },
    "Cloud Computing": {
        "pitch": "Cloud Computing is the on-demand delivery of compute power, database storage, and applications over the Internet with pay-as-you-go pricing, eliminating the need to own physical servers.",
        "analogy": "It works like the electricity grid: you don't build your own power generator; you plug into the wall and only pay for the kilowatt-hours you consume.",
        "mistakes": "Forgetting to mention 'on-demand' or 'scalability' and only referring to it as 'online storage'."
    },
    "Artificial Intelligence": {
        "pitch": "Artificial Intelligence is the broad engineering science of creating smart machines capable of performing tasks that typically require human intelligence, such as reasoning, visual perception, and decision-making.",
        "analogy": "AI is the broad umbrella of flight (like aircraft), while Machine Learning is the specific jet engine that powers modern advancement.",
        "mistakes": "Equating AI strictly with generative AI or robots without mentioning reasoning and problem-solving."
    },
    "Data Science": {
        "pitch": "Data Science is the interdisciplinary field combining statistical analysis, programming, and domain expertise to extract meaningful, actionable insights from structured and unstructured data.",
        "analogy": "Like an investigative journalist analyzing thousands of financial records to uncover the hidden story behind a market trend.",
        "mistakes": "Focusing solely on coding and ignoring the statistical rigor and domain business impact."
    },
    "Operating System": {
        "pitch": "An Operating System is the master system software that coordinates computer hardware, allocates memory and CPU resources, manages file systems, and provides a unified interface for applications.",
        "analogy": "Think of an air traffic controller managing runways (CPU), gates (RAM), and flight schedules (processes) so planes don't crash into each other.",
        "mistakes": "Describing the OS merely as the user desktop UI (like Windows or macOS icons) rather than the underlying kernel resource manager."
    }
}

KEYWORD_FACTS = {
    "algorithm": "Algorithms are step-by-step procedures used by computational models to process inputs and calculate outputs.",
    "patterns": "Pattern recognition allows models to identify underlying regularities and correlations across feature distributions.",
    "predictions": "Prediction is the core objective of inductive inference models evaluated on unseen test data.",
    "scalability": "Scalability is the architectural ability to handle growing workloads by provisioning resources elastically.",
    "databases": "Databases ensure structured persistence, indexing, and transactional ACID integrity.",
    "networking": "Cloud networking guarantees low latency, VPC isolation, and distributed routing.",
    "simulation": "Simulation models emulate physical or cognitive systems via mathematical abstractions.",
    "reasoning": "Reasoning involves drawing deductive or inductive inferences from known premises and observations.",
    "statistics": "Statistics provides mathematical rigor, hypothesis testing, and uncertainty quantification.",
    "interface": "An interface establishes standardized protocols and abstraction layers between decoupled system components.",
    "hardware": "Hardware encompasses physical silicon, registers, ALUs, memory buses, and peripheral controllers.",
    "processes": "Processes represent independent program execution instances with dedicated virtual memory space."
}

def get_topic_prompts(topic: str) -> list:
    """Returns interview practice questions for a topic."""
    return TOPIC_PROMPTS.get(topic, [
        f"1. Explain the primary definition and scope of {topic}.",
        f"2. Describe the core mechanism or architecture underlying {topic}.",
        f"3. Provide a practical application and key benefits of {topic}."
    ])

def get_topic_coach_answer(topic: str, q_type: str) -> str:
    """Returns instant coaching knowledge for a topic."""
    topic_data = TOPIC_COACHING.get(topic, TOPIC_COACHING["Machine Learning"])
    if q_type == "pitch":
        return topic_data.get("pitch", "")
    elif q_type == "analogy":
        return topic_data.get("analogy", "")
    elif q_type == "mistakes":
        return topic_data.get("mistakes", "")
    return ""

def get_keyword_flashcard_fact(keyword: str, topic: str) -> str:
    """Returns a short explanation of why a keyword is conceptually vital."""
    clean_kw = keyword.lower().strip()
    for k, v in KEYWORD_FACTS.items():
        if k in clean_kw:
            return v
    return f"In the context of {topic}, '{keyword}' represents a fundamental technical pillar required for precise conceptual articulation."

def generate_refined_speech(transcript: str, detected_fillers: dict) -> str:
    """
    Cleans filler words and elevates spoken transcript into an executive-level delivery.
    """
    if not transcript:
        return "No spoken input to refine."

    text = transcript
    for filler in detected_fillers.keys():
        pattern = re.compile(r"\b" + re.escape(filler) + r"\b,?\s*", re.IGNORECASE)
        text = pattern.sub("", text)

    # Clean double spaces and punctuation gaps
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,!?;])', r'\1', text)
    text = text.strip()

    if text:
        text = text[0].upper() + text[1:]

    return text

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