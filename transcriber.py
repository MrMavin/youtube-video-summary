import os
import json
from groq import Groq
from dotenv import load_dotenv
from utils import file_exists

load_dotenv()

def initialize_groq_client():
    """Initialize Groq client with API key from environment"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)

def transcribe_audio_chunk(audio_file, output_file, prompt=""):
    """Transcribe a single audio chunk using Groq"""
    if file_exists(output_file):
        print(f"Transcription already exists: {os.path.basename(output_file)}")
        return output_file
    
    if not file_exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return None
    
    try:
        client = initialize_groq_client()
        
        with open(audio_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3-turbo",
                prompt=prompt,
                response_format="text",
                temperature=0.0
            )
        
        # Save transcription text to file
        with open(output_file, 'w') as f:
            f.write(transcription)
        
        print(f"Transcribed: {os.path.basename(audio_file)} -> {os.path.basename(output_file)}")
        return output_file
        
    except Exception as e:
        print(f"Error transcribing {audio_file}: {e}")
        return None

def transcribe_all_chunks(chunks, transcripts_dir, prompt=""):
    """Transcribe all audio chunks"""
    transcription_files = []
    
    for chunk_file in chunks:
        chunk_name = os.path.splitext(os.path.basename(chunk_file))[0]
        output_file = os.path.join(transcripts_dir, f"{chunk_name}_transcript.txt")
        
        result = transcribe_audio_chunk(chunk_file, output_file, prompt)
        if result:
            transcription_files.append(result)
    
    return transcription_files

def combine_transcriptions(transcription_files, output_file):
    """Combine all chunk transcriptions into a single text file"""
    if file_exists(output_file):
        print(f"Combined transcription already exists: {os.path.basename(output_file)}")
        return output_file
    
    combined_text = ""
    
    for transcript_file in sorted(transcription_files):
        try:
            with open(transcript_file, 'r') as f:
                text = f.read().strip()
                combined_text += text + " "
        except Exception as e:
            print(f"Error processing {transcript_file}: {e}")
    
    # Save combined transcription
    with open(output_file, 'w') as f:
        f.write(combined_text.strip())
    
    print(f"Combined transcription saved: {os.path.basename(output_file)}")
    return output_file