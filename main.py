#!/usr/bin/env python3
import sys
import os
from utils import extract_video_id, create_video_folders
from downloader import download_youtube_audio
from splitter import split_audio_into_chunks
from transcriber import transcribe_all_chunks, combine_transcriptions
from metadata import analyze_all_content, display_content_metadata
from analysis import TranscriptAnalyzer

def process_youtube_video(youtube_url):
    """Process a YouTube video: download audio and split into chunks"""
    
    # Extract video ID
    video_id = extract_video_id(youtube_url)
    if not video_id:
        print("Error: Could not extract video ID from URL")
        return None
    
    print(f"Processing video ID: {video_id}")
    
    # Create folder structure
    folders = create_video_folders(video_id)
    print(f"Working directory: {folders['video_dir']}")
    
    # Download audio
    audio_file = download_youtube_audio(youtube_url, folders['audio_dir'])
    if not audio_file:
        print("Failed to download audio")
        return None
    
    # Split into chunks
    chunks = split_audio_into_chunks(audio_file, folders['chunks_dir'])
    if not chunks:
        print("Failed to create chunks")
        return None
    
    # Transcribe chunks
    transcription_files = transcribe_all_chunks(chunks, folders['transcripts_dir'])
    if not transcription_files:
        print("Failed to transcribe audio")
        return None
    
    # Combine transcriptions
    combined_transcript = os.path.join(folders['transcripts_dir'], "full_transcript.txt")
    combine_transcriptions(transcription_files, combined_transcript)
    
    # Generate and display metadata
    metadata = analyze_all_content(audio_file, chunks, transcription_files, combined_transcript)
    display_content_metadata(metadata)
    
    # Perform LLM analysis on individual chunks
    print(f"\n{'='*60}")
    print("STARTING LLM ANALYSIS ON INDIVIDUAL CHUNKS")
    print(f"{'='*60}")
    
    if transcription_files:
        # Initialize transcript analyzer (uses GroqAnalyzer by default)
        analyzer = TranscriptAnalyzer()
        analysis_dir = os.path.join(folders['video_dir'], "analysis")
        
        print(f"Processing {len(transcription_files)} transcript chunks for summaries, then final analysis...")
        llm_results = analyzer.analyze_transcript_chunks(transcription_files, analysis_dir)
        
        # Display cost summary
        cost_summary = analyzer.get_cost_summary()
        print(f"\n{'='*60}")
        print("LLM ANALYSIS COST SUMMARY")
        print(f"{'='*60}")
        print(f"Total chunks processed: {llm_results['total_chunks_processed']}")
        print(f"Total API calls: {cost_summary['total_calls']}")
        print(f"Successful calls: {cost_summary['successful_calls']}")
        print(f"Failed calls: {cost_summary['failed_calls']}")
        print(f"Total tokens: {cost_summary['total_tokens']:,}")
        print(f"Prompt tokens: {cost_summary['prompt_tokens']:,}")
        print(f"Completion tokens: {cost_summary['completion_tokens']:,}")
        print(f"Average tokens per call: {cost_summary['average_tokens_per_call']}")
        print(f"Actual usage calls: {cost_summary['actual_usage_calls']}")
        print(f"Estimated usage calls: {cost_summary['estimated_usage_calls']}")
        print(f"Total duration: {cost_summary['total_duration_seconds']}s")
        print(f"Model used: {cost_summary['model_used']}")
        print(f"\nCOST BREAKDOWN:")
        print(f"Input cost: ${cost_summary['input_cost_usd']:.6f}")
        print(f"Output cost: ${cost_summary['output_cost_usd']:.6f}")  
        print(f"Total cost: ${cost_summary['total_cost_usd']:.6f}")
        print(f"Pricing: {cost_summary['pricing']['input_per_million']}/1M input, {cost_summary['pricing']['output_per_million']}/1M output")
        
        # Display chunk processing summary
        print(f"\nCHUNK SUMMARIES:")
        print("-" * 20)
        for chunk_name, summary_data in llm_results['chunk_summaries'].items():
            status = "✓" if summary_data['summary'] else "✗"
            print(f"{chunk_name}: Summary {status}")
        
        final_status = "✓" if llm_results['final_analysis'] else "✗"
        print(f"Final Analysis: {final_status}")
        
    else:
        print("No transcription files found, skipping LLM analysis")
        llm_results = None
    
    print(f"\nProcessing complete!")
    print(f"All files saved in: {folders['video_dir']}")
    
    return {
        'video_id': video_id,
        'folders': folders,
        'audio_file': audio_file,
        'chunks': chunks,
        'transcriptions': transcription_files,
        'combined_transcript': combined_transcript,
        'metadata': metadata,
        'llm_analysis': llm_results
    }

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <youtube_url>")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    result = process_youtube_video(youtube_url)
    
    if not result:
        print("Processing failed")
        sys.exit(1)

if __name__ == "__main__":
    main()