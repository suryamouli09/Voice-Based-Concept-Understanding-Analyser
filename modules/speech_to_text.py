import os
import whisper

# Load model once when the app starts
model = whisper.load_model("base")


def transcribe_audio(audio_path):

    result = model.transcribe(audio_path)

    transcript = result["text"].strip()

    # Save transcript
    os.makedirs("outputs/transcripts", exist_ok=True)

    transcript_file = os.path.join(
        "outputs",
        "transcripts",
        "transcript.txt"
    )

    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    return transcript