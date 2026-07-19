# -*- coding: utf-8 -*-
"""
世界最高峰のデータ駆動型動画生成マスタースクリプト v3.2
Character-Level Audio-Driven Video Generation Pipeline with Proper Noun Preservation

このスクリプトは以下を完全自動化します：
1. 高品質音声生成（OpenAI TTS-1-HD）
2. 単語レベルの音声解析（Whisper API）
3. 固有名詞の自動識別と保護
4. 1文字単位の超精密タイムスタンプ生成
5. 固有名詞を尊重した文節・品詞境界を考慮したカラオケスタイルの字幕データ構造出力

v3.2 新機能:
- 固有名詞（K-RISE、BTS等）の完全保護システム
- 文脈的表現（「とは」等）との厳密な分離
- 固有名詞辞書による自動認識
- セグメント分割時の固有名詞境界尊重
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# Janome形態素解析器のインポート
try:
    from janome.tokenizer import Tokenizer
    JANOME_AVAILABLE = True
except ImportError:
    JANOME_AVAILABLE = False
    print("⚠️  Warning: Janome not installed. Falling back to simple segmentation.")

# 固有名詞パーサーのインポート
try:
    from proper_noun_parser import ProperNounParser
    PROPER_NOUN_PARSER_AVAILABLE = True
except ImportError:
    PROPER_NOUN_PARSER_AVAILABLE = False
    print("⚠️  Warning: ProperNounParser not available. Proper noun protection disabled.")

# 🎯 句読点完全除去システム - Guard A (データ前処理レイヤー)
PUNCTUATION_REGEX = re.compile(
    r'[、，,。．.・･！？!?…‥「」『』（）()【】［］\[\]〈〉《》〔〕｛｝\{\}〜～'
    r'\u3000-\u303F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]'
)

STRICT_PUNCTUATION_REGEX = re.compile(
    r'[、，,。．.・･\u3001\u3002\uFF0C\uFF0E\u30FB\uFF65]'
)


def clean_text_punctuation(text: str, strict: bool = True) -> str:
    """句読点を完全除去"""
    if not text:
        return ""
    regex = STRICT_PUNCTUATION_REGEX if strict else PUNCTUATION_REGEX
    return regex.sub("", text)


# Windows環境でのUnicode出力対応
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 環境変数の読み込み
load_dotenv()


def calculate_character_timestamps(
    words: List[Dict[str, Any]], 
    fps: int = 30
) -> List[Dict[str, Any]]:
    """
    🎯 1文字単位のタイムスタンプ計算
    """
    character_data = []
    
    for word in words:
        w_text = word.get("word", "").strip()
        w_start = word.get("start", 0.0)
        w_end = word.get("end", 0.0)
        
        if not w_text:
            continue
        
        char_count = len(w_text)
        word_duration = w_end - w_start
        
        if char_count > 0:
            char_duration = word_duration / char_count
        else:
            char_duration = 0
        
        for i, char in enumerate(w_text):
            char_start = w_start + (i * char_duration)
            char_end = char_start + char_duration
            
            char_start_frame = int(char_start * fps)
            char_end_frame = int(char_end * fps)
            
            # 🎯 Guard A: 句読点を完全除去（データ生成時）
            cleaned_char = clean_text_punctuation(char, strict=True)
            
            character_data.append({
                "char": cleaned_char,
                "startTime": round(char_start, 4),
                "endTime": round(char_end, 4),
                "startFrame": char_start_frame,
                "endFrame": char_end_frame,
                "duration": round(char_duration, 4),
                "wordIndex": len(character_data)
            })
    
    return character_data


def detect_phrase_boundaries_with_proper_nouns(
    text: str, 
    proper_noun_parser: Optional[Any] = None
) -> Tuple[List[int], List[Dict[str, Any]]]:
    """
    🎯 v3.2: 固有名詞を尊重した文節境界の検出
    
    Returns:
        (boundaries, proper_noun_positions)
    """
    # 固有名詞の位置を取得
    proper_noun_positions = []
    if proper_noun_parser and PROPER_NOUN_PARSER_AVAILABLE:
        proper_noun_positions = proper_noun_parser.identify_proper_nouns_in_text(text)
        print(f"   🎯 Protecting {len(proper_noun_positions)} proper nouns:")
        for pn in proper_noun_positions:
            print(f"      - '{pn['noun']}' @ position {pn['start']}-{pn['end']}")
    
    boundaries = []
    
    if not JANOME_AVAILABLE or not text:
        # Janomeが利用できない場合は句読点のみを境界とする
        for i, char in enumerate(text):
            if char in ["、", "。", "！", "？", "!", "?", " ", "　"]:
                # 固有名詞の内部でないことを確認
                is_inside_proper_noun = False
                for pn in proper_noun_positions:
                    if i >= pn["start"] and i < pn["end"]:
                        is_inside_proper_noun = True
                        break
                
                if not is_inside_proper_noun:
                    boundaries.append(i + 1)
        
        # 固有名詞の直後も境界として追加
        for pn in proper_noun_positions:
            boundaries.append(pn["end"])
        
        return sorted(list(set(boundaries))), proper_noun_positions
    
    # Janomeによる形態素解析
    tokenizer = Tokenizer()
    current_idx = 0
    
    try:
        tokens = list(tokenizer.tokenize(text))
        
        for token in tokens:
            surface = token.surface
            pos_info = token.part_of_speech.split(',')
            pos = pos_info[0] if pos_info else ""
            
            # 固有名詞の内部かチェック
            is_inside_proper_noun = False
            for pn in proper_noun_positions:
                if current_idx >= pn["start"] and current_idx < pn["end"]:
                    is_inside_proper_noun = True
                    break
            
            # 固有名詞の内部では境界を追加しない
            if not is_inside_proper_noun:
                if pos == "記号":
                    boundaries.append(current_idx + len(surface))
                elif pos in ['名詞', '動詞', '形容詞', '副詞', '接続詞', '感動詞']:
                    if current_idx > 0:
                        boundaries.append(current_idx)
                elif pos == '助詞' and current_idx > 0:
                    boundaries.append(current_idx)
            
            current_idx += len(surface)
        
        # 固有名詞の直後も境界として追加
        for pn in proper_noun_positions:
            boundaries.append(pn["end"])
        
    except Exception as e:
        print(f"⚠️  Morphological analysis warning: {e}")
        # エラー時は句読点のみを境界とする
        for i, char in enumerate(text):
            if char in ["、", "。", "！", "？", "!", "?", " ", "　"]:
                is_inside_proper_noun = False
                for pn in proper_noun_positions:
                    if i >= pn["start"] and i < pn["end"]:
                        is_inside_proper_noun = True
                        break
                
                if not is_inside_proper_noun:
                    boundaries.append(i + 1)
        
        for pn in proper_noun_positions:
            boundaries.append(pn["end"])
    
    return sorted(list(set(boundaries))), proper_noun_positions


def segment_text_by_phrase_with_proper_nouns(
    character_data: List[Dict[str, Any]],
    max_chars: int = 18,
    max_duration: float = 3.0,
    proper_noun_parser: Optional[Any] = None
) -> List[List[Dict[str, Any]]]:
    """
    🎯 v3.2: 固有名詞を保護したテキストセグメント分割
    🚨 緊急修正: 最大文字数を15-18文字に厳格化（スマホ縦画面対応）
    """
    if not character_data:
        return []
    
    # 全テキストを結合
    full_text = "".join([d["char"] for d in character_data])
    
    # 固有名詞を考慮した境界を検出
    boundaries, proper_noun_positions = detect_phrase_boundaries_with_proper_nouns(
        full_text, proper_noun_parser
    )
    
    print(f"   📊 Detected {len(boundaries)} phrase boundaries")
    
    segments = []
    current_segment = []
    segment_start_idx = 0
    
    for i, char_data in enumerate(character_data):
        char = char_data["char"]
        current_segment.append(char_data)
        current_length = len(current_segment)
        
        # 現在位置が境界かどうか
        is_boundary = (i + 1) in boundaries
        
        # 句読点の検出
        is_punctuation = char in ["、", "。", "！", "？", "!", "?"]
        
        # 現在のセグメントの継続時間
        if current_segment:
            segment_duration = char_data["endTime"] - current_segment[0]["startTime"]
        else:
            segment_duration = 0
        
        # 固有名詞の内部かチェック
        is_inside_proper_noun = False
        for pn in proper_noun_positions:
            if i >= pn["start"] and i < pn["end"]:
                is_inside_proper_noun = True
                break
        
        # 分割条件の判定（🚨 緊急修正: 18文字厳守）
        should_break = False
        
        # 条件1: 句読点（最優先、ただし固有名詞内部は除く）
        if is_punctuation and not is_inside_proper_noun:
            should_break = True
        
        # 条件2: 18文字に達し、かつ境界位置（固有名詞内部は除く）
        elif current_length >= max_chars and is_boundary and not is_inside_proper_noun:
            should_break = True
        
        # 条件3: 18文字を超過（緊急分割、ただし固有名詞内部は除く）
        # 🚨 修正: +3の猶予を削除し、18文字で厳格に分割
        elif current_length > max_chars and not is_inside_proper_noun:
            should_break = True
        
        # 条件4: 時間オーバー（固有名詞内部は除く）
        elif segment_duration > max_duration and not is_inside_proper_noun:
            should_break = True
        
        # セグメントを確定
        if should_break and current_segment:
            segments.append(current_segment)
            current_segment = []
            segment_start_idx = i + 1
    
    # 最後のセグメントを追加
    if current_segment:
        segments.append(current_segment)
    
    return segments


def build_karaoke_subtitles_with_proper_nouns(
    words: List[Dict[str, Any]],
    fps: int = 30,
    max_chars: int = 18,
    max_duration: float = 3.0,
    proper_noun_parser: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    🎤 カラオケスタイルの字幕生成（固有名詞保護版）
    🚨 緊急修正: 最大18文字に制限し、10文字前後で改行を挿入
    """
    if not words:
        return []
    
    # Step 1: 全文字のタイムスタンプを計算
    all_characters = calculate_character_timestamps(words, fps)
    
    if not all_characters:
        return []
    
    print(f"   ✅ Generated {len(all_characters)} character timestamps")
    
    # Step 2: 固有名詞を保護しながらセグメント分割
    print(f"   🔍 Analyzing phrase boundaries (protecting proper nouns)...")
    segments = segment_text_by_phrase_with_proper_nouns(
        all_characters, max_chars, max_duration, proper_noun_parser
    )
    
    print(f"   ✅ Created {len(segments)} natural segments")
    
    # Step 3: 各セグメントを字幕オブジェクトに変換
    subtitles = []
    for i, segment in enumerate(segments):
        if not segment:
            continue
        
        # テキスト結合時にも句読点を除去
        text = "".join([c["char"] for c in segment])
        text = clean_text_punctuation(text, strict=True)
        
        # 🚨 緊急修正: 10文字前後で自動改行を挿入
        if len(text) > 12:
            # 10文字前後の適切な位置で改行
            mid_point = len(text) // 2
            # 8-12文字の範囲で最適な分割点を探す
            best_split = mid_point
            for offset in range(0, 5):
                if mid_point - offset >= 8 and mid_point - offset <= 12:
                    best_split = mid_point - offset
                    break
                elif mid_point + offset >= 8 and mid_point + offset <= 12:
                    best_split = mid_point + offset
                    break
            
            # 改行を挿入
            text = text[:best_split] + "\n" + text[best_split:]
        
        start_time = segment[0]["startTime"]
        end_time = segment[-1]["endTime"]
        
        subtitle = {
            "text": text,
            "characters": segment,
            "startTime": start_time,
            "endTime": end_time
        }
        
        subtitles.append(finalize_karaoke_subtitle(subtitle, fps, i))
    
    # Step 4: 重なり防止処理
    subtitles = prevent_overlap(subtitles)
    
    # セグメント品質レポート
    print(f"\n   📊 Segmentation Quality Report:")
    for i, sub in enumerate(subtitles[:5]):
        char_count = len(sub["text"])
        print(f"      {i+1}. [{char_count:2d}文字] {sub['text']}")
    if len(subtitles) > 5:
        print(f"      ... and {len(subtitles) - 5} more segments")
    
    return subtitles


def finalize_karaoke_subtitle(subtitle: Dict[str, Any], fps: int, index: int) -> Dict[str, Any]:
    """カラオケ字幕オブジェクトを確定"""
    start_frame = int(subtitle["startTime"] * fps)
    end_frame = int(subtitle["endTime"] * fps) - 1
    
    text = subtitle["text"].strip()
    style_type = "normal"
    animation = "fadeIn"
    
    # キーフレーズの検出
    key_phrases = ["BTS", "伝説", "プロデューサー", "チャンス", "今すぐ", "応募", "K-RISE", "K-POP"]
    is_key_phrase = any(phrase in text for phrase in key_phrases)
    
    if is_key_phrase:
        style_type = "emphasis"
        animation = "fadeInScale"
    
    if "？" in text or "?" in text:
        style_type = "question"
        animation = "bounce"
    
    cta_keywords = ["応募", "チェック", "LINE", "今すぐ"]
    if any(keyword in text for keyword in cta_keywords):
        style_type = "cta"
        animation = "fadeInScale"
    
    cleaned_text = clean_text_punctuation(text, strict=True)
    
    return {
        "id": f"sub_{index:03d}",
        "text": cleaned_text,
        "startTime": subtitle["startTime"],
        "endTime": subtitle["endTime"],
        "startFrame": start_frame,
        "endFrame": end_frame,
        "duration": subtitle["endTime"] - subtitle["startTime"],
        "characterCount": len(cleaned_text),
        "characters": subtitle["characters"],
        "style": {
            "type": style_type,
            "animation": animation,
            "fontSize": 75,
            "fontWeight": "bold",
            "color": "#FFFFFF",
            "textShadow": "0px 0px 10px rgba(230,255,0,0.8), 0px 0px 30px rgba(230,255,0,0.5)",
            "position": "center"
        },
        "metadata": {
            "isKeyPhrase": is_key_phrase,
            "characterCount": len(subtitle["characters"]),
            "segmentationVersion": "3.2"
        }
    }


def prevent_overlap(subtitles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """字幕の重なりを完全に防止"""
    for i in range(len(subtitles) - 1):
        current = subtitles[i]
        next_sub = subtitles[i + 1]
        
        if current["endFrame"] >= next_sub["startFrame"]:
            current["endFrame"] = next_sub["startFrame"] - 1
            current["endTime"] = current["endFrame"] / 30.0
            current["duration"] = current["endTime"] - current["startTime"]
    
    return subtitles


def calculate_analytics(words: List[Dict[str, Any]], duration: float) -> Dict[str, Any]:
    """音声の分析データを計算"""
    if not words:
        return {}
    
    pauses = []
    for i in range(len(words) - 1):
        pause = words[i + 1]["start"] - words[i]["end"]
        if pause > 0.1:
            pauses.append(pause)
    
    word_durations = [w["end"] - w["start"] for w in words]
    avg_word_duration = sum(word_durations) / len(word_durations) if word_durations else 0
    speech_rate = len(words) / duration if duration > 0 else 0
    
    return {
        "totalWords": len(words),
        "averageWordDuration": round(avg_word_duration, 3),
        "speechRate": round(speech_rate, 2),
        "pauseCount": len(pauses),
        "longestPause": round(max(pauses), 2) if pauses else 0,
        "shortestPause": round(min(pauses), 2) if pauses else 0
    }


def generate_complete_video_data(
    script_text: str,
    project_id: str = "kpop-audition",
    fps: int = 30,
    audio_volume: float = 4.0,
    bgm_volume: float = 0.08
) -> Dict[str, Any]:
    """
    音声生成から1文字単位の字幕同期まで完全自動化（v3.2 固有名詞保護版）
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    # 固有名詞パーサーの初期化
    proper_noun_parser = None
    if PROPER_NOUN_PARSER_AVAILABLE:
        try:
            proper_noun_parser = ProperNounParser()
            print("✅ Proper Noun Parser initialized")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize ProperNounParser: {e}")
    
    # クレンジング
    script_text = script_text.replace("■", "").replace("★", "").replace("◆", "").strip()
    
    print("=" * 60)
    print("🎬 Character-Level Audio-Driven Video Pipeline v3.2")
    print("   ✨ NEW: Proper Noun Protection System")
    print("=" * 60)
    print(f"📝 Script: {script_text[:50]}...")
    print(f"🎯 Project ID: {project_id}")
    print(f"🎞️  FPS: {fps}")
    print(f"🔧 Janome: {'✅ Available' if JANOME_AVAILABLE else '❌ Not Available'}")
    print(f"🎯 Proper Noun Parser: {'✅ Available' if PROPER_NOUN_PARSER_AVAILABLE else '❌ Not Available'}")
    print()
    
    # Step 1: 音声生成
    print("🎤 Step 1/5: Generating high-quality audio (TTS-1-HD)...")
    audio_path = "public/audio.mp3"
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    
    try:
        audio_response = client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=script_text
        )
        audio_response.stream_to_file(audio_path)
        print(f"   ✅ Audio generated: {audio_path}")
    except Exception as e:
        print(f"   ❌ Error generating audio: {e}")
        raise
    
    # Step 2: 音声解析
    print("\n🔍 Step 2/5: Analyzing audio with Whisper API (word-level)...")
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                language="ja",
                timestamp_granularities=["word", "segment"],
                prompt="BTS, 出口氏, LINE, プロデューサー, K-POP, K-RISE, オーディション"
            )
        
        words = getattr(transcription, "words", [])
        if not words and isinstance(transcription, dict):
            words = transcription.get("words", [])
        
        words = [
            {
                "word": w.get("word") if isinstance(w, dict) else getattr(w, "word"),
                "start": w.get("start") if isinstance(w, dict) else getattr(w, "start"),
                "end": w.get("end") if isinstance(w, dict) else getattr(w, "end")
            }
            for w in words
        ]
        
        duration = getattr(transcription, "duration", 0)
        transcribed_text = getattr(transcription, "text", "")
        
        print(f"   ✅ Transcribed: {transcribed_text}")
        print(f"   ✅ Duration: {duration:.2f}s")
        print(f"   ✅ Words detected: {len(words)}")
    except Exception as e:
        print(f"   ❌ Error analyzing audio: {e}")
        raise
    
    # Step 3: 1文字単位のタイムスタンプ計算
    print("\n🎯 Step 3/5: Calculating character-level timestamps...")
    try:
        all_characters = calculate_character_timestamps(words, fps=fps)
        print(f"   ✅ Generated {len(all_characters)} character timestamps")
        
        for i, char_data in enumerate(all_characters[:5]):
            print(f"      {i+1}. '{char_data['char']}' @ frame {char_data['startFrame']}-{char_data['endFrame']}")
        if len(all_characters) > 5:
            print(f"      ... and {len(all_characters) - 5} more characters")
    except Exception as e:
        print(f"   ❌ Error calculating character timestamps: {e}")
        raise
    
    # Step 4: カラオケスタイル字幕生成（固有名詞保護版）
    print("\n🎤 Step 4/5: Building proper-noun-aware karaoke subtitles...")
    try:
        subtitles = build_karaoke_subtitles_with_proper_nouns(
            words, fps=fps, max_chars=18, proper_noun_parser=proper_noun_parser
        )
        print(f"   ✅ Generated {len(subtitles)} subtitle segments (max 18 chars)")
    except Exception as e:
        print(f"   ❌ Error building subtitles: {e}")
        raise
    
    # Step 5: 統合データ構造の生成
    print("\n🔧 Step 5/5: Building integrated data structure...")
    
    analytics = calculate_analytics(words, duration)
    
    video_data = {
        "version": "3.2",
        "metadata": {
            "projectId": project_id,
            "title": f"{project_id} - Character-Level Sync v3.2",
            "generatedAt": datetime.utcnow().isoformat() + "Z",
            "fps": fps,
            "duration": duration,
            "totalFrames": int(duration * fps),
            "syncMode": "character-level-proper-noun-aware",
            "segmentationEngine": "janome" if JANOME_AVAILABLE else "simple",
            "properNounProtection": PROPER_NOUN_PARSER_AVAILABLE
        },
        "content": {
            "script": {
                "original": script_text,
                "transcribed": transcribed_text
            }
        },
        "audio": {
            "narration": {
                "file": "audio.mp3",
                "duration": duration,
                "volume": audio_volume,
                "generationConfig": {
                    "model": "tts-1-hd",
                    "voice": "nova",
                    "speed": 1.0
                }
            },
            "bgm": {
                "file": "bg-music.mp3",
                "volume": bgm_volume,
                "loop": True,
                "fadeIn": 0.5,
                "fadeOut": 0.5
            }
        },
        "subtitles": subtitles,
        "analytics": analytics
    }
    
    # 保存
    output_path = "public/video-data-master.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Saved to: {output_path}")
    
    # レガシーフォーマットも更新
    legacy_subtitles = [
        {
            "text": clean_text_punctuation(sub["text"], strict=True),
            "startFrame": sub["startFrame"],
            "endFrame": sub["endFrame"]
        }
        for sub in subtitles
    ]
    
    with open("public/sample-video.json", "w", encoding="utf-8") as f:
        json.dump(legacy_subtitles, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Legacy format saved to: public/sample-video.json")
    
    print("\n" + "=" * 60)
    print("✨ Character-Level Pipeline v3.2 completed successfully!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   - Duration: {duration:.2f}s ({int(duration * fps)} frames)")
    print(f"   - Subtitles: {len(subtitles)}")
    print(f"   - Total characters: {len(all_characters)}")
    print(f"   - Words: {analytics.get('totalWords', 0)}")
    print(f"   - Speech rate: {analytics.get('speechRate', 0):.2f} words/sec")
    print(f"   - Sync mode: CHARACTER-LEVEL + PROPER-NOUN-AWARE")
    print(f"   - Proper noun protection: {'✅ ENABLED' if PROPER_NOUN_PARSER_AVAILABLE else '❌ DISABLED'}")
    print("=" * 60)
    
    return video_data


def main():
    """メイン実行関数"""
    script_text = ""
    
    if os.path.exists("today_script.txt"):
        print("📖 Reading script from today_script.txt...")
        try:
            with open("today_script.txt", "r", encoding="utf-8") as f:
                valid_lines = []
                for line in f:
                    line_str = line.strip()
                    if not line_str or line_str.startswith("■") or "ナレーション台本" in line_str:
                        continue
                    valid_lines.append(line_str)
                script_text = " ".join(valid_lines)
        except Exception as e:
            print(f"⚠️  Error reading file: {e}")
    
    if not script_text:
        print("⚠️  Using default script...")
        script_text = (
            "K-RISEとは、アジアモデルフェスティバルの新しいプロジェクトです。"
            "BTSを日本に導いた伝説のプロデューサー、出口氏が直接審査します。"
        )
    
    try:
        video_data = generate_complete_video_data(
            script_text=script_text,
            project_id="kpop-audition",
            fps=30,
            audio_volume=4.0,
            bgm_volume=0.08
        )
        
        print("\n🎉 All done! You can now render your video with Remotion.")
        print("   Run: npm run dev")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
