import edge_tts
from app.providers.tts.interface import TTSProvider

class EdgeTTSProvider(TTSProvider):
    async def generate_audio(self, text: str, output_path: str, voice: str = "en-US-AriaNeural") -> bool:
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"EdgeTTS Error: {e}")
            return False
