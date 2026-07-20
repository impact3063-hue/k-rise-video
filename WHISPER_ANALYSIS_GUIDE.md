# Whisper Audio Analysis Guide

## 🎯 Purpose
Extract millisecond-accurate phrase timing from actual audio waveform to achieve 1-frame (33.33ms) synchronization precision.

## 📋 Prerequisites

### 1. Install Whisper
```bash
pip install openai-whisper
```

**Note:** This installs PyTorch and other dependencies (~2-3 GB). Installation may take 5-10 minutes.

### 2. Verify Installation
```bash
python -c "import whisper; print('Whisper version:', whisper.__version__)"
```

## 🚀 Usage

### Step 1: Run Whisper Analysis
```bash
cd k-rise-video
python analyze_audio_whisper_phrases.py
```

**What it does:**
1. Loads Whisper base model
2. Analyzes `public/audio.mp3` with word-level timestamps
3. Maps words to 23 expected phrases
4. Generates `public/video-data-capcut-style.json` with frame-accurate timing

**Expected output:**
```
======================================================================
Whisper Audio Analysis - Phrase-Level Timing Extraction
======================================================================

Loading Whisper model (base)...
Analyzing audio: public/audio.mp3
This may take a few minutes...

Transcription: ダンス未経験でも世界へ行ける。条件はただ一つ...

Extracted 45 word segments:

   1. 'ダンス' - 0.120s → 0.580s (Frame 4 → 17)
   2. '未経験' - 0.600s → 1.200s (Frame 18 → 36)
   ...

======================================================================
Mapping Words to Phrases
======================================================================

Phrase: 'ダンス'
  Words: ダンス
  Timing: Frame 4 → 17 (0.43s)

Phrase: '未経験でも'
  Words: 未経験 + でも
  Timing: Frame 18 → 45 (0.90s)

...

======================================================================
JSON Generation Complete
======================================================================

Generated: public/video-data-capcut-style.json
Total phrases: 23
Timing source: Whisper word-level timestamps
Frame accuracy: 1/30 second (33.33ms)
```

### Step 2: Verify JSON Data
Check `public/video-data-capcut-style.json`:
```json
{
  "version": "10.1.0-whisper-accurate",
  "metadata": {
    "timingSource": "Whisper word-level timestamps"
  },
  "phrases": [
    {"text": "ダンス", "startFrame": 4, "endFrame": 17},
    {"text": "未経験でも", "startFrame": 18, "endFrame": 45},
    ...
  ]
}
```

### Step 3: Render Video (ONE TIME ONLY)
```bash
npx remotion render KRiseTikTok5 out/k-rise-capcut-style.mp4 --overwrite
```

### Step 4: Commit Changes
```bash
git add -A
git commit -m "Fix: Whisper-accurate phrase timing from actual audio waveform"
git push origin main
```

## 📊 Expected Phrases

The script expects these 23 phrases in order:

1. ダンス
2. 未経験でも
3. 世界へ
4. 行ける
5. 条件は
6. ただ一つ
7. 毎日
8. 鏡の前に
9. 立つこと
10. 才能は
11. 言い訳に
12. ならない
13. 本気の
14. 覚悟が
15. 君を変える
16. 残された
17. 席は
18. あとわずか
19. 今すぐ
20. 公式LINE
21. から
22. エントリー
23. しよう

## 🔧 Troubleshooting

### Whisper Not Found
```bash
pip install openai-whisper
```

### PyTorch Issues
```bash
pip install torch torchvision torchaudio
```

### Audio File Not Found
Ensure `public/audio.mp3` exists in the k-rise-video directory.

### Phrase Mismatch
If Whisper transcription doesn't match expected phrases, manually adjust the phrase mapping in `analyze_audio_whisper_phrases.py`.

## 📝 Technical Details

### Frame Calculation
```python
frame = round(seconds * 30)  # 30 FPS
```

### Timing Precision
- **Whisper accuracy:** ~10-50ms
- **Frame duration:** 33.33ms (1/30 second)
- **Result:** 1-frame accuracy

### Word-to-Phrase Mapping
The script collects words until the character count matches the expected phrase length, then assigns the phrase the start time of the first word and end time of the last word.

## ✅ Success Criteria

After running the analysis:
1. All 23 phrases have timing data
2. No frame overlaps between consecutive phrases
3. Total duration ≈ 14 seconds (420 frames)
4. Each phrase appears exactly when spoken in audio

## 🎬 Result

Video with phrases that appear **exactly** when spoken, synchronized to the actual audio waveform with 1-frame (33.33ms) precision.
