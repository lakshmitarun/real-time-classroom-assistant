import os
import hashlib

class SpeechService:
    def __init__(self):
        self.audio_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'audio')
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def text_to_speech(self, text, language='english'):
        """Convert text to speech and return audio file path"""
        if not text:
            return None
        
        # Map language codes
        lang_map = {
            'english': 'en',
            'bodo': 'hi',  # Use Hindi for Bodo (closest approximation)
            'mizo': 'en'   # Use English for Mizo
        }
        
        lang_code = lang_map.get(language.lower(), 'en')
        
        # Create unique filename based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
        filename = f'{language}_{text_hash}.mp3'
        filepath = os.path.join(self.audio_dir, filename)
        
        # Generate audio if not exists
        if not os.path.exists(filepath):
            try:
                # Try to use gTTS if available
                from gtts import gTTS
                tts = gTTS(text=text, lang=lang_code, slow=False)
                tts.save(filepath)
            except ImportError:
                print("gTTS not installed. Install with: pip install gTTS")
                return None
            except Exception as e:
                print(f"Error generating speech: {e}")
                return None
        
        return f'/static/audio/{filename}'
    
    def speech_to_text(self, audio_file):
        """Convert speech to text (placeholder for future implementation)"""
        # This would use services like Google Speech-to-Text, Azure, etc.
        # For now, return placeholder
        return "Speech recognition not yet implemented"
