import os
from groq_client import GroqAnalyzer
from utils import file_exists

class TranscriptAnalyzer:
    """High-level analysis orchestrator that uses any LLM client"""
    
    def __init__(self, llm_client=None):
        """Initialize with an LLM client (defaults to GroqAnalyzer)"""
        self.llm_client = llm_client or GroqAnalyzer()
    
    def analyze_transcript_chunks(self, transcription_files, analysis_dir=None):
        """Analyze transcript chunks: summaries + final analysis"""
        chunk_summaries = []
        chunk_results = {}
        
        if analysis_dir:
            os.makedirs(analysis_dir, exist_ok=True)
        
        # Step 1: Process each chunk individually to get summaries
        for i, transcript_file in enumerate(sorted(transcription_files), 1):
            if not file_exists(transcript_file):
                print(f"Transcript file not found: {transcript_file}")
                continue
            
            # Read transcript content
            with open(transcript_file, 'r') as f:
                chunk_content = f.read().strip()
            
            if not chunk_content:
                print(f"Empty transcript file: {transcript_file}")
                continue
            
            chunk_name = f"chunk_{i:02d}"
            print(f"\n{'='*50}")
            print(f"PROCESSING {chunk_name.upper()} SUMMARY")
            print(f"{'='*50}")
            
            # Set up output file for this chunk summary
            summary_file = None
            if analysis_dir:
                summary_file = os.path.join(analysis_dir, f"{chunk_name}_summary.txt")
            
            # Get summary for this chunk using the LLM client
            chunk_summary = self.llm_client.preprocessing_analysis(chunk_content, summary_file)
            
            if chunk_summary:
                chunk_summaries.append(f"Chunk {i} Summary:\n{chunk_summary}")
                chunk_results[chunk_name] = {
                    'summary': chunk_summary,
                    'source_file': transcript_file
                }
        
        # Step 2: Final analysis with all summaries combined
        final_analysis = None
        if chunk_summaries:
            print(f"\n{'='*60}")
            print("FINAL ANALYSIS WITH ALL SUMMARIES")
            print(f"{'='*60}")
            
            all_summaries_text = "\n\n".join(chunk_summaries)
            final_file = os.path.join(analysis_dir, "final_analysis.txt") if analysis_dir else None
            
            final_analysis = self.llm_client.final_processing_analysis(all_summaries_text, final_file)
        
        # Save cost metadata if the client supports it
        if hasattr(self.llm_client, 'cost_metadata') and analysis_dir and self.llm_client.cost_metadata:
            cost_file = os.path.join(analysis_dir, "cost_metadata.json")
            self.llm_client.save_cost_metadata(cost_file)
        
        return {
            'chunk_summaries': chunk_results,
            'final_analysis': final_analysis,
            'total_chunks_processed': len(chunk_summaries),
            'llm_client': type(self.llm_client).__name__
        }
    
    def get_cost_summary(self):
        """Get cost summary if the LLM client supports it"""
        if hasattr(self.llm_client, 'get_cost_summary'):
            return self.llm_client.get_cost_summary()
        else:
            return {"message": "Cost tracking not supported by this LLM client"}
    
    def analyze_single_text(self, text, output_file=None):
        """Analyze a single piece of text (useful for testing or simple analysis)"""
        return self.llm_client.preprocessing_analysis(text, output_file)