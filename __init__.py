from .nodes import PiperTTS

NODE_CLASS_MAPPINGS = { 
    "PiperTTS" : PiperTTS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
     "PiperTTS" : "Piper TTS" 
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS','WEB_DIRECTORY']