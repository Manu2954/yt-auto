import os
from moviepy import VideoFileClip, concatenate_videoclips

def concatenate_videos(video_paths, output_path="concatenated_video.mp4"):
    """
    Concatenate multiple video files into a single video.
    
    Args:
        video_paths (list): List of video file paths to concatenate
        output_path (str): Output file path for the concatenated video
    """
    loaded_clips = []
    final_video = None
    
    try:
        # Load and validate video clips
        print(f"[INFO] Loading {len(video_paths)} video clips...")
        total_duration = 0
        
        for i, video_path in enumerate(video_paths):
            if not os.path.exists(video_path):
                print(f"[WARNING] Video not found, skipping: {video_path}")
                continue
            
            try:
                clip = VideoFileClip(video_path)
                if clip.duration <= 0:
                    print(f"[WARNING] Video has zero duration, skipping: {video_path}")
                    clip.close()
                    continue
                
                loaded_clips.append(clip)
                total_duration += clip.duration
                print(f"[INFO] Loaded video {i+1}: {os.path.basename(video_path)} ({clip.duration:.2f}s)")
                
            except Exception as e:
                print(f"[WARNING] Failed to load {video_path}: {e}")
        
        if not loaded_clips:
            raise ValueError("[ERROR] No valid video clips found!")
        
        print(f"[INFO] Total duration: {total_duration:.2f} seconds")
        
        # Concatenate videos
        print("[INFO] Concatenating videos...")
        final_video = concatenate_videoclips(loaded_clips)
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Export final video
        print(f"[INFO] Exporting to: {output_path}")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac'
        )
        
        print(f"[SUCCESS] Video concatenated successfully!")
        print(f"[INFO] Final video: {output_path} ({final_video.duration:.2f}s)")
        
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up resources
        print("[INFO] Cleaning up...")
        for clip in loaded_clips:
            clip.close()
        if final_video:
            final_video.close()

def concatenate_with_fade(video_paths, output_path="faded_video.mp4", fade_duration=0.5):
    """
    Concatenate videos with crossfade transitions between clips.
    
    Args:
        video_paths (list): List of video file paths
        output_path (str): Output file path
        fade_duration (float): Duration of fade transition in seconds
    """
    loaded_clips = []
    final_video = None
    
    try:
        print(f"[INFO] Loading videos with {fade_duration}s crossfade...")
        
        for i, video_path in enumerate(video_paths):
            if not os.path.exists(video_path):
                print(f"[WARNING] Video not found, skipping: {video_path}")
                continue
            
            try:
                clip = VideoFileClip(video_path)
                
                # Add fade in/out effects
                if len(loaded_clips) > 0:  # Not the first clip
                    clip = clip.fadein(fade_duration)
                if i < len(video_paths) - 1:  # Not the last clip
                    clip = clip.fadeout(fade_duration)
                
                loaded_clips.append(clip)
                print(f"[INFO] Loaded: {os.path.basename(video_path)} ({clip.duration:.2f}s)")
                
            except Exception as e:
                print(f"[WARNING] Failed to load {video_path}: {e}")
        
        if not loaded_clips:
            raise ValueError("[ERROR] No valid video clips found!")
        
        # Concatenate with fade transitions
        final_video = concatenate_videoclips(loaded_clips, padding=-fade_duration, method="compose")
        
        # Export
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"[INFO] Exporting faded video to: {output_path}")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac'
        )
        
        print(f"[SUCCESS] Faded video created: {output_path}")
        
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        for clip in loaded_clips:
            clip.close()
        if final_video:
            final_video.close()

def batch_concatenate(input_folder, output_path="batch_concatenated.mp4", file_extensions=None):
    """
    Concatenate all video files from a folder.
    
    Args:
        input_folder (str): Folder containing video files
        output_path (str): Output file path
        file_extensions (list): List of file extensions to include (default: common video formats)
    """
    if file_extensions is None:
        file_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    
    try:
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"[ERROR] Input folder not found: {input_folder}")
        
        print(f"[INFO] Scanning folder: {input_folder}")
        
        # Get all video files from folder
        video_files = []
        for filename in sorted(os.listdir(input_folder)):
            if any(filename.lower().endswith(ext) for ext in file_extensions):
                video_files.append(os.path.join(input_folder, filename))
        
        if not video_files:
            raise ValueError(f"[ERROR] No video files found in {input_folder}")
        
        print(f"[INFO] Found {len(video_files)} video files")
        for i, video in enumerate(video_files, 1):
            print(f"  {i}. {os.path.basename(video)}")
        
        # Concatenate all videos
        concatenate_videos(video_files, output_path)
        
    except Exception as e:
        print(f"[ERROR] Batch concatenation failed: {e}")

# Example usage
def main():
    """Example usage of video concatenation functions"""
    
    # Method 1: Basic concatenation
    video_list = [
       'clips/Steam Peak_trimmed.mp4', 'clips/GTA Controversy_trimmed.mp4'
    ]
    
    print("=== Basic Video Concatenation ===")
    concatenate_videos(video_list, "output/basic_concat.mp4")
    
    print("\n=== Concatenation with Crossfade ===")
    concatenate_with_fade(video_list, "output/faded_concat.mp4", fade_duration=1.0)
    
    print("\n=== Batch Concatenation from Folder ===")
    batch_concatenate("clips/", "output/batch_concat.mp4")

if __name__ == "__main__":
    main()