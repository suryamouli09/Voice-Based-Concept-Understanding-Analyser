import os
import librosa
import matplotlib.pyplot as plt
import numpy as np

def save_uploaded_audio(uploaded_file):
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def get_audio_info(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 500:
        return 0.0, 0.0
    size = round(os.path.getsize(file_path) / (1024 * 1024), 2)
    try:
        y, sr = librosa.load(file_path, sr=None)
        duration = round(librosa.get_duration(y=y, sr=sr), 2)
    except Exception:
        duration = 0.0
    return size, duration

def generate_waveform(file_path):
    os.makedirs("outputs/graphs", exist_ok=True)
    waveform_path = os.path.join("outputs", "graphs", "waveform.png")

    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 500:
            raise ValueError("File too small or nonexistent.")
        y, sr = librosa.load(file_path, sr=None, mono=True)
        if len(y) == 0:
            raise ValueError("Empty audio signal.")
        time = np.arange(len(y)) / sr
    except Exception:
        # Graceful placeholder signal for silent/empty recordings
        sr = 16000
        y = np.zeros(sr)
        time = np.linspace(0, 1, sr)

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 3), facecolor='#111827')
    ax.set_facecolor('#111827')

    ax.plot(time, y, linewidth=0.7, color='#38BDF8', alpha=0.9)

    ax.set_title("Acoustic Audio Waveform", color='#F9FAFB', fontsize=12, fontweight='bold', pad=10)
    ax.set_xlabel("Time (seconds)", color='#9CA3AF', fontsize=9)
    ax.set_ylabel("Amplitude", color='#9CA3AF', fontsize=9)

    ax.tick_params(colors='#9CA3AF', labelsize=8)
    ax.grid(True, color='#1F2937', linestyle='--', alpha=0.5)

    for spine in ax.spines.values():
        spine.set_color('#374151')

    fig.savefig(
        waveform_path,
        dpi=200,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        edgecolor='none'
    )

    plt.close(fig)
    return waveform_path