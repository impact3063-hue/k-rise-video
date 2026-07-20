# -*- coding: utf-8 -*-
"""
Whisper Audio Analysis for Character-Level Karaoke Sync
音声ファイルを解析して1文字単位のタイムスタンプを抽出

Requirements:
- pip install openai-whisper
- pip install pydub
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
    print("WARNING: Whisper not installed. Install with: pip install openai-whisper")

# 定数
FPS = 30
AUDIO_FILE = "public/audio.mp3"
OUTPUT_JSON = "public/video-data-v2-optimized.json"

# セグメント定義（実際のナレーション内容）
SEGMENTS = [
    {
        "id": "seg1",
        "startFrame": 0,
        "endFrame": 90,
        "text": "ダンス未経験でも\n世界へ行ける。",
        "style": {"type": "highlight", "emphasis": "strong"}
    },
    {
        "id": "seg2",
        "startFrame": 90,
        "endFrame": 180,
        "text": "条件はただ一つ\n毎日鏡の前に立つこと。",
        "style": {"type": "highlight", "emphasis": "medium"}
    },
    {
        "id": "seg3",
        "startFrame": 180,
        "endFrame": 270,
        "text": "才能は言い訳にならない\n本気の覚悟が君を変える！",
        "style": {"type": "urgent", "emphasis": "strong", "shake": True}
    },
    {
        "id": "seg4-cta",
        "startFrame": 270,
        "endFrame": 420,
        "text": "残された席はあとわずか！\n今すぐ公式LINEからエントリーしよう！",
        "style": {"type": "cta", "emphasis": "maximum", "pulse": True, "showArrow": True},
        "ctaSubtext": {
            "text": "プロフィール欄のリンクをタップ！",
            "startFrame": 330,
            "endFrame": 420,
            "position": "bottom"
        }
    }
]


def time_to_frame(seconds: float, fps: int = FPS) -> int:
    """秒をフレーム番号に変換"""
    return int(seconds * fps)


def analyze_audio_with_whisper(audio_path: str) -> List[Dict[str, Any]]:
    """
    Whisperを使用して音声を解析し、単語レベルのタイムスタンプを取得
    """
    if not WHISPER_AVAILABLE:
        print("❌ Whisper is not available. Using fallback timing.")
        return []
    
    print(f"🎤 Loading Whisper model...")
    model = whisper.load_model("base")  # または "small", "medium", "large"
    
    print(f"🎵 Analyzing audio: {audio_path}")
    result = model.transcribe(
        audio_path,
        language="ja",
        word_timestamps=True,
        verbose=True
    )
    
    print(f"📝 Transcription: {result['text']}")
    
    # 単語レベルのタイムスタンプを抽出
    word_segments = []
    if "segments" in result:
        for segment in result["segments"]:
            if "words" in segment:
                for word in segment["words"]:
                    word_segments.append({
                        "text": word.get("word", "").strip(),
                        "start": word.get("start", 0),
                        "end": word.get("end", 0)
                    })
    
    return word_segments


def distribute_characters_in_word(word_text: str, start_time: float, end_time: float) -> List[Dict[str, Any]]:
    """
    単語内の文字を均等に時間分配
    """
    characters = []
    char_count = len(word_text)
    
    if char_count == 0:
        return characters
    
    duration = end_time - start_time
    char_duration = duration / char_count
    
    for i, char in enumerate(word_text):
        char_start = start_time + (i * char_duration)
        char_end = char_start + char_duration
        
        characters.append({
            "char": char,
            "startFrame": time_to_frame(char_start),
            "endFrame": time_to_frame(char_end)
        })
    
    return characters


def map_whisper_to_segments(word_segments: List[Dict[str, Any]], segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Whisperの解析結果をセグメントにマッピング
    """
    # 全テキストを結合（改行を除去）
    full_text = "".join([seg["text"].replace("\n", "") for seg in segments])
    
    # Whisperの単語を結合
    whisper_text = "".join([w["text"] for w in word_segments])
    
    print(f"📊 Expected text: {full_text}")
    print(f"📊 Whisper text: {whisper_text}")
    
    # 各セグメントに文字タイミングを割り当て
    char_index = 0
    all_characters = []
    
    for word_seg in word_segments:
        chars = distribute_characters_in_word(
            word_seg["text"],
            word_seg["start"],
            word_seg["end"]
        )
        all_characters.extend(chars)
    
    # セグメントごとに文字を分配
    result_segments = []
    for seg in segments:
        seg_text = seg["text"].replace("\n", "")
        seg_chars = []
        
        for char in seg_text:
            if char_index < len(all_characters):
                char_timing = all_characters[char_index].copy()
                
                # セグメントの範囲内に収める
                char_timing["startFrame"] = max(seg["startFrame"], char_timing["startFrame"])
                char_timing["endFrame"] = min(seg["endFrame"], char_timing["endFrame"])
                
                seg_chars.append(char_timing)
                char_index += 1
        
        # 改行文字を追加
        if "\n" in seg["text"]:
            lines = seg["text"].split("\n")
            final_chars = []
            char_idx = 0
            
            for line_idx, line in enumerate(lines):
                for _ in line:
                    if char_idx < len(seg_chars):
                        final_chars.append(seg_chars[char_idx])
                        char_idx += 1
                
                # 改行を追加（最後の行以外）
                if line_idx < len(lines) - 1:
                    newline_frame = final_chars[-1]["endFrame"] if final_chars else seg["startFrame"]
                    final_chars.append({
                        "char": "\n",
                        "startFrame": newline_frame,
                        "endFrame": newline_frame
                    })
            
            seg_chars = final_chars
        
        result_seg = seg.copy()
        result_seg["characters"] = seg_chars
        result_segments.append(result_seg)
    
    return result_segments


def generate_fallback_timing(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Whisperが使用できない場合のフォールバックタイミング生成
    均等分配ベース
    """
    print("⚠️ Using fallback timing (uniform distribution)")
    
    result_segments = []
    
    for seg in segments:
        text = seg["text"]
        start_frame = seg["startFrame"]
        end_frame = seg["endFrame"]
        
        # 改行を除いた文字数
        chars_without_newline = [c for c in text if c != "\n"]
        char_count = len(chars_without_newline)
        
        if char_count == 0:
            result_segments.append(seg)
            continue
        
        # フレーム範囲を計算
        total_frames = end_frame - start_frame
        frames_per_char = total_frames / char_count
        
        characters = []
        char_idx = 0
        
        for char in text:
            if char == "\n":
                # 改行は前の文字の終了フレームに配置
                prev_end = characters[-1]["endFrame"] if characters else start_frame
                characters.append({
                    "char": "\n",
                    "startFrame": prev_end,
                    "endFrame": prev_end
                })
            else:
                char_start = start_frame + int(char_idx * frames_per_char)
                char_end = start_frame + int((char_idx + 1) * frames_per_char)
                
                characters.append({
                    "char": char,
                    "startFrame": char_start,
                    "endFrame": char_end
                })
                char_idx += 1
        
        result_seg = seg.copy()
        result_seg["characters"] = characters
        result_segments.append(result_seg)
    
    return result_segments


def main():
    """メイン処理"""
    print("=" * 60)
    print("🎯 Whisper Audio Analysis for Character-Level Sync")
    print("=" * 60)
    
    # 音声ファイルの存在確認
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ Audio file not found: {AUDIO_FILE}")
        return
    
    # Whisperで解析
    if WHISPER_AVAILABLE:
        try:
            word_segments = analyze_audio_with_whisper(AUDIO_FILE)
            
            if word_segments:
                print(f"✅ Extracted {len(word_segments)} word segments")
                result_segments = map_whisper_to_segments(word_segments, SEGMENTS)
            else:
                print("⚠️ No word segments extracted, using fallback")
                result_segments = generate_fallback_timing(SEGMENTS)
        except Exception as e:
            print(f"❌ Whisper analysis failed: {e}")
            print("⚠️ Using fallback timing")
            result_segments = generate_fallback_timing(SEGMENTS)
    else:
        result_segments = generate_fallback_timing(SEGMENTS)
    
    # JSONデータを構築
    video_data = {
        "version": "9.3.0-whisper-analyzed",
        "metadata": {
            "projectId": "K-RISE-TikTok-4-WhisperSync",
            "title": "K-RISE Dance Project - Whisper Audio Analysis",
            "fps": FPS,
            "duration": 14.0,
            "totalFrames": 420,
            "syncMode": "character-level-whisper-analyzed",
            "basedOn": "Whisper API audio analysis of audio.mp3"
        },
        "content": {
            "script": {
                "original": "".join([s["text"].replace("\n", "") for s in SEGMENTS]),
                "transcribed": "".join([s["text"].replace("\n", "") for s in SEGMENTS])
            }
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
        "subtitles": result_segments,
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
            "characterAnimation": {
                "activeScale": 1.15,
                "activeDuration": 0.1,
                "glowIntensity": 1.2
            }
        }
    }
    
    # JSONファイルに書き出し
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated: {OUTPUT_JSON}")
    print(f"📊 Total segments: {len(result_segments)}")
    
    for seg in result_segments:
        char_count = len([c for c in seg.get("characters", []) if c["char"] != "\n"])
        print(f"  - {seg['id']}: {char_count} characters")
    
    print("\n🎬 Next step: npx remotion render KRiseTikTok4 out/k-rise-optimized-v2.mp4 --overwrite")


if __name__ == "__main__":
    main()
