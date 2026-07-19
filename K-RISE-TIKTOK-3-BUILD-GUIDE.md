# 🎬 K-RISE TikTok 3 ビルドガイド
## 1文字単位の超精密同期（Character-Level Sync）

このドキュメントは、K-RISE Dance Projectの3本目の動画をビルドする手順を説明します。

---

## 📋 実装内容

### ✅ 完了した実装

1. **Single Source of Truth の厳守**
   - [`public/video-data-master.json`](public/video-data-master.json) に全データを集約
   - プロジェクトID: `K-RISE-TikTok-3`
   - 動画の長さ: 15秒（450フレーム）

2. **1文字単位の超精密同期**
   - 各文字に個別のタイムスタンプを設定
   - フレーム単位での完全同期
   - 発音中の文字のみゴールド (#FFD700) + スケール1.2倍

3. **パフォーマンス最適化**
   - `useMemo` によるメモ化
   - フレーム単位の整数比較
   - 条件付きレンダリング

---

## 🎯 字幕データ

### メインコンテンツ

#### 字幕1: "本気で"
- **フレーム**: 30-50 (1.0秒 - 1.667秒)
- **文字数**: 3文字
- **Character-Level Sync**:
  - `本` → Frame 30-35 (0.167秒)
  - `気` → Frame 35-40 (0.166秒)
  - `で` → Frame 40-50 (0.334秒)

#### 字幕2: "目指すなら"
- **フレーム**: 51-90 (1.7秒 - 3.0秒)
- **文字数**: 5文字
- **Character-Level Sync**:
  - `目` → Frame 51-58 (0.233秒)
  - `指` → Frame 58-66 (0.267秒)
  - `す` → Frame 66-74 (0.267秒)
  - `な` → Frame 74-82 (0.266秒)
  - `ら` → Frame 82-90 (0.267秒)

#### CTA: "伝説のP出口氏が審査！..."
- **フレーム**: 390-450 (13.0秒 - 15.0秒)
- **スタイル**: フェードイン + スケール
- **内容**:
  ```
  伝説のP出口氏が審査！
  リアルオーディション開催
  詳細はプロフのLINEから
  ```

---

## 🎨 ビジュアル仕様

### カラオケスタイルのハイライト

```
発音中の文字:
  - 色: #FFD700 (ゴールド)
  - スケール: 1.2倍
  - グロー: 強い（20px + 40px）
  - トランジション: 0.05秒

未発音・発音済みの文字:
  - 色: rgba(255, 255, 255, 0.6) (白・半透明)
  - スケール: 1.0倍
  - グロー: 弱い（8px）
```

### レイアウト

- **位置**: 画面下部15%
- **セーフゾーン**: 左右7.5%ずつ（合計15%）
- **最大幅**: 85%
- **フォントサイズ**: 4.5rem
- **フォント**: Montserrat (英数字) + Noto Sans JP (日本語)
- **自動折り返し**: 有効

---

## 🚀 ビルド手順

### 1. プレビュー（開発サーバー起動）

```bash
cd C:\Users\user\Documents\k-rise-video
npm run dev
```

ブラウザで `http://localhost:3000` を開き、以下を確認：

1. コンポジション一覧から **`KRiseTikTok3`** を選択
2. 再生して字幕の同期を確認
3. 各文字がゴールドにハイライトされることを確認
4. スケールアニメーション（1.2倍）を確認

### 2. 動画のレンダリング

#### オプション1: Remotion Studio から直接レンダリング

1. Remotion Studio で `KRiseTikTok3` を選択
2. 右上の「Render」ボタンをクリック
3. 出力設定を確認:
   - **解像度**: 1080x1920 (TikTok縦型)
   - **FPS**: 30
   - **フレーム数**: 450 (15秒)
4. 「Start Render」をクリック

#### オプション2: コマンドラインでレンダリング

```bash
npx remotion render KRiseTikTok3 output.mp4
```

**高品質レンダリング（推奨）:**

```bash
npx remotion render KRiseTikTok3 output.mp4 --codec=h264 --crf=18 --audio-bitrate=320k
```

### 3. 出力ファイルの確認

レンダリング完了後、以下を確認：

- ✅ 動画の長さ: 15秒
- ✅ 解像度: 1080x1920
- ✅ 音声: ナレーション + BGM
- ✅ 字幕: 1文字単位で完全同期
- ✅ ハイライト: ゴールド (#FFD700) + スケール1.2倍

---

## 📁 ファイル構成

```
k-rise-video/
├── public/
│   ├── video-data-master.json    # 🎯 Single Source of Truth
│   ├── audio.mp3                 # ナレーション音声
│   ├── bg-music.mp3              # BGM
│   ├── bg-cyber.png              # 背景画像
│   └── logo.png                  # ロゴ
├── src/
│   ├── Root.tsx                  # コンポジション登録
│   ├── KRiseTikTok3.tsx          # 🎯 Video 3 コンポーネント
│   ├── AudioDrivenComposition.tsx # 汎用コンポーネント
│   └── utils/
│       └── textCleaner.ts        # テキスト処理ユーティリティ
└── K-RISE-TIKTOK-3-BUILD-GUIDE.md # このファイル
```

---

## 🎯 技術的特徴

### Single Source of Truth

すべてのデータは [`video-data-master.json`](public/video-data-master.json) から取得：

```typescript
import videoDataMaster from "../public/video-data-master.json";

const videoData = videoDataMaster as VideoData;

// 音声設定
const narrationVolume = videoData.audio.narration.volume;
const bgmVolume = videoData.audio.bgm.volume;

// 字幕データ
const subtitles = videoData.subtitles;
```

### Character-Level Synchronization

各文字に個別のタイムスタンプ：

```typescript
interface CharacterTimestamp {
  char: string;
  startFrame: number;
  endFrame: number;
  startTime: number;
  endTime: number;
  duration: number;
  wordIndex: number;
}
```

### パフォーマンス最適化

```typescript
// メモ化による再計算の削減
const renderCharacters = useMemo(() => {
  return subtitle.characters.map((charData, index) => {
    const isActive = frame >= charData.startFrame && frame <= charData.endFrame;
    // ...
  });
}, [subtitle, frame]);
```

---

## 🔧 トラブルシューティング

### 問題1: 字幕が表示されない

**原因**: データファイルの読み込みエラー

**解決策**:
```bash
# video-data-master.json の構文チェック
cat public/video-data-master.json | jq .
```

### 問題2: 音声が再生されない

**原因**: 音声ファイルが見つからない

**解決策**:
```bash
# 音声ファイルの存在確認
ls -la public/audio.mp3
ls -la public/bg-music.mp3
```

### 問題3: ハイライトが動作しない

**原因**: フレーム範囲の設定ミス

**解決策**:
- Remotion Studio のデバッグ情報を確認
- 画面右下に表示される「Frame: XX」を確認
- `video-data-master.json` の `startFrame` / `endFrame` を確認

---

## 📊 レンダリング設定（推奨）

### TikTok向け最適設定

```bash
npx remotion render KRiseTikTok3 k-rise-tiktok-3.mp4 \
  --codec=h264 \
  --crf=18 \
  --audio-bitrate=320k \
  --width=1080 \
  --height=1920 \
  --fps=30
```

### パラメータ説明

- `--codec=h264`: H.264コーデック（互換性最高）
- `--crf=18`: 品質設定（18 = 高品質、23 = デフォルト）
- `--audio-bitrate=320k`: 音声ビットレート（320kbps = 高品質）
- `--width=1080 --height=1920`: TikTok縦型フォーマット
- `--fps=30`: フレームレート（30fps = 滑らか）

---

## ✅ チェックリスト

レンダリング前の確認事項：

- [ ] `video-data-master.json` のデータが正しい
- [ ] `audio.mp3` が存在する
- [ ] `bg-music.mp3` が存在する
- [ ] `bg-cyber.png` が存在する
- [ ] `logo.png` が存在する
- [ ] Remotion Studio でプレビュー確認済み
- [ ] 字幕の同期が正確
- [ ] ハイライトが正しく動作
- [ ] CTAが最後に表示される

---

## 🎉 完成！

レンダリングが完了したら、以下を確認してください：

1. **動画の品質**: 1080x1920、30fps
2. **音声の品質**: ナレーション + BGM がクリア
3. **字幕の同期**: 1文字単位で完全同期
4. **ハイライト効果**: ゴールド + スケール1.2倍
5. **CTA表示**: 最後の2秒間に表示

---

## 📚 関連ドキュメント

- [CHARACTER_LEVEL_SYNC_GUIDE.md](CHARACTER_LEVEL_SYNC_GUIDE.md) - 1文字単位同期の詳細
- [REMOTION_AUDIO_SYNC_ARCHITECTURE.md](REMOTION_AUDIO_SYNC_ARCHITECTURE.md) - システムアーキテクチャ
- [KPOP_AUDITION_USAGE.md](KPOP_AUDITION_USAGE.md) - K-POPオーディション動画の使い方

---

**作成日**: 2026-07-15  
**バージョン**: 3.2.0  
**プロジェクト**: K-RISE Dance Project  
**動画番号**: 3本目  
**ステータス**: ✅ 実装完了・レンダリング準備完了
