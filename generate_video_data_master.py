# -*- coding: utf-8 -*-
"""
世界最高峰のデータ駆動型動画生成マスタースクリプト v3.1
Character-Level Audio-Driven Video Generation Pipeline with Phrase-Aware Segmentation

このスクリプトは以下を完全自動化します：
1. 高品質音声生成（OpenAI TTS-1-HD）
2. 単語レベルの音声解析（Whisper API）
3. 1文字単位の超精密タイムスタンプ生成
4. 文節・品詞境界を考慮したカラオケスタイルの字幕データ構造出力

v3.1 新機能:
- Janomeによる形態素解析を用いた文節境界検出
- 単語・文節の途中での不自然な分割を防止
- 句読点・記号を優先した自然な改行位置の決定
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

# 🎯 句読点完全除去システム - Guard A (データ前処理レイヤー)
# すべての句読点・約物を検出し、空文字に置換する正規表現
PUNCTUATION_REGEX = re.compile(
    r'[、，,。．.・･！？!?…‥「」『』（）()【】［］\[\]〈〉《》〔〕｛｝\{\}〜～'
    r'\u3000-\u303F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]'
)

# より厳密な句読点のみの正規表現（保守的なアプローチ）
STRICT_PUNCTUATION_REGEX = re.compile(
    r'[、，,。．.・･\u3001\u3002\uFF0C\uFF0E\u30FB\uFF65]'
)


def clean_text_punctuation(text: str, strict: bool = True) -> str:
    """
    🎯 Guard A: データ生成時に句読点を完全除去
    
    Args:
        text: クリーニング対象のテキスト
        strict: True=句読点・中黒のみ除去, False=すべての記号除去
    
    Returns:
        クリーニング済みテキスト
    """
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
    🎯 世界最高峰：1文字単位のタイムスタンプ計算
    
    Whisper APIの単語レベルタイムスタンプから、各文字が
    「何フレーム目に表示されるべきか」を1文字単位で計算します。
    
    アルゴリズム:
    - 各単語の開始・終了時間から、その単語内の文字数で均等分割
    - 各文字に対して startFrame と endFrame を割り当て
    - 日本語の1文字も英語の1文字も同等に扱う
    
    Args:
        words: Whisper APIから取得した単語レベルのタイムスタンプ
        fps: フレームレート（デフォルト30fps）
    
    Returns:
        1文字単位のタイムスタンプデータ
    """
    character_data = []
    
    for word in words:
        w_text = word.get("word", "").strip()
        w_start = word.get("start", 0.0)
        w_end = word.get("end", 0.0)
        
        if not w_text:
            continue
        
        # 単語の文字数
        char_count = len(w_text)
        
        # 単語の継続時間
        word_duration = w_end - w_start
        
        # 1文字あたりの時間（均等分割）
        if char_count > 0:
            char_duration = word_duration / char_count
        else:
            char_duration = 0
        
        # 各文字のタイムスタンプを計算
        for i, char in enumerate(w_text):
            char_start = w_start + (i * char_duration)
            char_end = char_start + char_duration
            
            char_start_frame = int(char_start * fps)
            char_end_frame = int(char_end * fps)
            
            # 🎯 Guard A: 句読点を完全除去（データ生成時）
            cleaned_char = clean_text_punctuation(char, strict=True)
            
            character_data.append({
                "char": cleaned_char,  # クリーニング済み文字
                "startTime": round(char_start, 4),
                "endTime": round(char_end, 4),
                "startFrame": char_start_frame,
                "endFrame": char_end_frame,
                "duration": round(char_duration, 4),
                "wordIndex": len(character_data)  # グローバルインデックス
            })
    
    return character_data


def detect_phrase_boundaries(text: str) -> List[int]:
    """
    🎯 v3.1新機能: 形態素解析による文節境界の検出
    
    Janomeを使用して日本語テキストを形態素解析し、
    自然な分割ポイント（文節境界）のインデックスリストを返します。
    
    優先度:
    1. 句読点・記号（「、」「。」「！」「？」など）
    2. 自立語の開始位置（名詞、動詞、形容詞、副詞など）
    3. 助詞の直前（「は」「が」「を」「に」など）
    
    Args:
        text: 解析対象のテキスト
    
    Returns:
        文節境界のインデックスリスト（0-based）
    """
    if not JANOME_AVAILABLE or not text:
        # Janomeが利用できない場合は句読点のみを境界とする
        boundaries = []
        for i, char in enumerate(text):
            if char in ["、", "。", "！", "？", "!", "?", " ", "　"]:
                boundaries.append(i + 1)  # 句読点の直後
        return boundaries
    
    tokenizer = Tokenizer()
    boundaries = []
    current_idx = 0
    
    try:
        tokens = list(tokenizer.tokenize(text))
        
        for token in tokens:
            surface = token.surface
            pos_info = token.part_of_speech.split(',')
            pos = pos_info[0] if pos_info else ""
            
            # 句読点・記号は最優先の境界
            if pos == "記号":
                boundaries.append(current_idx + len(surface))
            
            # 自立語（名詞、動詞、形容詞、副詞、接続詞、感動詞）の開始位置
            elif pos in ['名詞', '動詞', '形容詞', '副詞', '接続詞', '感動詞']:
                if current_idx > 0:  # 文頭以外
                    boundaries.append(current_idx)
            
            # 助詞の直前も境界候補（ただし優先度は低い）
            elif pos == '助詞' and current_idx > 0:
                boundaries.append(current_idx)
            
            current_idx += len(surface)
        
    except Exception as e:
        print(f"⚠️  Morphological analysis warning: {e}")
        # エラー時は句読点のみを境界とする
        boundaries = []
        for i, char in enumerate(text):
            if char in ["、", "。", "！", "？", "!", "?", " ", "　"]:
                boundaries.append(i + 1)
    
    # 重複を削除してソート
    boundaries = sorted(list(set(boundaries)))
    
    return boundaries


def find_optimal_break_point(
    text: str,
    boundaries: List[int],
    max_chars: int,
    current_length: int
) -> Optional[int]:
    """
    🎯 v3.1新機能: 最適な分割ポイントの検索
    
    文節境界リストから、max_charsを超えない範囲で
    最も適切な分割ポイントを見つけます。
    
    Args:
        text: 対象テキスト
        boundaries: 文節境界のインデックスリスト
        max_chars: 最大文字数
        current_length: 現在の累積文字数
    
    Returns:
        最適な分割ポイントのインデックス（見つからない場合はNone）
    """
    # 現在の長さから見て、max_charsを超えない境界を探す
    valid_boundaries = [b for b in boundaries if b <= current_length and b <= max_chars]
    
    if not valid_boundaries:
        return None
    
    # 最もmax_charsに近い境界を選択
    return max(valid_boundaries)


def segment_text_by_phrase(
    character_data: List[Dict[str, Any]],
    max_chars: int = 14,
    max_duration: float = 3.0
) -> List[List[Dict[str, Any]]]:
    """
    🎯 v3.1新機能: 文節・品詞境界を考慮したテキストセグメント分割
    
    1文字単位のデータを、文節境界を尊重しながら
    読みやすいセグメント（字幕単位）に分割します。
    
    アルゴリズム:
    1. 全テキストから形態素解析で文節境界を検出
    2. 句読点を最優先の分割ポイントとする
    3. max_charsに達する前に、最適な文節境界で分割
    4. 単語・文節の途中での分割を回避
    
    Args:
        character_data: 1文字単位のタイムスタンプデータ
        max_chars: 1セグメントの最大文字数（推奨: 12-15）
        max_duration: 1セグメントの最大表示時間（秒）
    
    Returns:
        セグメント分割された文字データのリスト
    """
    if not character_data:
        return []
    
    # 全テキストを結合
    full_text = "".join([d["char"] for d in character_data])
    
    # 文節境界を検出
    boundaries = detect_phrase_boundaries(full_text)
    
    print(f"   📊 Detected {len(boundaries)} phrase boundaries in text")
    
    segments = []
    current_segment = []
    segment_start_idx = 0
    
    for i, char_data in enumerate(character_data):
        char = char_data["char"]
        current_segment.append(char_data)
        current_length = len(current_segment)
        
        # 現在位置が境界かどうか
        is_boundary = (i + 1) in boundaries
        
        # 句読点の検出（最優先の分割ポイント）
        is_punctuation = char in ["、", "。", "！", "？", "!", "?"]
        
        # 現在のセグメントの継続時間
        if current_segment:
            segment_duration = char_data["endTime"] - current_segment[0]["startTime"]
        else:
            segment_duration = 0
        
        # 分割条件の判定
        should_break = False
        
        # 条件1: 句読点（最優先）
        if is_punctuation:
            should_break = True
        
        # 条件2: max_charsに達し、かつ境界位置
        elif current_length >= max_chars and is_boundary:
            should_break = True
        
        # 条件3: max_charsを超過（緊急分割）
        elif current_length > max_chars:
            # 直近の境界を探して分割
            optimal_break = find_optimal_break_point(
                full_text[segment_start_idx:i+1],
                [b - segment_start_idx for b in boundaries if segment_start_idx <= b <= i],
                max_chars,
                current_length
            )
            
            if optimal_break and optimal_break < current_length:
                # 最適な位置まで戻って分割
                split_segment = current_segment[:optimal_break]
                remaining = current_segment[optimal_break:]
                
                if split_segment:
                    segments.append(split_segment)
                
                current_segment = remaining
                segment_start_idx = i - len(remaining) + 1
                should_break = False
            else:
                # 境界が見つからない場合は強制分割
                should_break = True
        
        # 条件4: 時間オーバー
        elif segment_duration > max_duration:
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


def build_karaoke_subtitles(
    words: List[Dict[str, Any]], 
    fps: int = 30,
    max_chars: int = 14,
    max_duration: float = 3.0
) -> List[Dict[str, Any]]:
    """
    🎤 カラオケスタイルの字幕生成（1文字単位の超精密同期 + 文節考慮）
    
    v3.1改良点:
    - 形態素解析による文節境界の検出
    - 単語・文節の途中での不自然な分割を防止
    - 句読点を優先した自然な改行位置の決定
    
    原則:
    - 読みやすさ優先（1行12-15文字以内）
    - 1文字単位のタイムスタンプ（フレーム完全同期）
    - 自然な区切り（句読点・文節単位）
    - 重なり完全防止
    
    Args:
        words: Whisper APIから取得した単語レベルのタイムスタンプ
        fps: フレームレート（デフォルト30fps）
        max_chars: 1字幕の最大文字数
        max_duration: 1字幕の最大表示時間（秒）
    
    Returns:
        1文字単位のタイムスタンプを含む字幕データのリスト
    """
    if not words:
        return []
    
    # Step 1: 全文字のタイムスタンプを計算
    all_characters = calculate_character_timestamps(words, fps)
    
    if not all_characters:
        return []
    
    print(f"   ✅ Generated {len(all_characters)} character timestamps")
    
    # Step 2: 文節を考慮してセグメント分割
    print(f"   🔍 Analyzing phrase boundaries with Janome...")
    segments = segment_text_by_phrase(all_characters, max_chars, max_duration)
    
    print(f"   ✅ Created {len(segments)} natural segments")
    
    # Step 3: 各セグメントを字幕オブジェクトに変換
    subtitles = []
    for i, segment in enumerate(segments):
        if not segment:
            continue
        
        # 🎯 Guard A: テキスト結合時にも句読点を除去
        text = "".join([c["char"] for c in segment])
        text = clean_text_punctuation(text, strict=True)
        
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
    """
    カラオケ字幕オブジェクトを確定
    
    Args:
        subtitle: 構築中の字幕データ
        fps: フレームレート
        index: 字幕のインデックス
    
    Returns:
        確定した字幕オブジェクト（1文字単位のタイムスタンプ付き）
    """
    start_frame = int(subtitle["startTime"] * fps)
    end_frame = int(subtitle["endTime"] * fps) - 1  # 1フレーム前で終了
    
    # スタイルの自動判定
    text = subtitle["text"].strip()
    style_type = "normal"
    animation = "fadeIn"
    
    # キーフレーズの検出
    key_phrases = ["BTS", "伝説", "プロデューサー", "チャンス", "今すぐ", "応募"]
    is_key_phrase = any(phrase in text for phrase in key_phrases)
    
    if is_key_phrase:
        style_type = "emphasis"
        animation = "fadeInScale"
    
    # 疑問文の検出
    if "？" in text or "?" in text:
        style_type = "question"
        animation = "bounce"
    
    # CTAの検出
    cta_keywords = ["応募", "チェック", "LINE", "今すぐ"]
    if any(keyword in text for keyword in cta_keywords):
        style_type = "cta"
        animation = "fadeInScale"
    
    # 🎯 Guard A: 最終確認で句読点を除去
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
        "characters": subtitle["characters"],  # 🎯 1文字単位のタイムスタンプ
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
            "segmentationVersion": "3.1"  # 🎯 新バージョン識別子
        }
    }


def prevent_overlap(subtitles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    字幕の重なりを完全に防止
    
    原則: 現在の字幕は次の字幕の1フレーム前で必ず終了
    
    Args:
        subtitles: 字幕データのリスト
    
    Returns:
        重なりを修正した字幕データ
    """
    for i in range(len(subtitles) - 1):
        current = subtitles[i]
        next_sub = subtitles[i + 1]
        
        # 重なりチェック
        if current["endFrame"] >= next_sub["startFrame"]:
            # 現在の字幕を次の字幕の1フレーム前で終了
            current["endFrame"] = next_sub["startFrame"] - 1
            current["endTime"] = current["endFrame"] / 30.0
            current["duration"] = current["endTime"] - current["startTime"]
    
    return subtitles


def calculate_analytics(words: List[Dict[str, Any]], duration: float) -> Dict[str, Any]:
    """
    音声の分析データを計算
    
    Args:
        words: 単語レベルのタイムスタンプ
        duration: 音声の総時間
    
    Returns:
        分析データ
    """
    if not words:
        return {}
    
    # 単語間の間隔を計算
    pauses = []
    for i in range(len(words) - 1):
        pause = words[i + 1]["start"] - words[i]["end"]
        if pause > 0.1:  # 0.1秒以上の間隔をポーズとみなす
            pauses.append(pause)
    
    # 平均単語時間
    word_durations = [w["end"] - w["start"] for w in words]
    avg_word_duration = sum(word_durations) / len(word_durations) if word_durations else 0
    
    # 発話速度（単語/秒）
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
    音声生成から1文字単位の字幕同期まで完全自動化（v3.1 文節考慮版）
    
    このパイプラインは以下を実行します：
    1. OpenAI TTS-1-HDで高品質音声を生成
    2. Whisper APIで単語レベルの音声解析
    3. 1文字単位のタイムスタンプ計算
    4. Janomeによる形態素解析で文節境界を検出
    5. 文節を尊重したカラオケスタイルの字幕データ構造を出力
    
    Args:
        script_text: ナレーション台本
        project_id: プロジェクトID
        fps: フレームレート
        audio_volume: ナレーション音量
        bgm_volume: BGM音量
    
    Returns:
        統合された動画データ（1文字単位のタイムスタンプ付き）
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    # クレンジング
    script_text = script_text.replace("■", "").replace("★", "").replace("◆", "").strip()
    
    print("=" * 60)
    print("🎬 Character-Level Audio-Driven Video Pipeline v3.1")
    print("   ✨ NEW: Phrase-Aware Segmentation with Janome")
    print("=" * 60)
    print(f"📝 Script: {script_text[:50]}...")
    print(f"🎯 Project ID: {project_id}")
    print(f"🎞️  FPS: {fps}")
    print(f"🔧 Janome: {'✅ Available' if JANOME_AVAILABLE else '❌ Not Available'}")
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
                prompt="BTS, 出口氏, LINE, プロデューサー, K-POP, オーディション"
            )
        
        words = getattr(transcription, "words", [])
        if not words and isinstance(transcription, dict):
            words = transcription.get("words", [])
        
        # dict形式に変換
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
        
        # 最初の5文字をプレビュー
        for i, char_data in enumerate(all_characters[:5]):
            print(f"      {i+1}. '{char_data['char']}' @ frame {char_data['startFrame']}-{char_data['endFrame']}")
        if len(all_characters) > 5:
            print(f"      ... and {len(all_characters) - 5} more characters")
    except Exception as e:
        print(f"   ❌ Error calculating character timestamps: {e}")
        raise
    
    # Step 4: カラオケスタイル字幕生成（文節考慮版）
    print("\n🎤 Step 4/5: Building phrase-aware karaoke subtitles...")
    try:
        subtitles = build_karaoke_subtitles(words, fps=fps, max_chars=14)
        print(f"   ✅ Generated {len(subtitles)} subtitle segments")
    except Exception as e:
        print(f"   ❌ Error building subtitles: {e}")
        raise
    
    # Step 5: 統合データ構造の生成
    print("\n🔧 Step 5/5: Building integrated data structure...")
    
    analytics = calculate_analytics(words, duration)
    
    video_data = {
        "version": "3.1",  # 🎯 Phrase-aware version
        "metadata": {
            "projectId": project_id,
            "title": f"{project_id} - Character-Level Sync v3.1",
            "generatedAt": datetime.utcnow().isoformat() + "Z",
            "fps": fps,
            "duration": duration,
            "totalFrames": int(duration * fps),
            "syncMode": "character-level-phrase-aware",  # 🎯 新モード
            "segmentationEngine": "janome" if JANOME_AVAILABLE else "simple"
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
    
    # 後方互換性のため、sample-video.jsonも更新
    # 🎯 Guard A: レガシーフォーマットでも句読点を除去
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
    print("✨ Character-Level Pipeline v3.1 completed successfully!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   - Duration: {duration:.2f}s ({int(duration * fps)} frames)")
    print(f"   - Subtitles: {len(subtitles)}")
    print(f"   - Total characters: {len(all_characters)}")
    print(f"   - Words: {analytics.get('totalWords', 0)}")
    print(f"   - Speech rate: {analytics.get('speechRate', 0):.2f} words/sec")
    print(f"   - Sync mode: CHARACTER-LEVEL + PHRASE-AWARE")
    print(f"   - Segmentation: {'Janome (形態素解析)' if JANOME_AVAILABLE else 'Simple (句読点のみ)'}")
    print("=" * 60)
    
    return video_data


def main():
    """メイン実行関数"""
    # today_script.txtから台本を読み込む
    script_text = ""
    
    if os.path.exists("today_script.txt"):
        print("📖 Reading script from today_script.txt...")
        try:
            with open("today_script.txt", "r", encoding="utf-8") as f:
                valid_lines = []
                for line in f:
                    line_str = line.strip()
                    # ヘッダー行をスキップ
                    if not line_str or line_str.startswith("■") or "ナレーション台本" in line_str:
                        continue
                    valid_lines.append(line_str)
                script_text = " ".join(valid_lines)
        except Exception as e:
            print(f"⚠️  Error reading file: {e}")
    
    # フォールバック
    if not script_text:
        print("⚠️  Using default script...")
        script_text = (
            "あのBTSを日本に導いた伝説のプロデューサー、出口氏が…まさかの直接審査！？"
            "K-POPで本気で成功したいなら、このチャンスを逃したら後悔する。"
            "何百人が夢破れた世界で、伝説の男があなたの才能を見抜く。"
            "もう二度と巡ってこないこの瞬間、迷ってる時間はない。"
            "次は君の番かもしれない。応募はLINEから！プロフィールのリンクをチェックしてね！"
        )
    
    # パイプライン実行
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
