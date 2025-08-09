import os
import subprocess
import math
from utils import file_exists, get_file_size_mb

def get_audio_duration(audio_file):
    """Get audio duration in seconds"""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'csv=p=0',
        '-show_entries', 'format=duration',
        audio_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except subprocess.CalledProcessError:
        print("Error getting audio duration")
        return None

def split_audio_into_chunks(audio_file, chunks_dir, max_size_mb=18):
    """Split FLAC file into chunks of maximum size"""
    if not file_exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return []
    
    existing_chunks = [f for f in os.listdir(chunks_dir) if f.endswith('.flac')]
    if existing_chunks:
        print(f"Chunks already exist: {len(existing_chunks)} files")
        return [os.path.join(chunks_dir, f) for f in sorted(existing_chunks)]
    
    file_size_mb = get_file_size_mb(audio_file)
    if file_size_mb <= max_size_mb:
        chunk_file = os.path.join(chunks_dir, "chunk_01.flac")
        os.system(f"cp '{audio_file}' '{chunk_file}'")
        print(f"File is already under {max_size_mb}MB")
        return [chunk_file]
    
    total_duration = get_audio_duration(audio_file)
    if not total_duration:
        return []
    
    file_size_bytes = os.path.getsize(audio_file)
    max_size_bytes = max_size_mb * 1024 * 1024
    num_chunks = math.ceil(file_size_bytes / max_size_bytes)
    chunk_duration = total_duration / num_chunks
    
    chunks = []
    
    for i in range(num_chunks):
        start_time = i * chunk_duration
        output_file = os.path.join(chunks_dir, f"chunk_{i+1:02d}.flac")
        
        cmd = [
            'ffmpeg',
            '-i', audio_file,
            '-ss', str(start_time),
            '-t', str(chunk_duration),
            '-ar', '16000',
            '-ac', '1',
            '-map', '0:a',
            '-c:a', 'flac',
            output_file
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            chunks.append(output_file)
            size_mb = get_file_size_mb(output_file)
            print(f"Created chunk: {os.path.basename(output_file)} ({size_mb:.2f}MB)")
        except subprocess.CalledProcessError as e:
            print(f"Error creating chunk {i+1}: {e}")
    
    return chunks