# from elevenlabs import generate, save, set_api_key

# def generate_voiceover(script: str, voice_id: str, elevenlabs_api_key: str, output_path="voice.mp3"):
#     set_api_key(elevenlabs_api_key)
#     audio = generate(text=script, voice=voice_id, model="eleven_monolingual_v1")
#     save(audio, output_path)

import os
import pandas as pd
from elevenlabs.client import ElevenLabs


def generate_voiceover(output_dir, script, api_key, voice_id):
    client = ElevenLabs(api_key=api_key)

    os.makedirs(output_dir, exist_ok=True)
    # df = pd.read_excel(excel_path)

    filename = f"{output_dir}/script.mp3"

    try:
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_monolingual_v1",
            text=script
        )

        with open(filename, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        print(f"✅ Saved: {filename}")
    except Exception as e:
        print(f"❌ Error on script : {e}")
    
    print("\nAudio generated!!")