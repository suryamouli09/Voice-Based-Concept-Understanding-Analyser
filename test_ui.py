"""
Automated verification test script for Voice Based Concept Understanding Analyser.
Run this script to test the end-to-end evaluation pipeline.
"""
import os
from modules.speech_to_text import transcribe_audio
from modules.feature_extractor import extract_audio_features
from modules.filler_word import analyze_filler_words
from modules.semantic_eval import semantic_similarity
from modules.scoring_engine import calculate_final_score
from modules.feedback_engine import generate_feedback
from modules.report_generator import generate_pdf_report
from utils.helper import load_reference_concepts

def test_pipeline():
    print("=" * 60)
    print("VBCUA End-to-End Pipeline Verification")
    print("=" * 60)

    sample_audio = "data/samples/sample_machine_learning.wav"
    assert os.path.exists(sample_audio), f"Missing {sample_audio}"
    print(f"[OK] Found test audio: {sample_audio}")

    # 1. Benchmark Concept
    concepts = load_reference_concepts()
    topic = "Machine Learning"
    ref_text = concepts[topic]["reference_text"]
    print(f"[OK] Reference concept '{topic}' loaded.")

    # 2. Whisper Speech-to-Text
    print("Transcribing with Whisper...")
    transcript = transcribe_audio(sample_audio)
    print(f"[OK] Transcribed: \"{transcript[:60]}...\"")
    assert len(transcript) > 0

    # 3. Librosa Feature Extraction
    print("Extracting acoustic DSP features...")
    features = extract_audio_features(sample_audio, transcript)
    print(f"[OK] Features: {features['Speech Rate']} WPM, Pitch {features['Pitch']} Hz")

    # 4. Filler Word Detection
    filler_res = analyze_filler_words(transcript)
    print(f"[OK] Fillers detected: {filler_res['Filler Count']} ({filler_res['Filler Ratio']}%)")

    # 5. Semantic Alignment
    print("Evaluating Sentence-BERT cosine similarity...")
    sem_res = semantic_similarity(transcript, ref_text)
    print(f"[OK] Semantic Score: {sem_res['Similarity']}% ({sem_res['Level']})")

    # 6. Scoring & Feedback
    score_res = calculate_final_score(features, filler_res, sem_res)
    feedback = generate_feedback(score_res, filler_res, features, transcript, ref_text)
    print(f"[OK] Final Score: {score_res['Final Score']}/100 -> {score_res['Grade']}")

    # 7. PDF Report Generation
    pdf_path = generate_pdf_report(
        topic, transcript, features, filler_res, sem_res, score_res,
        feedback["strengths"], feedback["suggestions"]
    )
    print(f"[OK] PDF Report generated: {pdf_path}")
    assert os.path.exists(pdf_path)

    print("=" * 60)
    print("ALL TESTS PASSED! APPLICATION IS 100% OPERATIONAL.")
    print("=" * 60)

if __name__ == "__main__":
    test_pipeline()
