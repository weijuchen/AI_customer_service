import os
from openai import OpenAI
from pathlib import Path
from typing import Dict, Any


class WhisperService:
    """Speech-to-Text Transcription Service"""

    def __init__(self):
        # Lazy loading: 只在第一次使用時才初始化 OpenAI client
        self.client = None
        self._initialized = False
        print(f"✓ Whisper Service 初始化完成（延遲載入模式）")
    
    def _lazy_init(self):
        """延遲初始化：只在第一次使用時才載入 OpenAI client"""
        if self._initialized:
            return
        
        print(f"首次使用語音識別，正在初始化 Whisper Service...")
        try:
            # Initializes the OpenAI client using the API key from environment variables
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self._initialized = True
            print(f"✓ Whisper Service 載入完成！")
        except Exception as e:
            print(f"✗ 無法初始化 Whisper Service: {e}")
            self._initialized = True  # 標記為已初始化，避免重複嘗試

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
