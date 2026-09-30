from typing import Dict, Any
from moviepy import ColorClip, TextClip, CompositeVideoClip
from app.renderers.base import BaseRenderer

class TitleCardRenderer(BaseRenderer):
    async def render(self, visual_data: Dict[str, Any], duration: float, output_path: str) -> bool:
        try:
            text = visual_data.get("text", "Title")
            
            # Create a simple background
            bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0)).with_duration(duration)
            
            # Create text clip using TextClip
            # Note: TextClip requires ImageMagick or proper font configuration
            # If it fails, we fall back to just a color clip for the demo
            try:
                import os
                font_path = "C:/Windows/Fonts/arial.ttf"
                if not os.path.exists(font_path):
                    # fallback to some other standard Windows font or default
                    font_path = "C:/Windows/Fonts/seguiemj.ttf" # usually exists

                txt_clip = TextClip(
                    font=font_path, 
                    text=text,
                    font_size=100,
                    color='white'
                ).with_position('center').with_duration(duration)
                
                video = CompositeVideoClip([bg_clip, txt_clip])
            except Exception as e:
                print(f"TextClip failed (might need ImageMagick): {e}. Using blank background.")
                video = bg_clip
                
            video.write_videofile(output_path, fps=24, logger=None)
            video.close()
            return True
        except Exception as e:
            print(f"TitleCardRenderer error: {e}")
            return False
