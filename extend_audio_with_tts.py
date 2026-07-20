#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extend audio.mp3 with TTS for the final 3 phrases
Generates audio for:
- 残された席はあとわずか！
- プロフィール欄のリンクをタップ！
- エントリーしよう！
"""

import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

def generate_tts_segment(client, text, output_path, voice="alloy", model="tts-1"):
    """Generate TTS audio for a text segment"""
    print(f"🎙️  Generating TTS for: {text}")
    
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        speed=1.0
    )
    
    response.stream_to_file(output_path)
    print(f"✅ Saved to: {output_path}")


def merge_audio_files(original_audio, new_segments, output_path):
    """Merge original audio with new TTS segments using ffmpeg"""
    import subprocess
    
    # Create a concat file list
    concat_file = "public/concat_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        f.write(f"file '{os.path.basename(original_audio)}'\n")
        for segment in new_segments:
            f.write(f"file '{os.path.basename(segment)}'\n")
    
    # Use ffmpeg to concatenate
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_path
    ]
    
    print(f"🔧 Merging audio files...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ FFmpeg error: {result.stderr}")
        return False
    
    # Clean up concat file
    os.remove(concat_file)
    print(f"✅ Merged audio saved to: {output_path}")
    return True


def main():
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in .env file or environment variables.")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    # Define the missing phrases
    phrases = [
        "残された席はあとわずか！",
        "プロフィール欄のリンクをタップ！",
        "エントリーしよう！"
    ]
    
    # Combine all phrases into one for natural flow
    combined_text = "".join(phrases)
    
    print("=" * 60)
    print("🎬 K-RISE Audio Extension with OpenAI TTS")
    print("=" * 60)
    print(f"📝 Text to synthesize: {combined_text}")
    print()
    
    # Generate TTS for the combined ending
    tts_output = "public/audio_ending.mp3"
    generate_tts_segment(client, combined_text, tts_output, voice="alloy")
    
    print()
    print("=" * 60)
    print("🔧 Merging with original audio...")
    print("=" * 60)
    
    # Merge with original audio
    original_audio = "public/audio.mp3"
    final_output = "public/audio_extended.mp3"
    
    if merge_audio_files(original_audio, [tts_output], final_output):
        print()
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"Extended audio saved to: {final_output}")
        print()
        print("Next steps:")
        print("1. Backup current audio: copy public\\audio.mp3 public\\audio.original.mp3")
        print("2. Replace with extended: copy public\\audio_extended.mp3 public\\audio.mp3")
        print("3. Render video: npx remotion render KRiseTikTok5 out/k-rise-capcut-style.mp4 --overwrite")
        
        # Check duration
        import subprocess
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
             "-of", "default=noprint_wrappers=1:nokey=1", final_output],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            print(f"\n📊 Extended audio duration: {duration:.2f} seconds")
    else:
        print("❌ Failed to merge audio files")
        sys.exit(1)


if __name__ == "__main__":
    main()
