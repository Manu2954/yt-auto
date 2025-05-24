import subprocess
import os
import math

def get_duration(path):
    """Returns duration of audio/video in seconds."""
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-select_streams", "v:0" if path.endswith(".mp4") else "a:0",
        "-show_entries", "stream=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

def reencode_clip(input_path, output_path):
    """Ensures all clips are the same format (720x1280, H.264)."""
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-vf", "scale=720:1280",  # For Shorts (9:16)
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ])

def merge_clips_with_audio(clip_paths, audio_path, output_path="final_output.mp4"):
    print("[INFO] Re-encoding clips...")
    encoded_clips = []
    for i, path in enumerate(clip_paths):
        encoded = f"encoded_{i}.mp4"
        reencode_clip(path, encoded)
        encoded_clips.append(encoded)

    total_video_duration = sum(get_duration(p) for p in encoded_clips)
    audio_duration = get_duration(audio_path)

    print(f"[INFO] Total video: {total_video_duration:.2f}s, Audio: {audio_duration:.2f}s")

    repeat_factor = math.ceil(audio_duration / total_video_duration)
    final_clip_list = encoded_clips * repeat_factor

    # Write concat list
    with open("concat.txt", "w") as f:
        for p in final_clip_list:
            f.write(f"file '{os.path.abspath(p)}'\n")

    # Concatenate
    print("[INFO] Concatenating clips...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-shortest", "temp_video.mp4"
    ])

    # Merge with audio
    print("[INFO] Merging with audio...")
    subprocess.run([
        "ffmpeg", "-y", "-i", "temp_video.mp4", "-i", audio_path,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac",
        "-shortest", output_path
    ])

    print(f"[DONE] Final video saved to {output_path}")

    # Clean up
    os.remove("concat.txt")
    os.remove("temp_video.mp4")
    for f in encoded_clips:
        os.remove(f)
        
clips = ['clips/Steam Peak_trimmed.mp4', 'clips/GTA Controversy_trimmed.mp4']
audio = 'audio/script.mp3'
merge_clips_with_audio(clips, audio)
