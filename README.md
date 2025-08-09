# youtube-video-summary

Get a summary for youtube videos

⚠️ **Work in Progress** - This project is currently under development and may not be fully functional yet.

## What it does

This Python tool processes YouTube videos to create AI-powered summaries and analysis. It downloads the audio from a YouTube video, splits it into manageable chunks, transcribes the speech to text, and then uses AI (via Groq) to generate summaries and comprehensive analysis.

## How it works

1. **Download**: Uses `yt-dlp` to download high-quality audio from YouTube videos as FLAC files
2. **Split**: Automatically splits large audio files into smaller chunks (max 18MB each) for processing
3. **Transcribe**: Uses Groq's Whisper model to transcribe each audio chunk to text
4. **Analyze**: Processes transcripts with AI to generate:
   - Individual chunk summaries  
   - Final comprehensive analysis combining all content
   - Cost tracking and metadata

## Requirements

- Python 3.x
- `yt-dlp` and `ffmpeg` installed on your system
- Groq API key (set as `GROQ_API_KEY` environment variable)

Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py <youtube_url>
```

Example:
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Output

The tool creates a folder structure for each video with:
- `/audio/` - Original downloaded audio
- `/chunks/` - Split audio segments  
- `/transcripts/` - Text transcriptions of each chunk
- `/analysis/` - AI-generated summaries and analysis
- Metadata about file sizes, durations, and processing costs

*Built with [Claude Code](https://claude.ai/code)*
