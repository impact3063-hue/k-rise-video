import json
import math
import whisper
from pydub import AudioSegment
import sys
import io

# Windows環境でのUnicode出力問題を解決
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FPS = 30  # Root.tsxのfps設定と必ず一致させる
AUDIO_PATH = "public/audio.mp3"
FINAL_SUBTITLES_PATH = "public/sample-video.json"

def seconds_to_frame(seconds: float) -> int:
    """秒数をフレーム数に変換する。切り上げで、字幕が途切れないようにする。"""
    return math.ceil(seconds * FPS)

def generate_subtitles_from_existing_audio():
    """既存の音声ファイルから字幕を生成する（OpenAI API不要）"""
    print(f"[INFO] 音声ファイル {AUDIO_PATH} をWhisperで解析しています...")
    
    # Whisperで音声を解析
    model = whisper.load_model("base")
    result = model.transcribe(AUDIO_PATH, verbose=False, language="ja")
    
    subtitles = []
    for segment in result["segments"]:
        start_sec = segment["start"]
        end_sec = segment["end"]
        text = segment["text"].strip()
        if not text:
            continue
        subtitles.append(
            {
                "text": text,
                "startFrame": seconds_to_frame(start_sec),
                "endFrame": seconds_to_frame(end_sec),
            }
        )
    
    if not subtitles:
        print("[WARNING] Whisper解析結果が空でした。")
        return
    
    # 音声の長さを取得
    audio = AudioSegment.from_mp3(AUDIO_PATH)
    total_duration_sec = len(audio) / 1000.0
    
    # 最後の字幕のendFrameを音声の終端に合わせる
    subtitles[-1]["endFrame"] = seconds_to_frame(total_duration_sec)
    
    # 書き出し
    with open(FINAL_SUBTITLES_PATH, "w", encoding="utf-8") as f:
        json.dump(subtitles, f, ensure_ascii=False, indent=2)
    
    print(f"\n[SUCCESS] '{FINAL_SUBTITLES_PATH}' を更新しました。字幕数: {len(subtitles)}")
    print(f"[SUCCESS] 動画の最終フレーム: {subtitles[-1]['endFrame']} ({FPS}fps -> 約{subtitles[-1]['endFrame']/FPS:.2f}秒)")
    print(f"[SUCCESS] 最後の字幕テキスト: 「{subtitles[-1]['text']}」")

if __name__ == "__main__":
    generate_subtitles_from_existing_audio()
