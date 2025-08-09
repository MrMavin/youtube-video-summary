import os
import re
import subprocess
from utils import file_exists

def count_sentences(text):
    """Count sentences in text using basic sentence ending punctuation"""
    sentence_endings = re.findall(r'[.!?]+', text)
    return len(sentence_endings)

def count_words(text):
    """Count words in text"""
    return len(text.split())

def get_text_stats(text):
    """Get comprehensive text statistics"""
    return {
        'characters': len(text),
        'characters_no_spaces': len(text.replace(' ', '')),
        'words': count_words(text),
        'sentences': count_sentences(text)
    }

def get_audio_duration(audio_file):
    """Get audio duration in seconds using ffprobe"""
    if not file_exists(audio_file):
        return None
    
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
        return None

def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS"""
    if seconds is None:
        return "Unknown"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def analyze_audio_file(file_path):
    """Analyze an audio file for metadata"""
    if not file_exists(file_path):
        return None
    
    try:
        duration = get_audio_duration(file_path)
        stats = {
            'filename': os.path.basename(file_path),
            'file_size_bytes': os.path.getsize(file_path),
            'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
            'duration_seconds': duration,
            'duration_formatted': format_duration(duration)
        }
        return stats
    except Exception as e:
        print(f"Error analyzing audio {file_path}: {e}")
        return None

def analyze_transcription_file(file_path):
    """Analyze a single transcription file"""
    if not file_exists(file_path):
        return None
    
    try:
        with open(file_path, 'r') as f:
            text = f.read().strip()
        
        stats = get_text_stats(text)
        stats['file_size_bytes'] = os.path.getsize(file_path)
        stats['filename'] = os.path.basename(file_path)
        
        return stats
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None

def analyze_all_content(audio_file, chunks, transcription_files, combined_transcript=None):
    """Analyze all content including audio and transcriptions"""
    
    # Analyze original audio file
    original_audio = analyze_audio_file(audio_file)
    
    # Analyze audio chunks
    audio_chunks = []
    total_audio_stats = {
        'file_size_bytes': 0,
        'file_size_mb': 0,
        'duration_seconds': 0,
        'chunk_count': 0
    }
    
    for chunk_file in sorted(chunks):
        chunk_stats = analyze_audio_file(chunk_file)
        if chunk_stats:
            audio_chunks.append(chunk_stats)
            total_audio_stats['file_size_bytes'] += chunk_stats['file_size_bytes']
            total_audio_stats['file_size_mb'] += chunk_stats['file_size_mb']
            if chunk_stats['duration_seconds']:
                total_audio_stats['duration_seconds'] += chunk_stats['duration_seconds']
            total_audio_stats['chunk_count'] += 1
    
    total_audio_stats['duration_formatted'] = format_duration(total_audio_stats['duration_seconds'])
    
    # Analyze transcriptions
    transcription_chunks = []
    total_transcript_stats = {
        'characters': 0,
        'characters_no_spaces': 0,
        'words': 0,
        'sentences': 0,
        'file_size_bytes': 0,
        'chunk_count': 0
    }
    
    for file_path in sorted(transcription_files):
        stats = analyze_transcription_file(file_path)
        if stats:
            transcription_chunks.append(stats)
            total_transcript_stats['characters'] += stats['characters']
            total_transcript_stats['characters_no_spaces'] += stats['characters_no_spaces']
            total_transcript_stats['words'] += stats['words']
            total_transcript_stats['sentences'] += stats['sentences']
            total_transcript_stats['file_size_bytes'] += stats['file_size_bytes']
            total_transcript_stats['chunk_count'] += 1
    
    # Analyze combined transcript if provided
    combined_transcript_stats = None
    if combined_transcript and file_exists(combined_transcript):
        combined_transcript_stats = analyze_transcription_file(combined_transcript)
    
    return {
        'original_audio': original_audio,
        'audio_chunks': audio_chunks,
        'audio_totals': total_audio_stats,
        'transcription_chunks': transcription_chunks,
        'transcription_totals': total_transcript_stats,
        'combined_transcript': combined_transcript_stats
    }

def display_content_metadata(metadata):
    """Display comprehensive metadata for all content"""
    print("\n" + "="*70)
    print("COMPREHENSIVE CONTENT METADATA")
    print("="*70)
    
    # Original audio file
    if metadata['original_audio']:
        audio = metadata['original_audio']
        print(f"\nORIGINAL AUDIO FILE:")
        print("-" * 25)
        print(f"File:     {audio['filename']}")
        print(f"Duration: {audio['duration_formatted']}")
        print(f"Size:     {audio['file_size_mb']:.2f} MB ({audio['file_size_bytes']:,} bytes)")
    
    # Audio chunks
    if metadata['audio_chunks']:
        print(f"\nAUDIO CHUNKS ({len(metadata['audio_chunks'])} files):")
        print("-" * 40)
        for i, chunk in enumerate(metadata['audio_chunks'], 1):
            print(f"Chunk {i:2d}: {chunk['filename']}")
            print(f"  Duration: {chunk['duration_formatted']}")
            print(f"  Size:     {chunk['file_size_mb']:.2f} MB ({chunk['file_size_bytes']:,} bytes)")
        
        # Audio totals
        audio_totals = metadata['audio_totals']
        print(f"\nAUDIO TOTALS:")
        print(f"Total chunks:  {audio_totals['chunk_count']}")
        print(f"Total duration: {audio_totals['duration_formatted']}")
        print(f"Total size:    {audio_totals['file_size_mb']:.2f} MB ({audio_totals['file_size_bytes']:,} bytes)")
        print(f"Average chunk: {audio_totals['file_size_mb']/audio_totals['chunk_count']:.2f} MB")
    
    # Transcription chunks
    if metadata['transcription_chunks']:
        print(f"\nTRANSCRIPTION CHUNKS ({len(metadata['transcription_chunks'])} files):")
        print("-" * 55)
        for i, chunk in enumerate(metadata['transcription_chunks'], 1):
            print(f"Chunk {i:2d}: {chunk['filename']}")
            print(f"  Characters: {chunk['characters']:,} ({chunk['characters_no_spaces']:,} no spaces)")
            print(f"  Words:      {chunk['words']:,}")
            print(f"  Sentences:  {chunk['sentences']:,}")
            print(f"  File size:  {chunk['file_size_bytes']:,} bytes")
        
        # Transcription totals
        transcript_totals = metadata['transcription_totals']
        print(f"\nTRANSCRIPTION TOTALS:")
        print(f"Total chunks:     {transcript_totals['chunk_count']}")
        print(f"Total characters: {transcript_totals['characters']:,} ({transcript_totals['characters_no_spaces']:,} no spaces)")
        print(f"Total words:      {transcript_totals['words']:,}")
        print(f"Total sentences:  {transcript_totals['sentences']:,}")
        print(f"Total file size:  {transcript_totals['file_size_bytes']:,} bytes")
        
        if transcript_totals['words'] > 0:
            avg_words_per_chunk = transcript_totals['words'] / transcript_totals['chunk_count']
            avg_chars_per_word = transcript_totals['characters_no_spaces'] / transcript_totals['words']
            avg_words_per_sentence = transcript_totals['words'] / transcript_totals['sentences'] if transcript_totals['sentences'] > 0 else 0
            
            print(f"\nTRANSCRIPTION AVERAGES:")
            print(f"Words per chunk:     {avg_words_per_chunk:.1f}")
            print(f"Characters per word: {avg_chars_per_word:.1f}")
            print(f"Words per sentence:  {avg_words_per_sentence:.1f}")
    
    # Combined transcript
    if metadata['combined_transcript']:
        combined = metadata['combined_transcript']
        print(f"\nCOMBINED TRANSCRIPT:")
        print("-" * 25)
        print(f"File:       {combined['filename']}")
        print(f"Characters: {combined['characters']:,} ({combined['characters_no_spaces']:,} no spaces)")
        print(f"Words:      {combined['words']:,}")
        print(f"Sentences:  {combined['sentences']:,}")
        print(f"File size:  {combined['file_size_bytes']:,} bytes")
    
    print("="*70)