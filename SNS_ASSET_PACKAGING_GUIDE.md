# 📦 SNS投稿用アセット自動パッケージングシステム

## 概要
レンダリングされた動画、投稿用キャプション、ハッシュタグを1つのフォルダに自動集約し、SNS投稿オペレーションを効率化するシステムです。

## フォルダ構造

```
dist_sns_outputs/
└── YYYY-MM-DD_vX.X/
    ├── output.mp4      # レンダリング済み動画
    ├── caption.txt     # 投稿用キャプション
    └── hashtags.txt    # ハッシュタグ一覧
```

## 使用方法

### 方法1: npmスクリプトで実行（推奨）

```bash
npm run package-sns
```

デフォルト設定で自動的にパッケージングが実行されます。

### 方法2: カスタムパラメータで実行

```bash
node package_sns_assets.js [version] [caption-file] [hashtags-file]
```

**例:**
```bash
# バージョンv3.3で実行
node package_sns_assets.js v3.3

# カスタムキャプション・ハッシュタグファイルを指定
node package_sns_assets.js v3.3 my_caption.md my_hashtags.md
```

## デフォルト設定

- **バージョン**: `v3.2`
- **キャプションファイル**: `tiktok_caption_updated.md`
- **ハッシュタグファイル**: `tiktok_captions_hashtags.md`
- **ソース動画**: `output.mp4`（プロジェクトルート）

## 実行例

```bash
$ npm run package-sns

📦 SNS投稿用アセットのパッケージングを開始します...

✅ dist_sns_outputs/2026-07-14_v3.2/ フォルダを作成しました
✅ 動画ファイルをコピーしました: dist_sns_outputs/2026-07-14_v3.2/output.mp4 (2.45 MB)
✅ キャプションファイルを作成しました: dist_sns_outputs/2026-07-14_v3.2/caption.txt
   内容プレビュー: 伝説のプロデューサー出口氏による直接審査。未来のK-POPスターを発掘する...
✅ ハッシュタグファイルを作成しました: dist_sns_outputs/2026-07-14_v3.2/hashtags.txt
   内容プレビュー: #KRISE #KPOPオーディション #ダンスワークショップ #RIIZE...

🎉 パッケージングが完了しました！
📁 出力先: dist_sns_outputs/2026-07-14_v3.2/

📋 生成されたファイル:
   - output.mp4
   - caption.txt
   - hashtags.txt

💡 このフォルダをクラウド同期してスマホから投稿できます！
```

## ワークフロー統合

### レンダリング後の自動パッケージング

1. 動画をレンダリング:
   ```bash
   npm run render
   ```

2. パッケージングを実行:
   ```bash
   npm run package-sns
   ```

### ワンライナーで実行

```bash
npm run render && npm run package-sns
```

## クラウド同期との連携

### Google Drive / Dropbox / OneDrive
`dist_sns_outputs/` フォルダをクラウドストレージの同期フォルダに配置することで、スマホから直接アクセス可能になります。

### 推奨フォルダ配置
```
C:/Users/user/Dropbox/k-rise-sns/
└── dist_sns_outputs/
    ├── 2026-07-14_v3.2/
    ├── 2026-07-15_v3.3/
    └── ...
```

## トラブルシューティング

### エラー: output.mp4 が見つかりません
→ 先に `npm run render` で動画をレンダリングしてください

### エラー: キャプション/ハッシュタグファイルが見つかりません
→ ファイル名を確認するか、カスタムパラメータで正しいファイルパスを指定してください

### フォルダが作成されない
→ プロジェクトルートで実行していることを確認してください

## カスタマイズ

[`package_sns_assets.js`](package_sns_assets.js:1) を編集することで、以下をカスタマイズできます:

- デフォルトバージョン番号
- ソースファイルのパス
- 出力フォルダ名の形式
- テキスト抽出ロジック

## 第2弾動画（2026-07-14）の成果物

✅ 以下のフォルダとファイルが生成されました:

```
dist_sns_outputs/2026-07-14_v3.2/
├── output.mp4     (13.7秒の動画)
├── caption.txt    (投稿用キャプション)
└── hashtags.txt   (9個のハッシュタグ)
```

**パス**: `c:/Users/user/Documents/k-rise-video/dist_sns_outputs/2026-07-14_v3.2/`

### caption.txt の内容
```
伝説のプロデューサー出口氏による直接審査。未来のK-POPスターを発掘するリアルオーディション、残された席はあとわずか。今すぐ公式LINEからエントリーせよ。
（※注意：プロフィールのリンクから公式LINEに登録して、今すぐエントリーシートを受け取ってください！）
```

### hashtags.txt の内容
```
#KRISE #KPOPオーディション #ダンスワークショップ #RIIZE #Sunburst #ダンス動画 #1文字シンクロ #出口プロデュース #限定募集
```

## 今後の展開

- [ ] TikTok API連携による自動投稿
- [ ] Instagram API連携
- [ ] 複数SNSへの同時投稿機能
- [ ] 投稿スケジューリング機能
- [ ] アナリティクス連携
