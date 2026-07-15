import os
import json
from openai import OpenAI

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

def run_pipeline():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        return

    client = OpenAI(api_key=api_key)
    narration_body = ""

    # today_script.txt から台本テキストを「不要なヘッダーを完全に除外して」正確に読み込む
    if os.path.exists("today_script.txt"):
        try:
            with open("today_script.txt", "r", encoding="utf-8") as f:
                valid_lines = []
                for line in f:
                    line_str = line.strip()
                    if not line_str or line_str.startswith("■") or "ナレーション台本" in line_str:
                        continue
                    valid_lines.append(line_str)
                narration_body = " ".join(valid_lines)
        except Exception as e:
            print(f"Error reading file: {e}")

    if not narration_body:
        narration_body = "K-POPの世界を目指すなら、誰に評価されるかが全て。なんと今回のオーディション、BTSを日本進出させた伝説のプロデューサー出口氏が直々に審査してくれるんです！次は君の番かもしれない。応募はLINEから！プロフィールのリンクをチェックしてね！"

    # 特殊記号やゴミ文字を除去してきれいにクレンジング
    narration_body = narration_body.replace("■", "").replace("★", "").replace("◆", "")
    print(f"Using purified narration text: {narration_body}")

    audio_path = "public/audio.mp3"
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)

    # 1. 最高峰の高音質モデル「tts-1-hd」で純粋なナレーションのみを生成
    print("最高音質モデル「tts-1-hd」で新しいナレーション声を生成中...")
    try:
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=narration_body
        )
        response.stream_to_file(audio_path)
        print("Success: Generated purified studio-quality audio.mp3")
    except Exception as e:
        print(f"Error generating speech: {e}")
        return

    # 2. OpenAIの最高精度クラウドAPI版「Whisper」で単語レベルの超精密タイミングをミリ秒単位で抽出
    print("OpenAI Cloud Whisper API で単語レベルの超高精度ミリ秒解析中...")
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
        
        subtitles = []
        fps = 30
        
        words = getattr(transcription, "words", [])
        if not words and isinstance(transcription, dict):
            words = transcription.get("words", [])

        if words:
            # 単語レベルのタイムスタンプが取得できた場合：ミリ秒完全シンクロで再構成
            current_text = ""
            current_start = None
            
            for word_info in words:
                if isinstance(word_info, dict):
                    w_text = word_info.get("word", "").strip()
                    w_start = word_info.get("start", 0.0)
                    w_end = word_info.get("end", 0.0)
                else:
                    w_text = getattr(word_info, "word", "").strip()
                    w_start = getattr(word_info, "start", 0.0)
                    w_end = getattr(word_info, "end", 0.0)
                
                if not w_text:
                    continue
                    
                # 新しいテロップを開始すべきタイミングか判定（はみ出しの完全防止）
                # 1. w_textを追加すると12文字を超えてしまう場合
                # 2. 単語に句読点が含まれている場合
                has_delimiter = any(d in w_text for d in ["、", "。", "！", "？"])
                
                if current_start is not None and (len(current_text + w_text) > 12 or has_delimiter):
                    # 追加する「前」に、今までのテキストを現在のw_startの瞬間で一旦書き出す
                    subtitles.append({
                        "text": current_text.strip(),
                        "startFrame": int(current_start * fps),
                        "endFrame": int(w_start * fps)
                    })
                    current_text = w_text
                    current_start = w_start
                else:
                    if current_start is None:
                        current_start = w_start
                    current_text += w_text
            
            # 最後の残存パーツを追加
            if current_text:
                subtitles.append({
                    "text": current_text.strip(),
                    "startFrame": int(current_start * fps),
                    "endFrame": int((words[-1].get("end", current_start + 1.0) if isinstance(words[-1], dict) else getattr(words[-1], "end", current_start + 1.0)) * fps)
                })
        else:
            # フォールバック処理：セグメントデータから計算（等分割）
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

                seg_duration = seg_end - seg_start
                if not seg_text or seg_duration <= 0:
                    continue
                
                split_subtexts = split_text_by_length(seg_text, max_len=13)
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
        
        # 【プロ編集仕様：1フレーム瞬間ブランク（残像防止ギャップ）＆重なり防止ガード】
        for idx in range(len(subtitles) - 1):
            next_start = subtitles[idx+1]["startFrame"]
            current_end = subtitles[idx]["endFrame"]
            current_start = subtitles[idx]["startFrame"]
            
            # 前のテロップは、次のテロップが始まる「ちょうど1フレーム（1/30秒）手前」で必ずバサッと消す
            # これにより、文字が次の行にフライングして見える不快感や残像を100%シャットアウトします。
            subtitles[idx]["endFrame"] = max(current_start + 6, next_start - 1)
            
            # もし引き伸ばしすぎたことで次のテロップ開始とぶつかってしまった場合は、
            # 次のテロップの開始を自動的に1フレーム後ろに動かして、重なりを完全に防ぎます。
            if subtitles[idx]["endFrame"] >= subtitles[idx+1]["startFrame"]:
                subtitles[idx+1]["startFrame"] = subtitles[idx]["endFrame"] + 1
        
        with open("public/sample-video.json", "w", encoding="utf-8") as f:
            json.dump(subtitles, f, ensure_ascii=False, indent=2)
        print("Success: Updated public/sample-video.json with boundary-separated OpenAI Whisper subtitles")
    except Exception as e:
        print(f"Error running whisper api: {e}")

if __name__ == "__main__":
    run_pipeline()
