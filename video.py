import requests
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


