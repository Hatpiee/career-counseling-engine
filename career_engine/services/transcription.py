import os
import tempfile
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def transcribe_audio_file(uploaded_bytes: bytes, original_filename: str) -> str:
    suffix = os.path.splitext(original_filename)[1] or ".wav"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
        temp_audio.write(uploaded_bytes)
        temp_path = temp_audio.name

    try:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(temp_path)

        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(transcript.error)

        return transcript.text or ""
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)