import re
import os
from urllib.parse import urlparse, parse_qs

def extract_video_id(youtube_url):
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:vi\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    return None

def create_video_folders(video_id, base_dir="videos"):
    """Create folder structure for a video"""
    video_dir = os.path.join(base_dir, video_id)
    audio_dir = os.path.join(video_dir, "audio")
    chunks_dir = os.path.join(video_dir, "chunks")
    transcripts_dir = os.path.join(video_dir, "transcripts")
    
    for directory in [video_dir, audio_dir, chunks_dir, transcripts_dir]:
        os.makedirs(directory, exist_ok=True)
    
    return {
        'video_dir': video_dir,
        'audio_dir': audio_dir,
        'chunks_dir': chunks_dir,
        'transcripts_dir': transcripts_dir
    }

def get_file_size_mb(filepath):
    """Get file size in MB"""
    if os.path.exists(filepath):
        return os.path.getsize(filepath) / (1024 * 1024)
    return 0

def file_exists(filepath):
    """Check if file exists and is not empty"""
    return os.path.exists(filepath) and os.path.getsize(filepath) > 0