import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_whisper_sync():
    """実際のaudio.mp3を解析して、完全に同期した字幕を生成"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        return

    client = OpenAI(api_key=api_key)
    audio_path = "public/audio.mp3"
    
    if not os.path.exists(audio_path):
        print(f"Error: {audio_path} not found!")
        return
    
    print(f"Transcribing {audio_path} with OpenAI Whisper API (word-level timestamps)...")
    
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                language="ja",
                timestamp_granularities=["word"],
                prompt="BTS, 出口氏, LINE, プロデューサー, K-POP, オーディション"
            )
        
        print(f"\n=== Transcription Result ===")
        print(f"Full text: {transcription.text}")
        print(f"\n=== Word-level timestamps ===")
        
        subtitles = []
        fps = 30
        
        words = getattr(transcription, "words", [])
        if not words and isinstance(transcription, dict):
            words = transcription.get("words", [])
        
        if words:
            print(f"Found {len(words)} words with timestamps")
            
            # 単語レベルのタイムスタンプから字幕を生成
            current_text = ""
            current_start = None
            
            for i, word_info in enumerate(words):
                if isinstance(word_info, dict):
                    w_text = word_info.get("word", "").strip()
                    w_start = word_info.get("start", 0.0)
                    w_end = word_info.get("end", 0.0)
                else:
                    w_text = getattr(word_info, "word", "").strip()
                    w_start = getattr(word_info, "start", 0.0)
                    w_end = getattr(word_info, "end", 0.0)
                
                print(f"Word {i}: '{w_text}' ({w_start:.2f}s - {w_end:.2f}s)")
                
                if not w_text:
                    continue
                
                # 句読点や文字数で区切る
                has_delimiter = any(d in w_text for d in ["、", "。", "！", "？", "…"])
                
                if current_start is not None and (len(current_text + w_text) > 15 or has_delimiter):
                    # 現在のテキストを保存
                    subtitles.append({
                        "text": current_text.strip(),
                        "startFrame": int(current_start * fps),
                        "endFrame": int(w_start * fps) - 1,
                        "style": "normal"
                    })
                    current_text = w_text
                    current_start = w_start
                else:
                    if current_start is None:
                        current_start = w_start
                    current_text += w_text
            
            # 最後の残りを追加
            if current_text:
                last_end = words[-1].get("end", current_start + 1.0) if isinstance(words[-1], dict) else getattr(words[-1], "end", current_start + 1.0)
                subtitles.append({
                    "text": current_text.strip(),
                    "startFrame": int(current_start * fps),
                    "endFrame": int(last_end * fps),
                    "style": "normal"
                })
        else:
            print("No word-level timestamps available, using segment-based approach")
            segments = getattr(transcription, "segments", [])
            if not segments and isinstance(transcription, dict):
                segments = transcription.get("segments", [])
            
            for segment in segments:
                if isinstance(segment, dict):
                    seg_text = segment.get("text", "").strip()
                    seg_start = segment.get("start", 0.0)
                    seg_end = segment.get("end", 0.0)
                else:
                    seg_text = getattr(segment, "text", "").strip()
                    seg_start = getattr(segment, "start", 0.0)
                    seg_end = getattr(segment, "end", 0.0)
                
                if seg_text:
                    subtitles.append({
                        "text": seg_text,
                        "startFrame": int(seg_start * fps),
                        "endFrame": int(seg_end * fps),
                        "style": "normal"
                    })
        
        # 重なり防止処理
        for idx in range(len(subtitles) - 1):
            if subtitles[idx]["endFrame"] >= subtitles[idx+1]["startFrame"]:
                subtitles[idx]["endFrame"] = subtitles[idx+1]["startFrame"] - 1
        
        # 保存
        output_path = "public/kpop-audition-pattern1.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(subtitles, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== Generated {len(subtitles)} subtitles ===")
        for i, sub in enumerate(subtitles):
            print(f"{i+1}. [{sub['startFrame']}-{sub['endFrame']}] {sub['text']}")
        
        print(f"\nSuccess: Updated {output_path}")
        
        # 実際のナレーション内容を返す
        return transcription.text
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    actual_narration = run_whisper_sync()
    if actual_narration:
        print(f"\n{'='*60}")
        print("実際の音声内容（完全版）:")
        print(f"{'='*60}")
        print(actual_narration)
        print(f"{'='*60}")
