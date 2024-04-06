import folder_paths
import wave
from piper.voice import PiperVoice
import os
import re
from .utils import get_tts_voice_names_without_quality, get_tts_voice_names_with_quality, download_tts_model

class PiperTTS:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "text": ("STRING", {"default": "", "multiline": True}),
                "voice": (get_tts_voice_names_without_quality(),),
                "quality": (["high", "medium", "low"], {"default":"high"}),
            }
        }

    RETURN_NAMES = ("audio_path",)
    RETURN_TYPES = ("STRING",)
    FUNCTION = "main"
    CATEGORY = "PiperTTS"
    OUTPUT_NODE=True

    def main(self, text, voice, quality):

        if len(text) == 0:
            raise ValueError("Text cannot be empty.")

        voice_with_quality = f"{voice}-{quality}"

        if not voice_with_quality in get_tts_voice_names_with_quality():
            raise ValueError(f"{voice_with_quality} does not exist. Refer to https://github.com/rhasspy/piper/blob/master/VOICES.md")

        models_folder_name = "piper_tts"
        models_dir = os.path.join(folder_paths.models_dir,models_folder_name)
        os.makedirs(models_dir, exist_ok=True)

        output_dir = "piper_tts"
        output_path = os.path.join(folder_paths.get_output_directory(), output_dir)
        os.makedirs(output_path, exist_ok=True)

        voice_model_path = os.path.join(models_dir,f"{voice_with_quality}.onnx")

        if not os.path.exists(voice_model_path):
            download_tts_model(voice_with_quality, models_dir)

        TTS = PiperVoice.load(
            model_path=voice_model_path
        )

        audio_save_name = f"{((re.sub('[^A-Za-z]', ' ', text)).strip()).replace(' ', '_')[:60]}.wav"
        audio_save_path = os.path.join(output_path,audio_save_name)
        wav_file = wave.open(audio_save_path, 'w')
        audio = TTS.synthesize(text, wav_file)
        wav_file.close()

        previews = [
            {
                "filename": audio_save_name,
                "subfolder": output_dir,
                "type":"output"
            }
        ]
        return {"ui": {"previews":previews},"result": (audio_save_path,)}