#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧠 K-RISE 完全自律進化型 量産ライン — 脳と体の統合スクリプト
台本のLLM自律生成 → OpenAI TTS音声合成 → ffmpeg無音実測 →
1文字完全同期 video-data-master.json 出力までを1コマンドで実行。

使い方:
  python scripts/generate-master.py                     # フル自動（LLM台本+TTS）
  python scripts/generate-master.py --script-file s.txt # 台本を手動指定
  python scripts/generate-master.py --skip-tts          # 既存audio.mp3を再利用
必要環境変数: OPENAI_API_KEY（LLM/TTS使用時のみ）
"""
import argparse, datetime, json, os, re, shutil, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
PUB = os.path.join(ROOT, "public")
FPS = 30

DEFAULT_PARAMS = {
    "fontMinRem": 3.0, "fontVw": 9.0, "fontMaxRem": 5.5,
    "glow": 1.0, "scaleFactor": 1.15,
    "ctaText": "伝説のP出口氏が\n審査！\nリアルオーディション\n開催\n詳細はプロフの\nLINEから",
    "ctaSeconds": 2.0,
    "ttsVoice": "alloy", "ttsModel": "tts-1", "ttsSpeed": 1.0,
    "llmModel": "gpt-4o-mini",
}


def load_json(path, fallback):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def openai_post(path, payload, key, raw=False):
    req = urllib.request.Request(
        f"https://api.openai.com/v1/{path}",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read() if raw else json.loads(r.read())


def top_performer_context(log):
    """戦績ログから上位25%動画の台本傾向を抽出（インコンテキスト学習用）"""
    rows = [r for r in log if r.get("stats", {}).get("views") and r.get("scriptText")]
    if len(rows) < 4:
        return ""
    rows.sort(key=lambda r: r["stats"]["views"], reverse=True)
    top = rows[: max(1, len(rows) // 4)]
    lines = [f"- 再生{r['stats']['views']}回 完了率{r['stats'].get('avgWatchPct','?')}%: 「{r['scriptText']}」" for r in top]
    return "【過去の勝ち台本（この傾向をさらに進化させよ）】\n" + "\n".join(lines)


def generate_script(params, log, key):
    ctx = top_performer_context(log)
    prompt = (
        "あなたはTikTokバズ動画の放送作家。K-POPオーディション(審査:伝説のプロデューサー出口氏、"
        "エントリーは公式LINE)への参加を煽る15秒ナレーション台本を1本書け。\n"
        "条件: 全体70〜90文字。冒頭2秒で視聴者の手を止める強いフック。句点で4文に区切る。"
        "絵文字・記号・改行なしのプレーンな日本語のみ出力。\n" + ctx
    )
    res = openai_post("chat/completions", {
        "model": params["llmModel"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
    }, key)
    text = re.sub(r"[\s\u3000]", "", res["choices"][0]["message"]["content"])
    print(f"📝 LLM台本({len(text)}文字): {text}")
    return text


def synthesize_tts(text, params, key):
    audio = openai_post("audio/speech", {
        "model": params["ttsModel"], "voice": params["ttsVoice"],
        "speed": params["ttsSpeed"], "input": text,
    }, key, raw=True)
    with open(os.path.join(PUB, "audio.mp3"), "wb") as f:
        f.write(audio)
    print(f"🔊 TTS出力: public/audio.mp3 ({len(audio)}bytes)")


def probe_duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out.strip())


def detect_speech_segments(path, total):
    """ffmpeg silencedetectで無音を物理実測し、発話区間(秒)のリストを返す"""
    out = subprocess.run(
        ["ffmpeg", "-i", path, "-af", "silencedetect=noise=-35dB:d=0.25", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", out)]
    segs, cursor = [], 0.0
    for s, e in zip(starts, ends):
        if s - cursor > 0.15:
            segs.append((cursor, s))
        cursor = e
    if total - cursor > 0.15:
        segs.append((cursor, total))
    return segs or [(0.0, total)]


def split_script(text, segs):
    """台本を発話区間の長さに比例した文字数で分割"""
    total = sum(e - s for s, e in segs)
    chunks, pos = [], 0
    for i, (s, e) in enumerate(segs):
        n = len(text) - pos if i == len(segs) - 1 else max(1, round(len(text) * (e - s) / total))
        chunks.append(text[pos:pos + n]); pos += n
    return chunks


def build_chars(text, st, en):
    n, chars = len(text), []
    for i, ch in enumerate(text):
        cs = st + round(i * (en - st) / n)
        ce = min(max(cs + 1, st + round((i + 1) * (en - st) / n)), en)
        chars.append({"char": ch, "startTime": round(cs / FPS, 3), "endTime": round(ce / FPS, 3),
                      "startFrame": cs, "endFrame": ce, "duration": round((ce - cs) / FPS, 3), "wordIndex": 0})
    chars[-1]["endFrame"] = en; chars[-1]["endTime"] = round(en / FPS, 3)
    return chars


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script-file", help="台本テキストファイル（指定時はLLM生成をスキップ）")
    ap.add_argument("--skip-tts", action="store_true", help="既存public/audio.mp3を再利用")
    args = ap.parse_args()

    params = {**DEFAULT_PARAMS, **load_json(os.path.join(DOCS, "params-current.json"), {})}
    log = load_json(os.path.join(DOCS, "tiktok-analytics-log.json"), [])
    key = os.environ.get("OPENAI_API_KEY", "")

    # 1) 台本
    if args.script_file:
        with open(args.script_file, encoding="utf-8") as f:
            script = re.sub(r"[\s\u3000]", "", f.read())
    else:
        if not key:
            sys.exit("❌ OPENAI_API_KEY未設定。--script-file で台本を渡すか環境変数を設定してください。")
        script = generate_script(params, log, key)

    # 2) 音声
    if not args.skip_tts:
        if not key:
            sys.exit("❌ OPENAI_API_KEY未設定。--skip-tts で既存音声を再利用できます。")
        synthesize_tts(script, params, key)

    # 3) 物理実測 → 同期データ生成
    audio_path = os.path.join(PUB, "audio.mp3")
    audio_sec = probe_duration(audio_path)
    segs = detect_speech_segments(audio_path, audio_sec)
    chunks = split_script(script, segs)
    print(f"🎙️ 音声実測 {audio_sec:.3f}s / 発話{len(segs)}区間: " +
          ", ".join(f"{s:.2f}-{e:.2f}s「{c[:8]}…」" for (s, e), c in zip(segs, chunks)))

    narration_end = round(audio_sec * FPS)
    total_frames = narration_end + round(params["ctaSeconds"] * FPS)
    subs = []
    for i, ((ss, se), text) in enumerate(zip(segs, chunks), 1):
        st, en = round(ss * FPS), round(se * FPS)
        subs.append({"id": f"line-{i}", "text": text, "startFrame": st, "endFrame": en,
            "style": {"animation": "karaoke", "type": "highlight", "fontFamily": "Impact", "fontSize": 48,
                      "color": "#FFFFFF", "highlightColor": "#FFD700", "scaleFactor": params["scaleFactor"]},
            "characters": build_chars(text, st, en), "duration": round(se - ss, 3),
            "characterCount": len(text), "metadata": {"isKeyPhrase": True, "characterCount": len(text)}})
    subs.append({"id": "cta", "text": params["ctaText"], "startFrame": narration_end, "endFrame": total_frames,
        "style": {"animation": "fadeInScale", "type": "cta", "fontFamily": "Noto Sans JP", "fontSize": 42,
                  "color": "#FFFACD", "highlightColor": "#FFD700", "scaleFactor": 1.0},
        "characters": [], "duration": params["ctaSeconds"],
        "characterCount": len(params["ctaText"]), "metadata": {"isKeyPhrase": False, "characterCount": len(params["ctaText"])}})

    master_path = os.path.join(PUB, "video-data-master.json")
    if os.path.exists(master_path):
        shutil.copy(master_path, master_path + ".prev")
    master = {
        "version": "5.0.0",
        "metadata": {"projectId": "K-RISE-TikTok-3", "title": "K-RISE Dance Project - Auto",
                     "generatedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "fps": FPS, "duration": round(total_frames / FPS, 3), "totalFrames": total_frames,
                     "syncMode": "character-level"},
        "content": {"script": {"original": script, "transcribed": script}},
        "audio": {"narration": {"file": "audio.mp3", "duration": audio_sec, "volume": 0.8,
                                "generationConfig": {"model": params["ttsModel"], "voice": params["ttsVoice"],
                                                     "speed": params["ttsSpeed"]}},
                  "bgm": {"file": "bg-music.mp3", "volume": 0.3, "loop": True, "fadeIn": 0.5, "fadeOut": 0.5}},
        "renderParams": {k: params[k] for k in ("fontMinRem", "fontVw", "fontMaxRem", "glow")},
        "subtitles": subs,
        "analytics": {"totalWords": len(segs), "averageWordDuration": round(audio_sec / max(1, len(script)), 3),
                      "speechRate": round(len(script) / audio_sec * 60), "pauseCount": max(0, len(segs) - 1),
                      "longestPause": 0.3},
    }
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    print(f"✅ video-data-master.json v5.0.0 出力完了 ({total_frames}frames / 台本{len(script)}文字 / 全文字TS付き)")


if __name__ == "__main__":
    main()
