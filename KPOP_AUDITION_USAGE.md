# K-POPオーディション動画 - 使用方法

## 概要

このプロジェクトには、TikTok用のK-POPオーディション動画（パターン1：衝撃の事実訴求型）のRemotionコンポーネントが含まれています。

## ファイル構成

### 1. コンポーネントファイル
- **`src/KpopAuditionPattern1.tsx`** - メインのRemotionコンポーネント
- **`src/KpopAuditionRoot.tsx`** - Composition設定ファイル

### 2. データファイル
- **`public/kpop-audition-pattern1.json`** - テロップのタイミングとテキストデータ

### 3. 参考資料
- **`tiktok_kpop_audition_content.md`** - コンテンツ企画書

## テロップデータの構造

```json
[
  {
    "text": "表示するテキスト\n改行も可能",
    "startFrame": 0,
    "endFrame": 89,
    "style": "normal"
  }
]
```

### スタイルの種類

- **`normal`** - 通常のテロップ（黄色の光彩、フォントサイズ75px）
- **`bullet`** - 箇条書き用（金色の光彩、フォントサイズ65px）
- **`cta`** - CTA（行動喚起）用（ピンクの光彩、フォントサイズ70px）

## タイミング設定（30fps基準）

| セクション | 時間 | フレーム範囲 | 内容 |
|----------|------|------------|------|
| 冒頭 | 0〜3秒 | 0〜89 | BTSを日本に導いた... |
| メイン | 3〜7秒 | 90〜209 | 出口氏が直接審査！ |
| 箇条書き1 | 7〜9秒 | 210〜269 | ✨ 完全無料 |
| 箇条書き2 | 9〜11秒 | 270〜329 | ✨ 未経験OK |
| 箇条書き3 | 11〜12秒 | 330〜359 | ✨ 年齢制限なし |
| CTA | 12〜15秒 | 360〜449 | あなたの夢を叶える... |

## 使用方法

### 1. プレビュー

```bash
npm start
```

ブラウザで `http://localhost:3000` を開き、「KpopAuditionPattern1」を選択してプレビュー。

### 2. 動画のレンダリング

```bash
npx remotion render KpopAuditionPattern1 output.mp4
```

### 3. カスタマイズ

#### テロップの編集
`public/kpop-audition-pattern1.json` を編集：

```json
{
  "text": "新しいテキスト",
  "startFrame": 0,
  "endFrame": 90,
  "style": "normal"
}
```

#### Props のカスタマイズ
`src/KpopAuditionRoot.tsx` の `defaultProps` を編集：

```tsx
defaultProps={{
  subtitles: subtitlesPattern1,
  audioFile: "your-audio.mp3",      // 音声ファイル
  bgMusicFile: "your-bgm.mp3",      // BGM
  bgImageFile: "your-bg.png",       // 背景画像
  logoFile: "your-logo.png",        // ロゴ
}}
```

## アニメーション効果

### 1. スプリングアニメーション
テキストが表示される際に、バウンドするようなスプリング効果が適用されます。

```tsx
spring({
  frame: frame - currentSubtitle.startFrame,
  fps: 30,
  config: {
    damping: 100,      // 減衰率（高いほど早く止まる）
    stiffness: 200,    // バネの硬さ（高いほど速く動く）
    mass: 0.5,         // 質量（低いほど軽快）
  },
})
```

### 2. フェードイン
テキストが徐々に表示されます（0〜5フレーム）。

## ファイル配置

必要なメディアファイルを `public/` ディレクトリに配置：

```
public/
├── audio.mp3              # メイン音声
├── bg-music.mp3           # BGM
├── bg-cyber.png           # 背景画像
├── logo.png               # ロゴ
└── kpop-audition-pattern1.json  # テロップデータ
```

## 動画仕様

- **解像度**: 1080 x 1920 (TikTok縦型)
- **フレームレート**: 30fps
- **長さ**: 約15秒（450フレーム）

## トラブルシューティング

### テキストが表示されない
- `kpop-audition-pattern1.json` のフレーム範囲を確認
- `startFrame` と `endFrame` が正しく設定されているか確認

### 音声が再生されない
- `public/` ディレクトリに音声ファイルが存在するか確認
- ファイル名が `defaultProps` と一致しているか確認

### アニメーションが動かない
- ブラウザのキャッシュをクリア
- `npm start` を再起動

## 次のステップ

1. 音声ファイルを準備（ナレーション録音）
2. BGMを選定・配置
3. 背景画像とロゴを準備
4. テロップのタイミングを音声に合わせて微調整
5. プレビューで確認
6. 最終レンダリング

## 参考リンク

- [Remotion公式ドキュメント](https://www.remotion.dev/)
- [Remotion Spring API](https://www.remotion.dev/docs/spring)
- [Remotion Interpolate API](https://www.remotion.dev/docs/interpolate)
