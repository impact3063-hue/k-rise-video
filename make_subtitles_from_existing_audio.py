import os
import json
from openai import OpenAI

def split_text_by_length(text, max_len=14):
    """テキストを読みやすく最大文字数以内の短いセグメントに美しく分割する関数です"""
    delimiters = ["、", "。", "！", "？", " ", "　"]
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
    
    # APIキーをトリムして余分なスペースを除去
    api_key = api_key.strip()
    print(f"API Key length: {len(api_key)}")  # デバッグ用

    # タイムアウトとリトライ設定を追加
    import httpx
    http_client = httpx.Client(timeout=60.0)
    client = OpenAI(api_key=api_key, http_client=http_client)

    audio_path = "public/audio.mp3"
    
    if not os.path.exists(audio_path):
        print(f"Error: {audio_path} not found. Please generate audio first.")
        return

    print(f"Using existing audio file: {audio_path}")

    # OpenAIの最高精度クラウドAPI版「Whisper」で単語レベルの超精密タイミングをミリ秒単位で抽出
    print("OpenAI Cloud Whisper API で単語レベルの超高精度ミリ秒解析中...")
    try:
        with open(audio_path, "rb") as audio_file:
            # response_format="verbose_json" と timestamp_granularities=["word"] の組み合わせにより、
            # 単語が発声された「まさにそのミリ秒」を完全に特定し、タイミングのズレ（グダグダ感）を完全解消します。
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                language="ja",
                timestamp_granularities=["word"],
                prompt="BTS, 出口氏, LINE, プロデューサー, K-POP, オーディション" # 固有名詞のヒントを渡してさらに精度を極限まで高めます
            )
        
        subtitles = []
        fps = 30
        
        # APIレスポンスはDict形式、もしくはSDKのオブジェクト属性として返ってきます。
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
                    
                if current_start is None:
                    current_start = w_start
                
                # 12〜14文字以内、または区切り記号を検知したらテロップをテンポよく分割
                if len(current_text + w_text) > 13 or any(d in w_text for d in ["、", "。", "！", "？", " ", "　"]):
                    if current_text:
                        subtitles.append({
                            "text": current_text.strip(),
                            "startFrame": int(current_start * fps),
                            "endFrame": int(w_start * fps) # 次の単語が出る直前まで表示
                        })
                    current_text = w_text
                    current_start = w_start
                else:
                    current_text += w_text
            
            # 最後のパーツを追加
            if current_text:
                subtitles.append({
                    "text": current_text.strip(),
                    "startFrame": int(current_start * fps),
                    "endFrame": int(words[-1].get("end", current_start + 1.0) if isinstance(words[-1], dict) else getattr(words[-1], "end", current_start + 1.0) * fps)
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
        
        # 【境界セーフティバッファ＆テレビプロ品質ホールドロジック】
        # テロップ同士の切れ目がブツ切れになったり、文字が数ミリ秒切れてしまう現象を防ぎつつ、
        # 次のテロップの最初の1文字が絶対にフライングして食い込まないように極小バッファを持たせます。
        for idx in range(len(subtitles) - 1):
            next_start = subtitles[idx+1]["startFrame"]
            current_end = subtitles[idx]["endFrame"]
            
            # 前のテロップの終わりと次のテロップの始まりの「無音の隙間」が9フレーム（0.3秒）未満の場合、
            # 隙間を極限まで埋めますが、次の文字が絶対に食い込まないように「1フレーム(約0.03秒)手前」でバサッと閉じます。
            if next_start - current_end < 9:
                subtitles[idx]["endFrame"] = max(subtitles[idx]["startFrame"] + 1, next_start - 1)
            else:
                # 明確な間（ポーズ）がある場合も、次の開始の1フレーム前までに制限してフライングを防ぎます
                subtitles[idx]["endFrame"] = min(current_end, next_start - 1)
        
        with open("public/sample-video.json", "w", encoding="utf-8") as f:
            json.dump(subtitles, f, ensure_ascii=False, indent=2)
        print("Success: Updated public/sample-video.json with high-precision OpenAI Whisper subtitles")
        print(f"Generated {len(subtitles)} subtitle segments")
    except Exception as e:
        print(f"Error running whisper api: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_pipeline()
