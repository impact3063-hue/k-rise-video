# -*- coding: utf-8 -*-
"""
CapCut-Style Phrase-Based Subtitle Generator
音声に完全連動する短いフレーズ表示用のタイムスタンプ生成

ナレーション内容:
"ダンス未経験でも世界へ行ける。条件はただ一つ、毎日鏡の前に立つこと。
才能は言い訳にならない、本気の覚悟が君を変える！
残された席はあとわずか！今すぐ公式LINEからエントリーしよう！"
"""

import json
import sys

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

FPS = 30
OUTPUT_JSON = "public/video-data-capcut-style.json"

# CapCut風フレーズ分割（2〜5文字の短いフレーズ）
# 実際の音声タイミングに基づいて調整
PHRASES = [
    # セグメント1: 0-3秒 (0-90フレーム)
    {"text": "ダンス", "startFrame": 3, "endFrame": 18},
    {"text": "未経験でも", "startFrame": 18, "endFrame": 45},
    {"text": "世界へ", "startFrame": 48, "endFrame": 64},
    {"text": "行ける。", "startFrame": 64, "endFrame": 87},
    
    # セグメント2: 3-6秒 (90-180フレーム)
    {"text": "条件は", "startFrame": 93, "endFrame": 108},
    {"text": "ただ一つ", "startFrame": 108, "endFrame": 126},
    {"text": "毎日", "startFrame": 129, "endFrame": 141},
    {"text": "鏡の前に", "startFrame": 141, "endFrame": 159},
    {"text": "立つこと。", "startFrame": 159, "endFrame": 177},
    
    # セグメント3: 6-9秒 (180-270フレーム)
    {"text": "才能は", "startFrame": 183, "endFrame": 198},
    {"text": "言い訳に", "startFrame": 198, "endFrame": 213},
    {"text": "ならない", "startFrame": 213, "endFrame": 228},
    {"text": "本気の", "startFrame": 228, "endFrame": 243},
    {"text": "覚悟が", "startFrame": 243, "endFrame": 255},
    {"text": "君を変える！", "startFrame": 255, "endFrame": 270},
    
    # セグメント4: 9-14秒 (270-420フレーム)
    {"text": "残された", "startFrame": 273, "endFrame": 288},
    {"text": "席は", "startFrame": 288, "endFrame": 297},
    {"text": "あとわずか！", "startFrame": 297, "endFrame": 321},
    {"text": "今すぐ", "startFrame": 327, "endFrame": 345},
    {"text": "公式LINE", "startFrame": 345, "endFrame": 381},
    {"text": "から", "startFrame": 381, "endFrame": 390},
    {"text": "エントリー", "startFrame": 390, "endFrame": 408},
    {"text": "しよう！", "startFrame": 408, "endFrame": 420},
]

def generate_capcut_json():
    """CapCut風フレーズベースのJSON生成"""
    
    video_data = {
        "version": "10.0.0-capcut-style",
        "metadata": {
            "projectId": "K-RISE-TikTok-CapCut-Style",
            "title": "K-RISE Dance Project - CapCut Style Phrases",
            "fps": FPS,
            "duration": 14.0,
            "totalFrames": 420,
            "displayMode": "phrase-by-phrase",
            "description": "Short phrases appear in sync with audio pronunciation"
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
        "phrases": PHRASES,
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
    
    print("=" * 60)
    print("CapCut-Style Phrase Generator")
    print("=" * 60)
    print(f"✅ Generated: {OUTPUT_JSON}")
    print(f"📊 Total phrases: {len(PHRASES)}")
    print("\nPhrase breakdown:")
    
    for i, phrase in enumerate(PHRASES, 1):
        duration_frames = phrase["endFrame"] - phrase["startFrame"]
        duration_sec = duration_frames / FPS
        print(f"  {i:2d}. '{phrase['text']}' - {phrase['startFrame']:3d}f → {phrase['endFrame']:3d}f ({duration_sec:.2f}s)")
    
    print("\n🎬 Next step:")
    print("  1. Create KRiseTikTok5.tsx component")
    print("  2. npx remotion render KRiseTikTok5 out/k-rise-capcut-style.mp4")


if __name__ == "__main__":
    generate_capcut_json()
