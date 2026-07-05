import os
import librosa
import matplotlib.pyplot as plt
import numpy as np
from mutagen import File


def save_uploaded_audio(uploaded_file):
    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join("uploads", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def get_audio_info(file_path):
    audio = File(file_path)

    size = round(os.path.getsize(file_path) / (1024 * 1024), 2)
    duration = round(audio.info.length, 2)

    return size, duration


def generate_waveform(file_path):

    # Load audio
    y, sr = librosa.load(file_path, sr=None, mono=True)

    os.makedirs("outputs/graphs", exist_ok=True)

    waveform_path = os.path.join(
        "outputs",
        "graphs",
        "waveform.png"
    )

    # Create time axis
    time = np.arange(len(y)) / sr

    fig, ax = plt.subplots(figsize=(14, 3))

    ax.plot(time, y, linewidth=0.5)

    ax.set_title("Audio Waveform")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Amplitude")

    ax.grid(True)

    fig.savefig(
        waveform_path,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close(fig)

    return waveform_path