# 🎬 K-RISE Video Generation System

Automated video generation pipeline using Claude AI for script generation, OpenAI TTS for voice synthesis, and Remotion for video rendering.

## ✨ What's New in v3.1

**🎯 文節考慮型字幕セグメンテーション** - 日本語の自然な区切りを尊重した字幕分割

- ✅ Janome形態素解析による文節境界の自動検出
- ✅ 単語・文節の途中での不自然な分割を防止（例: 「伝説 / のプロデューサー」→「伝説」/「のプロデューサー」）
- ✅ 句読点を優先した自然な改行位置の決定
- ✅ 不自然な分割を80-90%削減

詳細は [`SEGMENTATION_V3.1_GUIDE.md`](SEGMENTATION_V3.1_GUIDE.md) または [`SEGMENTATION_V3.1_QUICK_REFERENCE.md`](SEGMENTATION_V3.1_QUICK_REFERENCE.md) を参照してください。

## ⚠️ Security Notice

**IMPORTANT**: This project uses API keys that must be kept secure:

- Never commit API keys to Git
- Use the `.env` file for storing keys (already in `.gitignore`)
- If a key is exposed, revoke it immediately on the respective platform

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Python dependencies (includes Janome for v3.1)
pip install -r requirements.txt

# Or install individually:
# pip install anthropic openai pydub openai-whisper janome requests python-dotenv

# Node.js dependencies
npm install
```

### 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your actual API keys:

```bash
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-anthropic-key-here
TIKTOK_ACCESS_TOKEN=your-tiktok-access-token-here
TIKTOK_OPEN_ID=your-tiktok-open-id-here
```

Get your API keys from:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys
- TikTok: https://developers.tiktok.com/

### 3. Set Environment Variables

**Windows (cmd.exe)**:
```bash
set OPENAI_API_KEY=sk-proj-...
set ANTHROPIC_API_KEY=sk-ant-api03-...
```

**Windows (PowerShell)**:
```bash
$env:OPENAI_API_KEY="sk-proj-..."
$env:ANTHROPIC_API_KEY="sk-ant-api03-..."
```

**macOS/Linux**:
```bash
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### 4. Generate and Upload Video

```bash
# 🎯 推奨: v3.1 文節考慮型パイプライン（最新）
python generate_video_data_master.py  # 音声生成 + 字幕同期（1文字単位 + 文節考慮）
npm run dev                            # プレビュー
npx remotion render                    # レンダリング

# または従来の方法:
# Step 1: Generate script with Claude AI
python make_script_auto.py

# Step 2: Generate audio and subtitles with OpenAI
python make_subtitles_auto.py

# Step 3: Render video with Remotion
npx remotion render

# Step 4: Upload to TikTok (optional)
python upload_tiktok_auto.py
```

Your video will be saved to `out/MyComp.mp4` 🎉

## 📖 Documentation

### 基本ガイド
- [`SETUP_GUIDE.md`](SETUP_GUIDE.md) - セットアップと基本的な使い方
- [`SEGMENTATION_V3.1_QUICK_REFERENCE.md`](SEGMENTATION_V3.1_QUICK_REFERENCE.md) - v3.1 クイックリファレンス ⭐ NEW

### 詳細ドキュメント
- [`SEGMENTATION_V3.1_GUIDE.md`](SEGMENTATION_V3.1_GUIDE.md) - v3.1 完全ガイド ⭐ NEW
- [`CHARACTER_LEVEL_SYNC_GUIDE.md`](CHARACTER_LEVEL_SYNC_GUIDE.md) - 1文字単位同期の詳細
- [`AUDIO_SYNC_USAGE_GUIDE.md`](AUDIO_SYNC_USAGE_GUIDE.md) - 音声同期の使い方
- [`MANUAL_SUBTITLE_EDITING_GUIDE.md`](MANUAL_SUBTITLE_EDITING_GUIDE.md) - 手動編集ガイド

## 🎨 Customization

- **Video content**: Edit [`video_config.json`](video_config.json)
- **Voice**: Change `TTS_VOICE` in [`make_subtitles_auto.py`](make_subtitles_auto.py)
- **Design**: Modify [`src/Composition.tsx`](src/Composition.tsx)
- **Resolution/FPS**: Edit [`src/Root.tsx`](src/Root.tsx)

## 📂 Project Structure

```
k-rise-video/
├── .env                      # API keys (DO NOT COMMIT)
├── .env.example              # API key template
├── video_config.json         # Video configuration
├── make_script_auto.py       # Script generation (Claude)
├── make_subtitles_auto.py    # Audio & subtitles (OpenAI)
├── upload_tiktok_auto.py     # TikTok upload (TikTok API)
├── public/                   # Assets and generated files
├── out/                      # Rendered videos
└── src/                      # Remotion components
```

## 🔒 Security Best Practices

1. **Never** hardcode API keys in source code
2. Always use environment variables or `.env` files
3. Keep `.env` in `.gitignore` (already configured)
4. Revoke exposed keys immediately
5. Use separate keys for development and production

## 📝 License

This project is for internal use. Handle API keys with care.

---

**Version**: 3.1 (Phrase-Aware Segmentation)
**Last Updated**: 2026-07-14
