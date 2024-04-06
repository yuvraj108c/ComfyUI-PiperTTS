import json
import httpx
from tqdm import tqdm
import os

base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

with open("/ComfyUI/custom_nodes/ComfyUI-PiperTTS/voices.json", 'r') as file:
    voices_file = json.load(file)

def download_file(url, save_path):
    print(f"downloading {url} ...")
    with httpx.stream("GET", url, follow_redirects=True) as stream:
        total = int(stream.headers["Content-Length"])
        with open(f"{save_path}", "wb") as f, tqdm(
            total=total, unit_scale=True, unit_divisor=1024, unit="B"
        ) as progress:
            num_bytes_downloaded = stream.num_bytes_downloaded
            for data in stream.iter_bytes():
                f.write(data)
                progress.update(
                    stream.num_bytes_downloaded - num_bytes_downloaded
                )
                num_bytes_downloaded = stream.num_bytes_downloaded

def download_tts_model(voice, save_dir):
    for v in voices_file:
        if v == voice:
            for file in voices_file[v]["files"]:
                if file.endswith(".json"): 
                    download_file(f"{base_url}/{file}",os.path.join(save_dir, f"{voice}.onnx.json"))
                if file.endswith(".onnx"):
                    download_file(f"{base_url}/{file}",os.path.join(save_dir, f"{voice}.onnx"))

def get_tts_voice_names_without_quality():
    voice_names = list(set([x.rsplit('-', 1)[0] for x in voices_file]))
    voice_names.sort()
    return voice_names

def get_tts_voice_names_with_quality():
    return [x for x in voices_file]