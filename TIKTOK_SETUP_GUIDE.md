# 🎵 TikTok API セットアップガイド

このガイドでは、`upload_tiktok_auto.py` を使用してTikTokに動画を自動アップロードするための設定方法を説明します。

## 📋 前提条件

- TikTokアカウント（個人または企業）
- TikTok Developer アカウント
- Python 3.7以上
- 必要なPythonパッケージ: `requests`, `python-dotenv`

## 🚀 セットアップ手順

### ステップ 1: TikTok Developer アカウントの作成

1. [TikTok for Developers](https://developers.tiktok.com/) にアクセス
2. 「Get Started」をクリック
3. TikTokアカウントでログイン
4. 開発者登録フォームに必要事項を入力

### ステップ 2: アプリケーションの作成

1. [Developer Portal](https://developers.tiktok.com/apps) にログイン
2. 「Create an app」をクリック
3. アプリ情報を入力:
   - **App name**: K-RISE Video Uploader（任意の名前）
   - **App type**: Web app
   - **Category**: Content & Publishing
4. 「Create」をクリック

### ステップ 3: Content Posting API の有効化

1. 作成したアプリの詳細ページを開く
2. 「Products」タブに移動
3. 「Content Posting API」を探して「Add product」をクリック
4. 利用規約に同意して有効化

### ステップ 4: OAuth 2.0 設定

1. アプリの「Settings」タブを開く
2. 「Redirect URI」を設定:
   ```
   http://localhost:8000/callback
   ```
3. 「Scopes」で以下の権限を選択:
   - `video.upload` - 動画アップロード権限
   - `video.publish` - 動画公開権限
4. 「Save」をクリック

### ステップ 5: アクセストークンの取得

#### 方法 A: 手動で取得（推奨）

1. アプリの「Client Key」と「Client Secret」をコピー
2. 以下のURLにアクセス（Client Keyを置き換え）:
   ```
   https://www.tiktok.com/v2/auth/authorize?client_key=YOUR_CLIENT_KEY&scope=video.upload,video.publish&response_type=code&redirect_uri=http://localhost:8000/callback
   ```
3. TikTokアカウントでログインして認証
4. リダイレクトされたURLから `code` パラメータをコピー
5. 以下のコマンドでアクセストークンを取得:
   ```bash
   curl -X POST "https://open.tiktokapis.com/v2/oauth/token/" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_key=YOUR_CLIENT_KEY" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "code=YOUR_AUTH_CODE" \
     -d "grant_type=authorization_code" \
     -d "redirect_uri=http://localhost:8000/callback"
   ```

#### 方法 B: Pythonスクリプトで取得

プロジェクトに含まれる `get_token.py` を使用:

```bash
python get_token.py
```

画面の指示に従ってブラウザで認証を完了してください。

### ステップ 6: 環境変数の設定

1. `.env` ファイルを開く
2. 取得した情報を追加:
   ```bash
   TIKTOK_ACCESS_TOKEN=act.your-access-token-here
   TIKTOK_OPEN_ID=your-open-id-here
   ```

### ステップ 7: 動作確認

```bash
# 動画を生成
python make_script_auto.py
python make_subtitles_auto.py
npx remotion render

# TikTokにアップロード
python upload_tiktok_auto.py
```

## 🔧 トラブルシューティング

### エラー: "TIKTOK_ACCESS_TOKEN が設定されていません"

**原因**: `.env` ファイルにアクセストークンが設定されていない

**解決方法**:
1. `.env` ファイルを確認
2. `TIKTOK_ACCESS_TOKEN=` の後に正しいトークンを貼り付け
3. ファイルを保存

### エラー: "動画ファイルが見つかりません"

**原因**: 動画がまだレンダリングされていない

**解決方法**:
```bash
npx remotion render
```

### エラー: "アップロード初期化に失敗しました (401)"

**原因**: アクセストークンが無効または期限切れ

**解決方法**:
1. アクセストークンを再取得
2. `.env` ファイルを更新
3. トークンの有効期限を確認（通常24時間）

### エラー: "アップロード初期化に失敗しました (403)"

**原因**: 必要な権限がない

**解決方法**:
1. TikTok Developer Portalでアプリの権限を確認
2. `video.upload` と `video.publish` スコープが有効か確認
3. 必要に応じて再認証

### エラー: "動画ファイルが大きすぎます"

**原因**: 動画サイズが500MBを超えている

**解決方法**:
1. Remotionの設定で解像度を下げる
2. 動画の長さを短くする
3. ビットレートを調整

## 📝 重要な注意事項

### アクセストークンの有効期限

- **短期トークン**: 24時間で期限切れ
- **長期トークン**: リフレッシュトークンで更新可能（最大1年）

定期的にトークンを更新する必要があります。

### アップロード制限

- **ファイルサイズ**: 最大 500MB
- **動画長**: 最大 10分（アカウントによる）
- **フォーマット**: MP4, MOV, WEBM
- **解像度**: 最小 540x960、最大 4096x4096

### プライバシー設定

デフォルトでは `SELF_ONLY`（自分のみ）に設定されています。

公開する場合は [`upload_tiktok_auto.py`](upload_tiktok_auto.py:267) の以下の行を変更:

```python
'privacy_level': 'PUBLIC_TO_EVERYONE',  # 公開
```

オプション:
- `SELF_ONLY` - 自分のみ
- `MUTUAL_FOLLOW_FRIENDS` - 相互フォロワー
- `FOLLOWER_OF_CREATOR` - フォロワー
- `PUBLIC_TO_EVERYONE` - 全体公開

## 🔐 セキュリティのベストプラクティス

1. **アクセストークンを共有しない**
   - トークンは個人情報と同等に扱う
   - Gitにコミットしない（`.gitignore` で保護済み）

2. **定期的にトークンを更新**
   - 古いトークンは無効化
   - 新しいトークンを生成

3. **最小権限の原則**
   - 必要な権限のみを要求
   - 不要な権限は削除

4. **環境変数を使用**
   - ハードコードしない
   - `.env` ファイルで管理

## 📚 参考リンク

- [TikTok for Developers](https://developers.tiktok.com/)
- [Content Posting API Documentation](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [OAuth 2.0 Guide](https://developers.tiktok.com/doc/oauth-user-access-token-management)
- [API Reference](https://developers.tiktok.com/doc/content-posting-api-reference-upload-video)

## 💡 ヒント

### 自動化のための長期トークン

本番環境では、リフレッシュトークンを使用して自動的にアクセストークンを更新することをお勧めします。

### バッチアップロード

複数の動画を一度にアップロードする場合は、スクリプトをループで実行できます:

```python
for video_file in video_files:
    upload_video(video_file)
    time.sleep(60)  # レート制限を避けるため
```

### ログの保存

アップロード履歴を保存する場合は、ログファイルに出力を記録:

```bash
python upload_tiktok_auto.py >> upload_log.txt 2>&1
```

## 🆘 サポート

問題が解決しない場合:

1. [TikTok Developer Community](https://developers.tiktok.com/community/)
2. [GitHub Issues](https://github.com/your-repo/issues)
3. TikTok Developer Support（アプリダッシュボードから）

---

**最終更新**: 2026-07-12  
**バージョン**: 1.0
