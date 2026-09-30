from abc import ABC, abstractmethod

class TTSProvider(ABC):
    @abstractmethod
    async def generate_audio(self, text: str, output_path: str, voice: str = "en-US-AriaNeural") -> bool:
        """
        Generate audio from text and save to output_path.
        Returns True if successful, False otherwise.
        """
        pass
