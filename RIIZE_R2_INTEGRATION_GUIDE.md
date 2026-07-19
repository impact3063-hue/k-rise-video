# 🎬 RIIZE Character-Level Sync × Cloudflare R2 統合ガイド

## 📋 概要

このガイドでは、RIIZE最新アルバム『II』をモチーフとした**1文字単位精密同期動画**をRemotion で生成し、Cloudflare R2バケットに自動アップロード、LINEへシームレスに配信するインフラの使用方法を説明します。

## ✅ 完了した実装

### 1. 環境変数設定（`.env`）
Cloudflare R2の接続キーを設定済み：

```env
CLOUDFLARE_ACCOUNT_ID="ce43db3e02cd26f119444ba2b8bbceed"
CLOUDFLARE_API_TOKEN="cfat_540LFv8nNj2qISM4vrjhjS1OnCdxmCS6Dgo18hBl0c570ab3"
R2_BUCKET_NAME="k-rise-video-storage"
```

### 2. Character-Level Syncデータ（`public/video-data-master.json`）
カラオケスタイルの字幕データを作成：
- **全体表示**: 最初から全テキストが表示
- **1文字ハイライト**: 歌い出しに合わせて1文字ずつゴールド（#FFD700）に変化
- **スケール効果**: ハイライト時に1.25倍に拡大

```json
{
  "metadata": {
    "syncMode": "character-level"
  },
  "subtitles": [
    {
      "text": "Get a Guitar",
      "characters": [
        { "char": "G", "startFrame": 20, "endFrame": 23 },
        { "char": "e", "startFrame": 24, "endFrame": 27 },
        ...
      ]
    }
  ]
}
```

### 3. R2アップロードユーティリティ（`src/utils/r2Upload.ts`）
- S3互換APIを使用したR2アップロード機能
- パブリックURL自動生成
- アップロード結果のログ出力

### 4. レンダリング＆アップロードスクリプト（`scripts/render-and-upload.mjs`）
ワンコマンドで以下を実行：
1. Remotionプロジェクトのバンドル
2. 動画レンダリング
3. R2へのアップロード
4. パブリックURL取得

## 🚀 使用方法

### ステップ1: Remotionプレビューで確認

現在、Remotion Studioが起動中です（`npm run dev`）。ブラウザで以下を確認してください：

1. **http://localhost:3000** にアクセス
2. 「AudioDrivenVideo」コンポジションを選択
3. Character-Level Syncが正しく動作することを確認：
   - "Get a Guitar" のテキストが表示される
   - フレーム20から1文字ずつゴールドにハイライト
   - ハイライト時に1.25倍にスケール

### ステップ2: 動画をレンダリング＆R2アップロード

新しいターミナルを開いて以下を実行：

```bash
npm run render-upload
```

このコマンドは以下を自動実行します：
- 📦 Remotionプロジェクトのバンドル
- 🎥 動画レンダリング（output.mp4）
- ☁️ Cloudflare R2へのアップロード
- 🔗 パブリックURL生成

### ステップ3: 出力結果の確認

レンダリング完了後、以下の情報が表示されます：

```
============================================================
📊 R2アップロード結果
============================================================
✅ ステータス: 成功
🔗 パブリックURL: https://k-rise-video-storage.r2.dev/videos/2026-07-15T04-18-00-000Z_output.mp4
📅 アップロード日時: 2026-07-15T04:18:00.000Z
📦 ファイルサイズ: 2.45 MB
============================================================

🎉 すべての処理が完了しました！

📺 動画URL: https://k-rise-video-storage.r2.dev/videos/2026-07-15T04-18-00-000Z_output.mp4

💡 このURLをLINE Botやその他のプラットフォームで使用できます。
```

## 🎨 Character-Level Syncのカスタマイズ

### フレームタイミングの調整

`public/video-data-master.json` の `characters` 配列を編集：

```json
{
  "char": "G",
  "startFrame": 20,  // ハイライト開始フレーム
  "endFrame": 23     // ハイライト終了フレーム
}
```

**計算式**: 30fps の場合、1秒 = 30フレーム

### スタイルのカスタマイズ

`style` オブジェクトを編集：

```json
{
  "style": {
    "fontFamily": "Impact",           // フォント
    "fontSize": 48,                   // サイズ
    "color": "#FFFFFF",               // デフォルト色（白）
    "highlightColor": "#FFD700",      // ハイライト色（ゴールド）
    "scaleFactor": 1.25               // スケール倍率
  }
}
```

### 複数行の歌詞を追加

`subtitles` 配列に新しい行を追加：

```json
{
  "subtitles": [
    {
      "id": "line-1",
      "text": "Get a Guitar",
      "startFrame": 20,
      "endFrame": 68,
      "characters": [...]
    },
    {
      "id": "line-2",
      "text": "次の歌詞",
      "startFrame": 90,
      "endFrame": 150,
      "characters": [
        { "char": "次", "startFrame": 90, "endFrame": 95 },
        { "char": "の", "startFrame": 96, "endFrame": 101 },
        ...
      ]
    }
  ]
}
```

## 🔧 トラブルシューティング

### Remotion Studioでエラーが出る場合

1. ターミナルで `Ctrl+C` を押してサーバーを停止
2. `npm run dev` で再起動

### R2アップロードが失敗する場合

1. `.env` ファイルの認証情報を確認
2. Cloudflare R2バケットが存在することを確認
3. APIトークンに適切な権限があることを確認

### レンダリングが遅い場合

`scripts/render-and-upload.mjs` で並列処理を有効化：

```javascript
await renderMedia({
  composition,
  serveUrl: bundleLocation,
  codec: "h264",
  outputLocation: outputPath,
  inputProps: {},
  concurrency: 4,  // 並列処理数を追加
  onProgress: ({ progress }) => {
    const percentage = (progress * 100).toFixed(1);
    process.stdout.write(`\r   進捗: ${percentage}%`);
  },
});
```

## 📦 NPMスクリプト一覧

| コマンド | 説明 |
|---------|------|
| `npm run dev` | Remotion Studioを起動（プレビュー） |
| `npm run render` | 動画をレンダリング（R2アップロードなし） |
| `npm run render-upload` | 動画をレンダリング＆R2アップロード |
| `npm run build` | Remotionプロジェクトをバンドル |

## 🌐 LINE Bot統合

R2からのパブリックURLを使用してLINE Botで動画を配信：

```javascript
// LINE Messaging API例
const message = {
  type: 'video',
  originalContentUrl: 'https://k-rise-video-storage.r2.dev/videos/xxx.mp4',
  previewImageUrl: 'https://your-thumbnail.jpg'
};
```

## 🎯 次のステップ

1. ✅ Remotion Studioでプレビュー確認
2. ✅ `npm run render-upload` で動画生成＆アップロード
3. 📱 生成されたURLをLINE Botに統合
4. 🚀 本番環境でテスト配信

## 📚 参考リンク

- [Remotion公式ドキュメント](https://www.remotion.dev/)
- [Cloudflare R2ドキュメント](https://developers.cloudflare.com/r2/)
- [AWS SDK for JavaScript v3](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/)

---

**作成日**: 2026-07-15  
**バージョン**: 1.0.0  
**プロジェクト**: K-RISE Video × RIIZE Character-Level Sync
