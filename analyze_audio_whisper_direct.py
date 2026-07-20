# -*- coding: utf-8 -*-
"""
Whisper Direct Transcription to Phrases
Whisperの認識結果をそのまま使用してフレーズを生成

Whisperが認識した単語を2〜5文字の自然なフレーズにグループ化
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


def time_to_frame(seconds: float, fps: int = FPS) -> int:
    """秒をフレーム番号に変換（ミリ秒精度）"""
    return round(seconds * fps)


def analyze_audio_with_whisper(audio_path: str) -> List[Dict[str, Any]]:
    """
    Whisperを使用して音声を解析し、単語レベルのタイムスタンプを取得
    """
    print("=" * 70)
    print("Whisper Direct Transcription Analysis")
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
    
    print(f"Full Transcription: {result['text']}\n")
    
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
    
    return word_segments, result['text']


def group_words_into_phrases(word_segments: List[Dict[str, Any]], max_chars: int = 5) -> List[Dict[str, Any]]:
    """
    単語を2〜5文字の自然なフレーズにグループ化
    """
    print("\n" + "=" * 70)
    print("Grouping Words into Natural Phrases (2-5 chars)")
    print("=" * 70 + "\n")
    
    phrases = []
    current_phrase_words = []
    current_char_count = 0
    
    for word in word_segments:
        word_text = word["text"]
        # 句読点を除いた文字数
        word_chars = [c for c in word_text if c not in ["。", "！", "？", "、", " "]]
        word_char_count = len(word_chars)
        
        # 現在のフレーズに追加するか判定
        if current_char_count == 0:
            # 新しいフレーズの開始
            current_phrase_words.append(word)
            current_char_count += word_char_count
        elif current_char_count + word_char_count <= max_chars:
            # 現在のフレーズに追加
            current_phrase_words.append(word)
            current_char_count += word_char_count
        else:
            # 現在のフレーズを確定して新しいフレーズを開始
            if current_phrase_words:
                phrase_text = "".join([w["text"] for w in current_phrase_words])
                phrases.append({
                    "text": phrase_text,
                    "startFrame": current_phrase_words[0]["startFrame"],
                    "endFrame": current_phrase_words[-1]["endFrame"],
                    "words": [w["text"] for w in current_phrase_words],
                    "duration_sec": (current_phrase_words[-1]["endFrame"] - current_phrase_words[0]["startFrame"]) / FPS
                })
            
            # 新しいフレーズを開始
            current_phrase_words = [word]
            current_char_count = word_char_count
    
    # 最後のフレーズを追加
    if current_phrase_words:
        phrase_text = "".join([w["text"] for w in current_phrase_words])
        phrases.append({
            "text": phrase_text,
            "startFrame": current_phrase_words[0]["startFrame"],
            "endFrame": current_phrase_words[-1]["endFrame"],
            "words": [w["text"] for w in current_phrase_words],
            "duration_sec": (current_phrase_words[-1]["endFrame"] - current_phrase_words[0]["startFrame"]) / FPS
        })
    
    print(f"Generated {len(phrases)} phrases:\n")
    for i, phrase in enumerate(phrases, 1):
        print(f"  {i:2d}. '{phrase['text']}'")
        print(f"      Words: {' + '.join(phrase['words'])}")
        print(f"      Timing: Frame {phrase['startFrame']} → {phrase['endFrame']} ({phrase['duration_sec']:.2f}s)")
        print()
    
    return phrases


def generate_capcut_json_with_whisper(phrases: List[Dict[str, Any]], full_transcription: str):
    """
    Whisper解析結果を使用してCapCut風JSONを生成
    """
    # 最後のフレーズの終了フレームを確認
    last_phrase_end = phrases[-1]["endFrame"] if phrases else 0
    
    # CTAの開始フレームを音声終了後に設定
    cta_start_frame = max(last_phrase_end + 30, 330)  # 音声終了後1秒、または330フレーム
    
    video_data = {
        "version": "10.2.0-whisper-direct",
        "metadata": {
            "projectId": "K-RISE-TikTok-CapCut-Whisper-Direct",
            "title": "K-RISE Dance Project - Whisper Direct Transcription",
            "fps": FPS,
            "duration": 14.0,
            "totalFrames": 420,
            "displayMode": "phrase-by-phrase",
            "description": "Phrases from actual Whisper transcription",
            "timingSource": "Whisper word-level timestamps (direct)",
            "fullTranscription": full_transcription
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
            "startFrame": cta_start_frame,
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
    print(f"Timing source: Whisper direct transcription")
    print(f"Frame accuracy: 1/{FPS} second (33.33ms)")
    print(f"Audio ends at: Frame {last_phrase_end}")
    print(f"CTA starts at: Frame {cta_start_frame}")
    
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
        word_segments, full_transcription = analyze_audio_with_whisper(AUDIO_FILE)
        
        if not word_segments:
            print("ERROR: No word segments extracted from audio")
            return
        
        # 単語を自然なフレーズにグループ化
        phrases = group_words_into_phrases(word_segments, max_chars=5)
        
        if not phrases:
            print("ERROR: No phrases generated")
            return
        
        # JSONを生成
        generate_capcut_json_with_whisper(phrases, full_transcription)
        
        print("\nSUCCESS: Whisper direct transcription complete!")
        print("The timing data is based on actual audio waveform analysis.")
        print("Phrases are generated from Whisper's actual transcription.")
        
    except Exception as e:
        print(f"\nERROR: Whisper analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
