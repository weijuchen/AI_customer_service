import os
from openai import OpenAI
from pathlib import Path
from typing import Dict, Any


class WhisperService:
    """Speech-to-Text Transcription Service"""

    def __init__(self):
        # Initializes the OpenAI client using the API key from environment variables
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def transcribe(self, audio_file_path: str) -> Dict[str, str]:
        """
        Converts an audio file to text using the Whisper API.

        Args:
            audio_file_path: Path to the audio file (supports mp3, mp4, mpeg, mpga, m4a, wav, webm).

        Returns:
            {"text": "transcribed text", "language": "language code"} or
            {"error": "failure reason", "text": "", "language": ""}
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                # Use the Whisper API for transcription
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file, language="zh"  # Specify Chinese
                )

            return {"text": transcript.text, "language": "zh"}

        except Exception as e:
            return {
                "error": f"Speech transcription failed: {str(e)}",
                "text": "",
                "language": "",
            }

    def transcribe_from_bytes(
        self, audio_bytes: bytes, filename: str = "audio.wav"
    ) -> Dict[str, str]:
        """
        Converts audio bytes to text (useful for API uploads).

        Args:
            audio_bytes: The raw audio data as bytes.
            filename: A filename to infer the audio format (e.g., "audio.wav").

        Returns:
            {"text": "transcribed text", "language": "language code"} or
            {"error": "failure reason", "text": "", "language": ""}
        """
        try:
            # The Whisper API requires a file-like object, which we simulate with BytesIO
            from io import BytesIO

            audio_file = BytesIO(audio_bytes)
            audio_file.name = (
                filename  # The API needs a filename to determine the format
            )

            transcript = self.client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, language="zh"
            )

            return {"text": transcript.text, "language": "zh"}

        except Exception as e:
            return {
                "error": f"Speech transcription failed: {str(e)}",
                "text": "",
                "language": "",
            }


# Test Code
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    whisper_service = WhisperService()

    # Test: Create a test message (In real use, you would upload a real audio file)
    print("Whisper Service initialized.")
    print("Note: Please upload an audio file via the API for testing.")
