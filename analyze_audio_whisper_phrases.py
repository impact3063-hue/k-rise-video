# -*- coding: utf-8 -*-
"""
Whisper Audio Analysis for CapCut-Style Phrase Timing
実音声波形からフレーズごとの正確なタイムスタンプを抽出

Requirements:
- pip install openai-whisper
- pip install torch torchvision torchaudio
"""

import json
import os
import sys
from typing import List, Dict, Any

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("ERROR: Whisper not installed. Install with: pip install openai-whisper")
    sys.exit(1)

# 定数
FPS = 30
AUDIO_FILE = "public/audio.mp3"
OUTPUT_JSON = "public/video-data-capcut-style.json"

# 期待されるフレーズ（順序通り）
EXPECTED_PHRASES = [
    "ダンス",
    "未経験でも",
    "世界へ",
    "行ける",
    "条件は",
    "ただ一つ",
    "毎日",
    "鏡の前に",
    "立つこと",
    "才能は",
    "言い訳に",
    "ならない",
    "本気の",
    "覚悟が",
    "君を変える",
    "残された",
    "席は",
    "あとわずか",
    "今すぐ",
    "公式LINE",
    "から",
    "エントリー",
    "しよう"
]


def time_to_frame(seconds: float, fps: int = FPS) -> int:
    """秒をフレーム番号に変換（ミリ秒精度）"""
    return round(seconds * fps)


def analyze_audio_with_whisper(audio_path: str) -> List[Dict[str, Any]]:
    """
    Whisperを使用して音声を解析し、単語レベルのタイムスタンプを取得
    """
    print("=" * 70)
    print("Whisper Audio Analysis - Phrase-Level Timing Extraction")
    print("=" * 70)
    print(f"\nLoading Whisper model (base)...")
    
    model = whisper.load_model("base")
    
    print(f"Analyzing audio: {audio_path}")
    print("This may take a few minutes...\n")
    
    result = model.transcribe(
        audio_path,
        language="ja",
        word_timestamps=True,
        verbose=False
    )
    
    print(f"Transcription: {result['text']}\n")
    
    # 単語レベルのタイムスタンプを抽出
    word_segments = []
    if "segments" in result:
        for segment in result["segments"]:
            if "words" in segment:
                for word in segment["words"]:
                    word_text = word.get("word", "").strip()
                    if word_text:
                        word_segments.append({
                            "text": word_text,
                            "start": word.get("start", 0),
                            "end": word.get("end", 0),
                            "startFrame": time_to_frame(word.get("start", 0)),
                            "endFrame": time_to_frame(word.get("end", 0))
                        })
    
    print(f"Extracted {len(word_segments)} word segments:\n")
    for i, word in enumerate(word_segments, 1):
        print(f"  {i:2d}. '{word['text']}' - {word['start']:.3f}s → {word['end']:.3f}s "
              f"(Frame {word['startFrame']} → {word['endFrame']})")
    
    return word_segments


def map_words_to_phrases(word_segments: List[Dict[str, Any]], expected_phrases: List[str]) -> List[Dict[str, Any]]:
    """
    Whisperの単語セグメントを期待されるフレーズにマッピング
    """
    print("\n" + "=" * 70)
    print("Mapping Words to Phrases")
    print("=" * 70 + "\n")
    
    phrases = []
    word_index = 0
    
    for phrase_text in expected_phrases:
        # フレーズの文字数
        phrase_chars = [c for c in phrase_text if c not in ["。", "！", "？"]]
        phrase_len = len(phrase_chars)
        
        # このフレーズに対応する単語を収集
        phrase_words = []
        chars_collected = 0
        
        while word_index < len(word_segments) and chars_collected < phrase_len:
            word = word_segments[word_index]
            phrase_words.append(word)
            # 句読点を除いた文字数をカウント
            word_chars = [c for c in word["text"] if c not in ["。", "！", "？", "、"]]
            chars_collected += len(word_chars)
            word_index += 1
        
        if phrase_words:
            # フレーズの開始は最初の単語の開始
            # フレーズの終了は最後の単語の終了
            start_frame = phrase_words[0]["startFrame"]
            end_frame = phrase_words[-1]["endFrame"]
            
            phrases.append({
                "text": phrase_text,
                "startFrame": start_frame,
                "endFrame": end_frame,
                "words": [w["text"] for w in phrase_words],
                "duration_sec": (end_frame - start_frame) / FPS
            })
            
            print(f"Phrase: '{phrase_text}'")
            print(f"  Words: {' + '.join([w['text'] for w in phrase_words])}")
            print(f"  Timing: Frame {start_frame} → {end_frame} ({(end_frame - start_frame) / FPS:.2f}s)")
            print()
        else:
            print(f"WARNING: No words found for phrase '{phrase_text}'")
    
    return phrases


def generate_capcut_json_with_whisper(phrases: List[Dict[str, Any]]):
    """
    Whisper解析結果を使用してCapCut風JSONを生成
    """
    video_data = {
        "version": "10.1.0-whisper-accurate",
        "metadata": {
            "projectId": "K-RISE-TikTok-CapCut-Whisper",
            "title": "K-RISE Dance Project - Whisper-Accurate Timing",
            "fps": FPS,
            "duration": 14.0,
            "totalFrames": 420,
            "displayMode": "phrase-by-phrase",
            "description": "Phrases synced with actual audio using Whisper analysis",
            "timingSource": "Whisper word-level timestamps"
        },
        "audio": {
            "narration": {
                "file": "audio.mp3",
                "volume": 0.8
            },
            "bgm": {
                "file": "bg-music.mp3",
                "volume": 0.3,
                "loop": True
            }
        },
        "phrases": [
            {
                "text": p["text"],
                "startFrame": p["startFrame"],
                "endFrame": p["endFrame"]
            }
            for p in phrases
        ],
        "visualEffects": {
            "background": {
                "kenBurns": {
                    "enabled": True,
                    "zoomFrom": 1.0,
                    "zoomTo": 1.15,
                    "duration": 420
                },
                "neonPulse": {
                    "enabled": True,
                    "color": "#FFD700",
                    "intensity": 0.3,
                    "speed": 2.0
                }
            },
            "phraseAnimation": {
                "popInScale": 1.1,
                "fadeInFrames": 5,
                "fadeOutFrames": 5,
                "glowColor": "#FFD700",
                "glowIntensity": 1.5
            }
        },
        "cta": {
            "text": "プロフィール欄のリンクをタップ！",
            "startFrame": 330,
            "endFrame": 420,
            "showArrow": True
        }
    }
    
    # JSONファイルに書き出し
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print("JSON Generation Complete")
    print("=" * 70)
    print(f"\nGenerated: {OUTPUT_JSON}")
    print(f"Total phrases: {len(phrases)}")
    print(f"Timing source: Whisper word-level timestamps")
    print(f"Frame accuracy: 1/{FPS} second (33.33ms)")
    
    print("\nPhrase timing summary:")
    for i, phrase in enumerate(phrases, 1):
        print(f"  {i:2d}. '{phrase['text']}' - "
              f"Frame {phrase['startFrame']:3d} → {phrase['endFrame']:3d} "
              f"({phrase['duration_sec']:.2f}s)")
    
    print("\nNext step:")
    print("  npx remotion render KRiseTikTok5 out/k-rise-capcut-style.mp4 --overwrite")


def main():
    """メイン処理"""
    if not WHISPER_AVAILABLE:
        print("ERROR: Whisper is required for this script")
        return
    
    # 音声ファイルの存在確認
    if not os.path.exists(AUDIO_FILE):
        print(f"ERROR: Audio file not found: {AUDIO_FILE}")
        return
    
    try:
        # Whisperで解析
        word_segments = analyze_audio_with_whisper(AUDIO_FILE)
        
        if not word_segments:
            print("ERROR: No word segments extracted from audio")
            return
        
        # 単語をフレーズにマッピング
        phrases = map_words_to_phrases(word_segments, EXPECTED_PHRASES)
        
        if not phrases:
            print("ERROR: No phrases generated")
            return
        
        # JSONを生成
        generate_capcut_json_with_whisper(phrases)
        
        print("\nSUCCESS: Whisper analysis complete!")
        print("The timing data is now based on actual audio waveform analysis.")
        
    except Exception as e:
        print(f"\nERROR: Whisper analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
