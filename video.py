import requests
import os
import subprocess

PEXELS_API = "https://api.pexels.com/videos/search"

def get_video_urls(keys: dict, pexels_api_key: str) -> list:
    keywords = list(keys.keys())
    headers = {"Authorization": pexels_api_key}
    urls = []

    for kw in keywords:
        res = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params={"query": kw, "per_page": 5}
        )
        data = res.json()
        chosen_url = None

        for video in data.get("videos", []):
            for file in video.get("video_files", []):
                width = file.get("width")
                height = file.get("height")

                if height > width:  # vertical
                    chosen_url = file["link"]
                    break
            if chosen_url:
                break
        urls.append(chosen_url)
    return urls

def download_and_trim_videos(video_urls: list, durations: dict, download_dir="clips") -> list:
    os.makedirs(download_dir, exist_ok=True)
    trimmed_paths = []
    
    for idx, (scene_name, url) in enumerate(zip(durations.keys(), video_urls)):
        if url:
            raw_path = f"{download_dir}/{scene_name}_raw.mp4"
            trimmed_path = f"{download_dir}/{scene_name}_trimmed.mp4"
            duration = durations[scene_name]

            # Download video
            with requests.get(url, stream=True) as r:
                with open(raw_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            # Trim using FFmpeg
            subprocess.run([
                "ffmpeg", "-y", "-i", raw_path,
                "-ss", "0", "-t", str(duration),
                "-c:v", "libx264", "-c:a", "aac",
                trimmed_path
            ])
            trimmed_paths.append(trimmed_path)
    return trimmed_paths

