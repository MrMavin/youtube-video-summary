import os
import json
import time
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from prompts import (
    render_system_prompt, 
    render_preprocessing_prompt, 
    render_final_system_prompt
)
from utils import file_exists

load_dotenv()

class GroqAnalyzer:
    def __init__(self):
        """Initialize Groq client for content analysis"""
        self.client = self._initialize_client()
        self.model = "openai/gpt-oss-120b"
        self.cost_metadata = []
        
        # Pricing for openai/gpt-oss-120b model
        self.input_price_per_million = 0.15  # $0.15 per 1M input tokens
        self.output_price_per_million = 0.75  # $0.75 per 1M output tokens
    
    def _initialize_client(self):
        """Initialize Groq client with API key"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        return Groq(api_key=api_key)
    
    def _make_api_call(self, system_prompt, user_prompt, temperature=1, max_tokens=8192, call_type="analysis"):
        """Make API call to Groq with streaming response and cost tracking"""
        start_time = time.time()
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=1,
                reasoning_effort="medium",
                stream=True,
                stop=None
            )
            
            # Collect streaming response and usage metadata
            full_response = ""
            usage_info = None
            
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                print(content, end="", flush=True)
                
                # Try to get usage info from the final chunk
                if hasattr(chunk, 'usage') and chunk.usage:
                    usage_info = chunk.usage
            
            print()  # New line after streaming
            
            # Track cost metadata with actual usage if available
            end_time = time.time()
            
            cost_entry = {
                "timestamp": datetime.now().isoformat(),
                "call_type": call_type,
                "model": self.model,
                "duration_seconds": round(end_time - start_time, 2),
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Add actual token usage if available, otherwise use estimates
            if usage_info:
                cost_entry.update({
                    "prompt_tokens": usage_info.prompt_tokens,
                    "completion_tokens": usage_info.completion_tokens,
                    "total_tokens": usage_info.total_tokens,
                    "usage_source": "actual"
                })
            else:
                # Fallback to estimates
                input_tokens_est = len(system_prompt.split()) + len(user_prompt.split())
                output_tokens_est = len(full_response.split())
                cost_entry.update({
                    "prompt_tokens_estimate": input_tokens_est,
                    "completion_tokens_estimate": output_tokens_est,
                    "total_tokens_estimate": input_tokens_est + output_tokens_est,
                    "usage_source": "estimate"
                })
            
            self.cost_metadata.append(cost_entry)
            return full_response
            
        except Exception as e:
            print(f"Error making API call: {e}")
            # Still track failed calls
            cost_entry = {
                "timestamp": datetime.now().isoformat(),
                "call_type": call_type,
                "model": self.model,
                "error": str(e),
                "duration_seconds": round(time.time() - start_time, 2)
            }
            self.cost_metadata.append(cost_entry)
            return None
    
    def preprocessing_analysis(self, transcript_content, output_file=None):
        """Perform preprocessing analysis - simple transcript summarization"""
        if output_file and file_exists(output_file):
            print(f"Preprocessing analysis already exists: {output_file}")
            with open(output_file, 'r') as f:
                return f.read()
        
        # Render simplified prompts
        system_prompt = render_system_prompt()
        user_prompt = render_preprocessing_prompt(transcript_content)
        
        print(f"\n{'='*60}")
        print("PREPROCESSING ANALYSIS")
        print(f"{'='*60}")
        print(f"Making API call to {self.model}...")
        print("-" * 60)
        
        # Make API call
        response = self._make_api_call(system_prompt, user_prompt, call_type="preprocessing")
        
        # Save response if output file specified
        if output_file and response:
            with open(output_file, 'w') as f:
                f.write(response)
            print(f"\nPreprocessing analysis saved: {output_file}")
        
        return response
    
    def final_processing_analysis(self, all_summaries, output_file=None):
        """Perform final processing analysis using all chunk summaries"""
        if output_file and file_exists(output_file):
            print(f"Final analysis already exists: {output_file}")
            with open(output_file, 'r') as f:
                return f.read()
        
        # System prompt: final processing instructions, User prompt: all summaries
        system_prompt = render_final_system_prompt()
        user_prompt = all_summaries
        
        print(f"\n{'='*60}")
        print("FINAL PROCESSING ANALYSIS")
        print(f"{'='*60}")
        print(f"Making API call to {self.model}...")
        print("-" * 60)
        
        # Make API call
        response = self._make_api_call(system_prompt, user_prompt, call_type="final_processing")
        
        # Save response if output file specified
        if output_file and response:
            with open(output_file, 'w') as f:
                f.write(response)
            print(f"\nFinal analysis saved: {output_file}")
        
        return response
    
    def analyze_transcript_complete(self, transcript_content, analysis_dir=None):
        """Complete analysis pipeline: preprocessing + final processing"""
        results = {}
        
        # Set up output files if analysis directory provided
        preprocessing_file = None
        final_file = None
        if analysis_dir:
            os.makedirs(analysis_dir, exist_ok=True)
            preprocessing_file = os.path.join(analysis_dir, "preprocessing_analysis.txt")
            final_file = os.path.join(analysis_dir, "final_analysis.txt")
        
        # Step 1: Preprocessing analysis (summarize transcript)
        preprocessing_results = self.preprocessing_analysis(
            transcript_content, preprocessing_file
        )
        results['preprocessing'] = preprocessing_results
        
        if not preprocessing_results:
            print("Preprocessing failed, skipping final analysis")
            return results
        
        # Step 2: Final processing analysis (detailed summary from preprocessing)
        final_results = self.final_processing_analysis(
            preprocessing_results, final_file
        )
        results['final_analysis'] = final_results
        results['cost_metadata'] = self.cost_metadata
        
        # Save cost metadata if analysis directory provided
        if analysis_dir and self.cost_metadata:
            cost_file = os.path.join(analysis_dir, "cost_metadata.json")
            with open(cost_file, 'w') as f:
                json.dump(self.cost_metadata, f, indent=2)
            print(f"\nCost metadata saved: {cost_file}")
        
        return results
    
    
    def save_cost_metadata(self, output_file):
        """Save cost metadata to file"""
        with open(output_file, 'w') as f:
            json.dump(self.cost_metadata, f, indent=2)
        print(f"Cost metadata saved: {output_file}")
    
    def calculate_cost(self, prompt_tokens, completion_tokens):
        """Calculate cost based on token usage and pricing"""
        input_cost = (prompt_tokens / 1_000_000) * self.input_price_per_million
        output_cost = (completion_tokens / 1_000_000) * self.output_price_per_million
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6), 
            "total_cost": round(total_cost, 6)
        }
    
    def get_cost_summary(self):
        """Get summary of costs from metadata"""
        if not self.cost_metadata:
            return {"message": "No API calls made yet"}
        
        total_calls = len(self.cost_metadata)
        successful_calls = [call for call in self.cost_metadata if "error" not in call]
        failed_calls = total_calls - len(successful_calls)
        
        if successful_calls:
            # Try to get actual token usage first, fall back to estimates
            total_tokens = 0
            prompt_tokens = 0
            completion_tokens = 0
            actual_usage_calls = 0
            
            for call in successful_calls:
                if call.get("usage_source") == "actual":
                    total_tokens += call.get("total_tokens", 0)
                    prompt_tokens += call.get("prompt_tokens", 0)
                    completion_tokens += call.get("completion_tokens", 0)
                    actual_usage_calls += 1
                else:
                    # Use estimates if actual not available
                    total_tokens += call.get("total_tokens_estimate", 0)
                    prompt_tokens += call.get("prompt_tokens_estimate", 0)
                    completion_tokens += call.get("completion_tokens_estimate", 0)
            
            total_duration = sum(call.get("duration_seconds", 0) for call in successful_calls)
            avg_tokens = total_tokens / len(successful_calls) if successful_calls else 0
            
            # Calculate costs
            cost_breakdown = self.calculate_cost(prompt_tokens, completion_tokens)
        else:
            total_tokens = prompt_tokens = completion_tokens = avg_tokens = total_duration = actual_usage_calls = 0
            cost_breakdown = {"input_cost": 0, "output_cost": 0, "total_cost": 0}
        
        return {
            "total_calls": total_calls,
            "successful_calls": len(successful_calls),
            "failed_calls": failed_calls,
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "average_tokens_per_call": round(avg_tokens, 1),
            "total_duration_seconds": round(total_duration, 2),
            "actual_usage_calls": actual_usage_calls,
            "estimated_usage_calls": len(successful_calls) - actual_usage_calls,
            "model_used": self.model,
            "input_cost_usd": cost_breakdown["input_cost"],
            "output_cost_usd": cost_breakdown["output_cost"], 
            "total_cost_usd": cost_breakdown["total_cost"],
            "pricing": {
                "input_per_million": f"${self.input_price_per_million}",
                "output_per_million": f"${self.output_price_per_million}"
            }
        }