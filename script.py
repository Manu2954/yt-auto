import requests
import pandas as pd
from dotenv import load_dotenv
import os
from video import get_video_urls, download_and_trim_videos
from voice import generate_voiceover



load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")


def fetch_reddit_trends(niche):
    url = f"https://www.reddit.com/r/{niche}/hot.json?limit=2"
    headers = {'User-agent': 'TrendBot/0.1'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    posts = response.json()["data"]["children"]
    return [post["data"]["title"] for post in posts]


def generate_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "google/gemma-3n-e4b-it:free",  # You can change this to any available OpenRouter model
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return data['choices'][0]['message']['content'].strip()

def generate_script(text, niche):
    prompt = f"Write a short, engaging voiceover without any headings or mentions for a YouTube Shorts video about this {niche} news:\n\n{text}\n\nKeep it under 60 seconds and casual tone. Dont add any side headings"
    return generate_openrouter(prompt)

def save_trends_with_scripts(trend, niche):
    data = []

    script = generate_script(trend, niche)
    keywords = parse_keywords(script)
    
    # Add current date and time for each entry
    data.append({
        "DateTime": pd.Timestamp.now(), 
        "Trend": trend,
        "GeneratedScript": script,
        "RelatedKeywords": keywords   # Adds current date and time
    })
    print(f"\n✅ Trend: {trend}\n🎬 Script: {script}\n")

    df = pd.DataFrame(data)
    df.to_excel("post1.xlsx", index=False)
    print("\n📁 Saved trends and scripts to 'post1.xlsx'")

def parse_keywords(raw_str):
    
    prompt_key = f"hey divide this into scenes and give a keyword to each scene and  also estimate how much time does each scene takes when readout for an ai text to speech generator and return only keywords with estimated time in order, without headings and numberings, separate them using commas, also estimate how much time does each scene takes when readout '{raw_str}'"
    keywords = generate_openrouter(prompt_key)    
    # Split the string into parts
    parts = [p.strip() for p in keywords.split(",")]
    
    # Pair keywords with their time values
    keyword_dict = {}
    for i in range(0, len(parts), 2):
        if i+1 >= len(parts):
            break  # Skip incomplete pairs
        keyword = parts[i]
        time_value = parts[i+1].replace("seconds", "").strip()
        keyword_dict[keyword] = int(time_value)
    return keyword_dict


def main():
    niche = 'gaming'
    reddit_trends = fetch_reddit_trends(niche)
    script = generate_script(reddit_trends, niche)
    save_trends_with_scripts(reddit_trends, niche)
    keywords = parse_keywords(script)
    print(keywords)
    video_urls = get_video_urls(keywords, PEXELS_API_KEY)
    print(video_urls)
    # script_audio = generate_voiceover('audio',script, ELEVENLABS_API_KEY, VOICE_ID)
    clips = download_and_trim_videos(video_urls, keywords)
    print(clips)

    
if __name__ == "__main__":
    main()
