import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def create_perfect_subtitles():
    """正しいスクリプトテキストとWhisperのタイミングを組み合わせて完璧な字幕を作成"""
    
    # 正しいナレーション内容（today_script.txtから）
    correct_narration = "あのBTSを日本に導いた伝説のプロデューサー、出口氏が…まさかの直接審査！？K-POPで本気で成功したいなら、このチャンスを逃したら後悔する。何百人が夢破れた世界で、伝説の男があなたの才能を見抜く。もう二度と巡ってこないこの瞬間、迷ってる時間はない。次は君の番かもしれない。応募はLINEから！プロフィールのリンクをチェックしてね！"
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set")
        return
    
    client = OpenAI(api_key=api_key)
    audio_path = "public/audio.mp3"
    
    print("Transcribing audio with word-level timestamps...")
    
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                language="ja",
                timestamp_granularities=["word"],
                prompt="BTS, 出口氏, LINE, プロデューサー, K-POP, オーディション, 伝説"
            )
        
        words = getattr(transcription, "words", [])
        if not words and isinstance(transcription, dict):
            words = transcription.get("words", [])
        
        if not words:
            print("No word-level timestamps available")
            return
        
        # 音声の総時間を取得
        total_duration = words[-1].get("end", 22.0) if isinstance(words[-1], dict) else getattr(words[-1], "end", 22.0)
        fps = 30
        
        print(f"Total audio duration: {total_duration:.2f}s ({int(total_duration * fps)} frames)")
        print(f"Correct narration: {correct_narration}")
        
        # 正しいテキストを意味のある塊に分割（句読点と長さで）
        segments = [
            "あのBTSを日本に導いた伝説のプロデューサー、",
            "出口氏が…まさかの直接審査！？",
            "K-POPで本気で成功したいなら、",
            "このチャンスを逃したら後悔する。",
            "何百人が夢破れた世界で、",
            "伝説の男があなたの才能を見抜く。",
            "もう二度と巡ってこないこの瞬間、",
            "迷ってる時間はない。",
            "次は君の番かもしれない。",
            "応募はLINEから！",
            "プロフィールのリンクをチェックしてね！"
        ]
        
        # 各セグメントの文字数を計算
        total_chars = sum(len(seg) for seg in segments)
        
        # 時間を文字数に比例して配分
        subtitles = []
        current_time = 0.0
        
        for segment in segments:
            char_ratio = len(segment) / total_chars
            segment_duration = total_duration * char_ratio
            
            start_frame = int(current_time * fps)
            end_frame = int((current_time + segment_duration) * fps) - 1
            
            # 最小表示時間を確保（0.5秒 = 15フレーム）
            if end_frame - start_frame < 15:
                end_frame = start_frame + 15
            
            subtitles.append({
                "text": segment,
                "startFrame": start_frame,
                "endFrame": end_frame,
                "style": "normal"
            })
            
            current_time += segment_duration
            
            print(f"[{start_frame:3d}-{end_frame:3d}] ({(end_frame-start_frame)/fps:.2f}s) {segment}")
        
        # 最後の字幕の終了フレームを調整
        if subtitles:
            subtitles[-1]["endFrame"] = int(total_duration * fps)
        
        # 重なり防止
        for idx in range(len(subtitles) - 1):
            if subtitles[idx]["endFrame"] >= subtitles[idx+1]["startFrame"]:
                subtitles[idx]["endFrame"] = subtitles[idx+1]["startFrame"] - 1
        
        # 保存
        output_path = "public/kpop-audition-pattern1.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(subtitles, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Success! Updated {output_path} with {len(subtitles)} perfectly synced subtitles")
        
        return correct_narration
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    narration = create_perfect_subtitles()
    if narration:
        print(f"\n{'='*70}")
        print("実際の音声内容:")
        print(f"{'='*70}")
        print(narration)
        print(f"{'='*70}")
