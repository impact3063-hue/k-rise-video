# 🎬 K-RISE RIIZE Dance Challenge System - 完全実装ガイド

## 📋 概要

**プロジェクト名**: K-RISE Dance Project - RIIZE 2026 Comeback Edition  
**バージョン**: 6.0.0-RIIZE  
**実装日**: 2026年7月18日  
**目的**: TikTok/Reels バズ → LINE登録 → リアルオーディション集客

---

## 🎯 マーケティング背景

### 現在のトレンド状況（2026年7月）
- **ターゲット**: RIIZE 最新カムバック楽曲のダンスチャレンジ
- **プラットフォーム**: TikTok / Instagram Reels
- **熱量**: 圧倒的なトレンドジャック中
- **コンバージョンゴール**: 公式LINE登録 → リアルオーディション参加

### コンバージョンファネル
```
TikTok/Reels 視聴
    ↓
プロフィール訪問
    ↓
LINE登録（CTA）
    ↓
限定ワークショップ予約
    ↓
リアルオーディション参加
```

---

## 🏗️ システムアーキテクチャ

### Single Source of Truth
すべてのデータは [`video-data-master-riize.json`](public/video-data-master-riize.json) から駆動されます。

```
video-data-master-riize.json
    ↓
KRiseTikTok3Enhanced.tsx
    ↓
Remotion レンダリング
    ↓
TikTok/Reels 自動投稿
```

---

## 📁 ファイル構成

### 新規作成ファイル

1. **`public/video-data-master-riize.json`**
   - RIIZE ダンスチャレンジ用のマスターデータ
   - 1文字単位の超精密同期タイムスタンプ
   - LINE CTA メタデータ完備

2. **`src/KRiseTikTok3Enhanced.tsx`**
   - 強化版カラオケコンポーネント
   - ゴールドグロー強化（5層シャドウ）
   - ラスト3秒固定のLINE CTA専用レイヤー

---

## 🎨 主要機能

### 1. Character-Level Karaoke Sync（1文字単位同期）

#### データ構造
```json
{
  "characters": [
    {
      "char": "R",
      "startTime": 0.0,
      "endTime": 0.15,
      "startFrame": 0,
      "endFrame": 5,
      "duration": 0.15,
      "wordIndex": 0
    }
  ]
}
```

#### 視覚効果
- **未発音**: 白（半透明 65%）
- **発音中**: ゴールド (#FFD700) + スケール1.2倍 + 5層グロー
- **発音済**: 白（半透明 65%）

#### グロー仕様（強化版）
```css
textShadow: 
  0px 0px 25px rgba(255,215,0,1),      /* 内側グロー */
  0px 0px 45px rgba(255,215,0,0.9),    /* 中間グロー */
  0px 0px 60px rgba(255,215,0,0.7),    /* 外側グロー */
  0px 4px 15px rgba(0,0,0,0.95),       /* ドロップシャドウ */
  0px 0px 80px rgba(255,215,0,0.5)     /* 最外周グロー */
```

---

### 2. Dedicated LINE CTA Layer（ラスト3秒固定）

#### 自動表示タイミング
```typescript
const ctaDuration = 3.0; // 秒
const ctaFrames = Math.floor(ctaDuration * fps);
const ctaStartFrame = totalFrames - ctaFrames;
```

#### 表示内容
```
続きはプロフィールURLから
LINEへ登録

限定ダンスワークショップ
受付中
```

#### 視覚効果
- **フェードイン**: 20フレーム（0.67秒）
- **スケールアップ**: 0.85 → 1.0
- **パルスアニメーション**: 1.0 ↔ 1.05（30フレーム周期）
- **ボーダー**: 3px ゴールド（80%透明度）
- **ボックスシャドウ**: ゴールドグロー + インセットグロー
- **矢印アニメーション**: バウンス（下向き▼）

---

## 🚀 使用方法

### Step 1: データファイルの準備

RIIZE用のデータを使用する場合：
```bash
# video-data-master-riize.json を video-data-master.json にコピー
cd k-rise-video/public
copy video-data-master-riize.json video-data-master.json
```

### Step 2: コンポーネントの登録

[`src/Root.tsx`](src/Root.tsx) に新しいコンポジションを追加：

```typescript
import { KRiseTikTok3Enhanced } from "./KRiseTikTok3Enhanced";

// Composition登録
<Composition
  id="KRiseTikTok3Enhanced"
  component={KRiseTikTok3Enhanced}
  durationInFrames={450}  // 15秒 @ 30fps
  fps={30}
  width={1080}
  height={1920}
  defaultProps={{}}
/>
```

### Step 3: プレビュー

```bash
npm start
```

ブラウザで `http://localhost:3000` を開き、`KRiseTikTok3Enhanced` を選択。

### Step 4: レンダリング

```bash
npx remotion render KRiseTikTok3Enhanced output-riize.mp4
```

### Step 5: TikTok/Reels 投稿

生成された `output-riize.mp4` を使用：

```bash
# TikTok自動投稿（既存スクリプト使用）
python upload_tiktok_auto.py
```

#### 推奨キャプション
```
RIIZEの新曲ダンスチャレンジに挑戦！🔥
未経験でもプロが直接指導します💪

続きはプロフィールのLINEから👇
限定ワークショップ受付中🎵

#RIIZE #RIIZEChallenge #KRISEDanceProject 
#ダンスチャレンジ #KPOP #ダンスオーディション
```

---

## 🎛️ カスタマイズガイド

### 歌詞・セリフの変更

[`video-data-master-riize.json`](public/video-data-master-riize.json) の `subtitles` セクションを編集：

```json
{
  "id": "line-1",
  "text": "あなたの新しい歌詞",
  "startFrame": 0,
  "endFrame": 75,
  "characters": [
    {
      "char": "あ",
      "startTime": 0.0,
      "endTime": 0.15,
      "startFrame": 0,
      "endFrame": 5
    }
    // ... 1文字ずつ定義
  ]
}
```

### CTA メッセージの変更

#### 方法1: データ駆動（推奨）
`video-data-master-riize.json` の `content.cta` を編集：

```json
{
  "content": {
    "cta": {
      "message": "あなたのCTAメッセージ\n複数行対応",
      "startTime": 12.0,
      "duration": 3.0,
      "action": "LINE Registration",
      "urgency": "high"
    }
  }
}
```

#### 方法2: コンポーネント直接編集
[`src/KRiseTikTok3Enhanced.tsx`](src/KRiseTikTok3Enhanced.tsx) の `DedicatedLINECTA` コンポーネント内のテキストを変更。

### ゴールドカラーの変更

`highlightColor` を変更：
```json
{
  "style": {
    "highlightColor": "#FF1493"  // 例: ピンク
  }
}
```

### スケールファクターの調整

```json
{
  "style": {
    "scaleFactor": 1.3  // デフォルト: 1.2
  }
}
```

---

## 🔧 技術仕様

### パフォーマンス最適化

1. **useMemo による文字レンダリングのメモ化**
   ```typescript
   const renderCharacters = useMemo(() => {
     // 文字レンダリングロジック
   }, [subtitle, frame]);
   ```

2. **半開区間判定による境界フレーム問題の解決**
   ```typescript
   const isActive = frame >= charStartFrame && frame < charEndFrame;
   ```

3. **Rules of Hooks 遵守**
   - すべてのHooksを条件分岐の外で実行
   - 表示判定は最後に実施

### レスポンシブデザイン

```css
fontSize: "clamp(3.2rem, 9.5vw, 6rem)"
```

- **最小**: 3.2rem
- **推奨**: 9.5vw（ビューポート幅の9.5%）
- **最大**: 6rem

---

## 📊 データスキーマ仕様

### 必須フィールド

```typescript
interface VideoData {
  version: string;                    // "6.0.0-RIIZE"
  metadata: {
    projectId: string;
    fps: number;                      // 30
    duration: number;                 // 15.0
    totalFrames: number;              // 450
    syncMode: "character-level";
  };
  subtitles: Subtitle[];
  audio: {
    narration: { file: string; volume: number; };
    bgm: { file: string; volume: number; loop: boolean; };
  };
}
```

### Character Timestamp 仕様

```typescript
interface CharacterTimestamp {
  char: string;           // 1文字
  startTime: number;      // 秒単位
  endTime: number;        // 秒単位
  startFrame: number;     // フレーム単位
  endFrame: number;       // フレーム単位
  duration: number;       // 秒単位
  wordIndex: number;      // 単語インデックス
}
```

---

## 🎯 マーケティング活用

### ハッシュタグ戦略

データに含まれる推奨ハッシュタグ：
```json
{
  "marketing": {
    "hashtags": [
      "#RIIZE",
      "#RIIZEChallenge",
      "#KRISEDanceProject",
      "#ダンスチャレンジ",
      "#KPOP",
      "#ダンスオーディション"
    ]
  }
}
```

### A/Bテスト推奨項目

1. **CTA表示タイミング**
   - ラスト3秒（現在）
   - ラスト4秒
   - ラスト2秒

2. **ゴールドカラー**
   - #FFD700（現在）
   - #FFA500（オレンジゴールド）
   - #FF69B4（ピンクゴールド）

3. **スケールファクター**
   - 1.2（現在）
   - 1.15（控えめ）
   - 1.3（強調）

---

## 🐛 トラブルシューティング

### 問題: 文字が2つ同時にゴールドになる

**原因**: 境界フレームでの重複判定

**解決策**: 半開区間判定を使用（既に実装済み）
```typescript
const isActive = frame >= charStartFrame && frame < charEndFrame;
```

### 問題: CTAが表示されない

**チェック項目**:
1. `totalFrames` が正しく設定されているか
2. `fps` が30に設定されているか
3. `durationInFrames` が450（15秒 @ 30fps）になっているか

### 問題: グローが弱い

**解決策**: `renderParams.glow` を調整
```json
{
  "renderParams": {
    "glow": 1.5  // デフォルト: 1.2
  }
}
```

---

## 📈 次のステップ

### Phase 1: データ生成自動化
既存の Python スクリプトを RIIZE 仕様に対応：
```bash
python generate_video_data_master_v3.2.py --theme riize
```

### Phase 2: 音声同期の精度向上
Whisper API を使用した自動タイムスタンプ生成：
```bash
python make_subtitles_auto.py --input audio.mp3 --output video-data-master-riize.json
```

### Phase 3: TikTok Analytics 連携
投稿後のパフォーマンス追跡：
- 視聴回数
- プロフィールクリック率
- LINE登録コンバージョン率

---

## 🔗 関連ドキュメント

- [CHARACTER_LEVEL_SYNC_GUIDE.md](CHARACTER_LEVEL_SYNC_GUIDE.md) - 1文字同期の詳細
- [AUDIO_SYNC_USAGE_GUIDE.md](AUDIO_SYNC_USAGE_GUIDE.md) - 音声同期ガイド
- [TIKTOK_PRODUCTION_QUICK_START.md](TIKTOK_PRODUCTION_QUICK_START.md) - TikTok投稿ガイド
- [LINE_BOT_SETUP_GUIDE.md](LINE_BOT_SETUP_GUIDE.md) - LINE Bot設定

---

## 📝 変更履歴

### v6.0.0-RIIZE (2026-07-18)
- ✨ RIIZE ダンスチャレンジ対応
- ✨ ゴールドグロー5層強化
- ✨ ラスト3秒固定LINE CTA専用レイヤー実装
- ✨ パルスアニメーション追加
- ✨ マーケティングメタデータ追加
- 🐛 境界フレーム2文字同時ゴールド問題を半開区間で解決

### v5.0.0 (2026-07-17)
- ✨ Character-level sync 実装
- ✨ Single Source of Truth 確立

---

## 👥 サポート

質問・問題がある場合：
1. このドキュメントのトラブルシューティングセクションを確認
2. 既存の関連ドキュメントを参照
3. `video-data-master-riize.json` のスキーマを確認

---

## 🎉 成功の鍵

1. **データ駆動**: すべてを JSON で管理
2. **視認性**: 未発音文字も常に表示（半透明）
3. **強調**: 発音中のみゴールド + グロー + スケール
4. **CTA固定**: ラスト3秒は必ずLINE誘導
5. **トレンド活用**: RIIZE の熱量を K-RISE へ流し込む

---

**🚀 世界標準動画システムで、SNSバズからリアルオーディションへの完全動線を構築しましょう！**
