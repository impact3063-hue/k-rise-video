# 🎬 K-RISE 動画生成全自動化システム セットアップガイド

## 📋 概要

このシステムは、Claude AIで台本を生成し、OpenAI TTSで音声合成、Remotionで動画レンダリングを行う完全自動化された動画生成パイプラインです。

## 🔧 必要な依存関係

### Python依存関係

以下のPythonライブラリが必要です：

```bash
pip install anthropic openai pydub openai-whisper
```

各ライブラリの役割：
- `anthropic` - Claude APIで台本生成（新規追加）
- `openai` - TTS音声合成とWhisper字幕タイミング抽出
- `pydub` - 音声ファイルの結合と処理
- `openai-whisper` - 音声からの字幕タイミング自動抽出

### Node.js依存関係

プロジェクトルートで以下を実行：

```bash
npm install
```

主要な依存関係（package.jsonに記載済み）：
- `@remotion/cli` - 動画レンダリングCLI
- `remotion` - React-based動画フレームワーク
- `react` & `react-dom` - UIコンポーネント

## 🔑 APIキーの設定

**重要**: APIキーは絶対にGitにコミットしないでください。[`.env`](.env) ファイルは [`.gitignore`](.gitignore) に含まれています。

### 環境変数ファイルの作成

1. プロジェクトルートに `.env` ファイルを作成（[`.env.example`](.env.example) をコピー）：

```bash
# Windows (cmd.exe)
copy .env.example .env

# Windows (PowerShell) / macOS / Linux
cp .env.example .env
```

2. `.env` ファイルを開き、実際のAPIキーを設定：

```bash
# OpenAI API Key (for make_subtitles_auto.py)
# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here

# Anthropic API Key (for make_script_auto.py)
# Get your key from: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-anthropic-key-here
```

### 環境変数の読み込み

Pythonスクリプトは自動的に `.env` ファイルから環境変数を読み込みません。以下のいずれかの方法で設定してください：

**方法1: 手動で環境変数を設定（推奨）**

```bash
# Windows (cmd.exe)
set OPENAI_API_KEY=sk-proj-...
set ANTHROPIC_API_KEY=sk-ant-api03-...

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-proj-..."
$env:ANTHROPIC_API_KEY="sk-ant-api03-..."

# macOS/Linux
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

**方法2: python-dotenvを使用**

```bash
pip install python-dotenv
```

各Pythonスクリプトの先頭に以下を追加：
```python
from dotenv import load_dotenv
load_dotenv()
```

## 📝 設定ファイル

### video_config.json

動画の内容を制御する設定ファイル。新しい動画を作成する際は、このファイルを編集するだけでOK。

```json
{
  "industry": "K-POPオーディション",
  "theme": "BTSを日本進出させた伝説のプロデューサー出口氏が直々に審査してくれる特別なチャンス",
  "target_audience": "K-POPの世界を目指す人、オーディションで絶対に失敗したくない人",
  "tone_style": "熱量が高く、説得力があり、思わず最後まで見てしまうバズるトーン",
  "cta_text": "次は君の番かもしれない。応募はLINEから！プロフィールのリンクをチェックしてね！",
  "length_limit": "150文字〜180文字程度"
}
```

## 🚀 実行手順

### ステップ1: 台本生成（Claude AI）

```bash
python make_script_auto.py
```

**出力ファイル**:
- [`today_script.json`](today_script.json) - JSON形式の台本
- [`today_script.txt`](today_script.txt) - テキスト形式の台本（確認用）

**処理内容**:
- [`video_config.json`](video_config.json) から設定を読み込み
- Claude APIでバズる台本を自動生成
- CTAテキストを末尾に必ず含める

### ステップ2: 音声・字幕生成（OpenAI TTS + Whisper）

```bash
python make_subtitles_auto.py
```

**出力ファイル**:
- [`public/audio.mp3`](public/audio.mp3) - 完成した音声ファイル
- [`public/sample-video.json`](public/sample-video.json) - 字幕タイミングデータ

**処理内容**:
- 台本からCTA部分を自動抽出
- 本編とCTAを別々にTTS生成
- 無音を挟んで結合
- Whisperで本編の字幕タイミングを抽出
- CTAは音声長から直接フレーム計算（ズレ防止）

### ステップ3: 動画レンダリング（Remotion）

```bash
npx remotion render
```

**出力ファイル**:
- `out/MyComp.mp4` - 完成した動画ファイル

**処理内容**:
- [`src/Root.tsx`](src/Root.tsx) で動画の長さを自動計算
- [`src/Composition.tsx`](src/Composition.tsx) で字幕・音声・背景を合成
- 1080x1920 (縦型) 30fps でレンダリング

## 📂 ファイル構成

```
k-rise-video/
├── .env                       # APIキー設定（Gitに含めない）
├── .env.example               # APIキー設定テンプレート
├── .gitignore                 # Git除外設定
├── video_config.json          # 動画設定（編集可能）
├── make_script_auto.py        # 台本生成スクリプト（Claude）
├── make_subtitles_auto.py     # 音声・字幕生成スクリプト
├── today_script.json          # 生成された台本（自動生成）
├── today_script.txt           # 台本テキスト版（自動生成）
├── public/
│   ├── audio.mp3              # 完成音声（自動生成）
│   ├── sample-video.json      # 字幕データ（自動生成）
│   ├── bg-cyber.png           # 背景画像
│   ├── bg-music.mp3           # BGM
│   └── logo.png               # ロゴ
├── src/
│   ├── Root.tsx               # Remotion設定
│   └── Composition.tsx        # 動画コンポーネント
└── out/
    └── MyComp.mp4             # 完成動画（自動生成）
```

## 🎨 カスタマイズ

### 動画の内容を変更

[`video_config.json`](video_config.json) を編集して、ステップ1から再実行。

### 音声の声を変更

[`make_subtitles_auto.py`](make_subtitles_auto.py:20) の `TTS_VOICE` を変更：

```python
TTS_VOICE = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
```

### 動画のデザインを変更

[`src/Composition.tsx`](src/Composition.tsx) を編集：
- フォントサイズ: 68行目 `fontSize: 75`
- テキストカラー: 67行目 `color: "#fff"`
- 背景画像: 26行目 `bg-cyber.png`

### 動画の解像度・FPS

[`src/Root.tsx`](src/Root.tsx:15-17) を編集：

```tsx
fps={30}
width={1080}
height={1920}
```

## ⚠️ トラブルシューティング

### エラー: "anthropic library is not installed"

```bash
pip install anthropic
```

### エラー: "OPENAI_API_KEY が設定されていません"

環境変数を設定してください（上記「APIキーの設定」参照）。

### エラー: "Anthropic API key is not set"

環境変数 `ANTHROPIC_API_KEY` を設定してください。または `.env` ファイルに記載してください。

### セキュリティ警告

- **絶対にAPIキーをコードに直接書き込まないでください**
- `.env` ファイルは [`.gitignore`](.gitignore) に含まれており、Gitにコミットされません
- APIキーが漏洩した場合は、すぐに該当のプラットフォームで無効化してください
  - OpenAI: https://platform.openai.com/api-keys
  - Anthropic: https://console.anthropic.com/settings/keys

### エラー: "today_script.json が見つかりません"

ステップ1（`python make_script_auto.py`）を先に実行してください。

### 動画の長さがおかしい

[`make_subtitles_auto.py`](make_subtitles_auto.py:13) の `FPS` と [`src/Root.tsx`](src/Root.tsx:15) の `fps` が一致しているか確認してください（両方とも30）。

### 字幕が音声とズレる

Whisperの解析精度の問題です。[`make_subtitles_auto.py`](make_subtitles_auto.py:141) の `model` を `"base"` から `"small"` や `"medium"` に変更すると精度が上がります（処理時間は増加）。

## 📊 システムフロー

```
video_config.json
    ↓
make_script_auto.py (Claude API)
    ↓
today_script.json
    ↓
make_subtitles_auto.py (OpenAI TTS + Whisper)
    ↓
public/audio.mp3 + public/sample-video.json
    ↓
npx remotion render
    ↓
out/MyComp.mp4
```

## 🎯 完了確認

すべてのステップが成功すると、以下のファイルが生成されます：

- ✅ [`today_script.json`](today_script.json) - 台本データ
- ✅ [`today_script.txt`](today_script.txt) - 台本テキスト
- ✅ [`public/audio.mp3`](public/audio.mp3) - 音声ファイル
- ✅ [`public/sample-video.json`](public/sample-video.json) - 字幕データ
- ✅ `out/MyComp.mp4` - **完成動画** 🎉

---

**作成日**: 2026-07-11  
**バージョン**: 2.0 (Claude移行版)
