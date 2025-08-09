import os
import subprocess
from utils import file_exists

def download_youtube_audio(youtube_url, output_dir):
    """Download YouTube video as FLAC using yt-dlp with grok.com compatible settings"""
    output_file = os.path.join(output_dir, "audio.flac")
    
    if file_exists(output_file):
        print(f"Audio already exists: {output_file}")
        return output_file
    
    cmd = [
        'yt-dlp',
        '-f', 'bestaudio',
        '--extract-audio',
        '--audio-format', 'flac',
        '--postprocessor-args', 'ffmpeg:-ar 16000 -ac 1',
        '-o', os.path.join(output_dir, "audio.%(ext)s"),
        youtube_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Download successful: {output_file}")
        return output_file if file_exists(output_file) else None
    except subprocess.CalledProcessError as e:
        print(f"Error downloading: {e.stderr}")
        return None