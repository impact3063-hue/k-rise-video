import os
import json
import whisper

def split_text_by_length(text, max_len=14):
    """テキストを読みやすく最大文字数以内の短いセグメントに美しく分割する関数です"""
    delimiters = ["、", "。", "！", "？", " ", " "]
    parts = []
    current = ""
    for char in text:
        current += char
        if char in delimiters:
            parts.append(current.strip())
            current = ""
    if current:
        parts.append(current.strip())
    
    final_parts = []
    for part in parts:
        if not part:
            continue
        if len(part) <= max_len:
            final_parts.append(part)
        else:
            for k in range(0, len(part), max_len):
                sub_part = part[k:k+max_len]
                if sub_part:
                    final_parts.append(sub_part)
    return [p for p in final_parts if p]

def run_whisper_only():
    audio_path = "public/audio.mp3"
    
    if not os.path.exists(audio_path):
        print(f"Error: {audio_path} does not exist.")
        return

    # Whisperで基本タイミングを取得
    # ※丸ごと長文をプロンプトに入れるとタイミングが崩壊して字幕が消えるため、重要な単語だけを耳打ち（ヒント）として渡します！
    print("Whisperで音声データを解析中（固有名詞のヒントを指定し、バグを回避しつつ精度を最大化します）...")
    try:
        model = whisper.load_model("base")
        # 重要な単語だけを指定することでタイミング崩壊を防ぎます
        result = model.transcribe(audio_path, verbose=False, language="ja", initial_prompt="BTS, 出口氏, LINE, プロデューサー, K-POP, オーディション")
        
        subtitles = []
        fps = 30
        
        for segment in result["segments"]:
            seg_text = segment["text"].strip()
            seg_start = segment["start"]
            seg_end = segment["end"]
            seg_duration = seg_end - seg_start
            
            if not seg_text or seg_duration <= 0:
                continue
            
            split_subtexts = split_text_by_length(seg_text, max_len=14)
            total_chars = sum(len(t) for t in split_subtexts)
            
            if total_chars == 0:
                continue
                
            current_time = seg_start
            for subtext in split_subtexts:
                char_ratio = len(subtext) / total_chars
                duration_share = seg_duration * char_ratio
                
                sub_start_frame = int(current_time * fps)
                sub_end_frame = int((current_time + duration_share) * fps)
                
                if sub_end_frame - sub_start_frame < 10:
                    sub_end_frame = sub_start_frame + 10
                
                subtitles.append({
                    "text": subtext,
                    "startFrame": sub_start_frame,
                    "endFrame": sub_end_frame
                })
                current_time += duration_share
        
        # タイミングの重なり調整（端数が逆転しないよう、最小表示間隔を1フレーム確保）
        for idx in range(len(subtitles) - 1):
            if subtitles[idx]["endFrame"] > subtitles[idx+1]["startFrame"]:
                subtitles[idx]["endFrame"] = max(subtitles[idx]["startFrame"] + 1, subtitles[idx+1]["startFrame"])
        
        with open("public/sample-video.json", "w", encoding="utf-8") as f:
            json.dump(subtitles, f, ensure_ascii=False, indent=2)
        print("Success: Updated public/sample-video.json with robust tempo subtitles")
        print(f"Generated {len(subtitles)} subtitle segments")
    except Exception as e:
        print(f"Error running whisper: {e}")

if __name__ == "__main__":
    run_whisper_only()
