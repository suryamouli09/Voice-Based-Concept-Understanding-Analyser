import streamlit as st


def upload_audio():
    """Reusable audio uploader."""
    return st.file_uploader(
        "Choose an audio file",
        type=["wav", "mp3", "m4a"],
        help="Supported formats: WAV, MP3, M4A"
    )


def audio_summary(size, duration, file_type):
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📁 File Size", f"{size} MB")
    c2.metric("⏱ Duration", f"{duration} sec")
    c3.metric("🎵 Format", file_type.upper())
    c4.metric("✅ Status", "Ready")


def loading(message="Analyzing audio..."):
    return st.spinner(message)


def empty_state(message):
    st.info(message)