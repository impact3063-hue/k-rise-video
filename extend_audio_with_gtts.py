#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extend audio.mp3 with gTTS for the final 3 phrases
Uses Google Text-to-Speech (free, no API key required)
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from gtts import gTTS
    from pydub import AudioSegment
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("ERROR: Required packages not installed.")
    print("Please install: pip install gtts pydub")
    sys.exit(1)


def generate_tts_segment(text, output_path, lang='ja', slow=False):
    """Generate TTS audio for a text segment using gTTS"""
    print(f"🎙️  Generating TTS for: {text}")
    
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(output_path)
    
    print(f"✅ Saved to: {output_path}")
    return output_path


def adjust_audio_speed(audio_path, speed_factor):
    """Adjust audio playback speed"""
    audio = AudioSegment.from_mp3(audio_path)
    
    # Change speed by changing frame rate
    new_frame_rate = int(audio.frame_rate * speed_factor)
    adjusted = audio._spawn(audio.raw_data, overrides={'frame_rate': new_frame_rate})
    adjusted = adjusted.set_frame_rate(audio.frame_rate)
    
    return adjusted


def merge_audio_files(original_audio, new_segments, output_path):
    """Merge original audio with new TTS segments using pydub"""
    print(f"🔧 Loading original audio: {original_audio}")
    combined = AudioSegment.from_mp3(original_audio)
    
    print(f"📊 Original audio duration: {len(combined)/1000:.2f} seconds")
    
    for segment_path in new_segments:
        print(f"🔧 Loading segment: {segment_path}")
        segment = AudioSegment.from_mp3(segment_path)
        print(f"   Segment duration: {len(segment)/1000:.2f} seconds")
        combined += segment
    
    print(f"🔧 Exporting merged audio to: {output_path}")
    combined.export(output_path, format="mp3", bitrate="192k")
    
    final_duration = len(combined) / 1000
    print(f"✅ Merged audio duration: {final_duration:.2f} seconds")
    
    return final_duration


def main():
    print("=" * 60)
    print("🎬 K-RISE Audio Extension with gTTS")
    print("=" * 60)
    
    # Define the missing phrases
    phrases = [
        "残された席はあとわずか！",
        "プロフィール欄のリンクをタップ！",
        "エントリーしよう！"
    ]
    
    # Generate TTS for each phrase
    segment_files = []
    for i, phrase in enumerate(phrases, 1):
        output_file = f"public/audio_segment_{i}.mp3"
        generate_tts_segment(phrase, output_file, lang='ja', slow=False)
        segment_files.append(output_file)
    
    print()
    print("=" * 60)
    print("🔧 Merging with original audio...")
    print("=" * 60)
    
    # Merge with original audio
    original_audio = "public/audio.mp3"
    final_output = "public/audio_extended.mp3"
    
    final_duration = merge_audio_files(original_audio, segment_files, final_output)
    
    # Clean up temporary segment files
    print()
    print("🧹 Cleaning up temporary files...")
    for segment_file in segment_files:
        if os.path.exists(segment_file):
            os.remove(segment_file)
            print(f"   Removed: {segment_file}")
    
    print()
    print("=" * 60)
    print("✅ SUCCESS!")
    print("=" * 60)
    print(f"Extended audio saved to: {final_output}")
    print(f"Final duration: {final_duration:.2f} seconds")
    print()
    print("Next steps:")
    print("1. Backup current audio: copy public\\audio.mp3 public\\audio.original.mp3")
    print("2. Replace with extended: copy public\\audio_extended.mp3 public\\audio.mp3")
    print("3. Update video-data-capcut-style.json if needed")
    print("4. Render video: npx remotion render KRiseTikTok5 out/k-rise-capcut-style.mp4 --overwrite")


if __name__ == "__main__":
    main()
