# 🚀 TikTok Production環境 セットアップガイド

本番環境（Production）でTikTok APIを使用するための完全ガイドです。

---

## 📋 目次

1. [前提条件](#前提条件)
2. [Developer Portalの設定](#developer-portalの設定)
3. [環境変数の設定](#環境変数の設定)
4. [認証フロー](#認証フロー)
5. [動画アップロード](#動画アップロード)
6. [トラブルシューティング](#トラブルシューティング)

---

## 🎯 前提条件

### 必要なもの

- ✅ TikTok Developer アカウント
- ✅ 本番用のTikTokアカウント（実際に投稿するアカウント）
- ✅ App Review の承認（video.upload/video.publish を使用する場合）
- ✅ Python 3.7以上
- ✅ 必要なPythonパッケージ（`pip install -r requirements.txt`）

### Sandbox環境との違い

| 項目 | Sandbox | Production |
|------|---------|------------|
| Client Key | `sbaw` で始まる | `aw` で始まる |
| API Base URL | `sandbox-open.tiktokapis.com` | `open.tiktokapis.com` |
| 認証URL | 共通 (`www.tiktok.com/v2/auth/authorize/`) | 共通 |
| App Review | 不要 | **必須** |
| 投稿先 | テスト環境 | **本番TikTok** |
| テストユーザー | 必要 | 不要（実アカウント） |

---

## 🔧 Developer Portalの設定

### 1. TikTok Developer Portalにアクセス

https://developers.tiktok.com/apps

### 2. アプリを選択または作成

既存のアプリを選択するか、新しいアプリを作成します。

### 3. **Production タブ**を選択

⚠️ **重要**: Sandboxタブではなく、**Productionタブ**を選択してください。

### 4. Client Credentials を確認

```
Client Key:    aw*************** (本番用は 'aw' で始まる)
Client Secret: ****************
```

⚠️ **注意**: `sbaw` で始まる場合はSandbox用です。Productionタブで確認してください。

### 5. Redirect URI を登録

**Production タブ**の「Redirect URI」セクションで以下を登録:

```
https://google.com
```

または、独自のコールバックURLを使用する場合はそのURLを登録してください。

### 6. Scopes（権限）を設定

**Production タブ**の「Scopes」セクションで以下を有効化:

- ✅ `user.info.basic` - ユーザー基本情報（必須）
- ✅ `video.upload` - 動画アップロード
- ✅ `video.publish` - 動画公開

### 7. App Review を申請

⚠️ **重要**: `video.upload` と `video.publish` を使用するには、App Reviewの承認が必要です。

#### App Review 申請手順:

1. Developer Portalで「App Review」セクションに移動
2. 使用したいスコープ（`video.upload`, `video.publish`）を選択
3. アプリの用途を説明
4. デモ動画やスクリーンショットを提供
5. 申請を送信

#### 承認までの期間:
- 通常: 1-2週間
- 場合によっては数日～1ヶ月

#### App Review なしで使用できるスコープ:
- `user.info.basic` のみ（ユーザー情報の取得のみ可能）

---

## 🔐 環境変数の設定

### `.env` ファイルを編集

プロジェクトルートの `.env` ファイルに以下を追加:

```bash
# TikTok Production Credentials
TIKTOK_CLIENT_KEY_PROD=aw***************  # 本番用Client Key ('aw'で始まる)
TIKTOK_CLIENT_SECRET_PROD=****************  # 本番用Client Secret
TIKTOK_REDIRECT_URI=https://google.com

# TikTok Tokens (認証後に自動設定)
TIKTOK_ACCESS_TOKEN=
TIKTOK_REFRESH_TOKEN=
TIKTOK_TOKEN_EXPIRES_IN=
TIKTOK_OPEN_ID=
```

### 環境変数の説明

| 変数名 | 説明 | 取得方法 |
|--------|------|----------|
| `TIKTOK_CLIENT_KEY_PROD` | 本番用Client Key | Developer Portal > Production タブ |
| `TIKTOK_CLIENT_SECRET_PROD` | 本番用Client Secret | Developer Portal > Production タブ |
| `TIKTOK_REDIRECT_URI` | リダイレクトURI | Developer Portalに登録したURI |
| `TIKTOK_ACCESS_TOKEN` | アクセストークン | 認証フロー後に取得 |
| `TIKTOK_REFRESH_TOKEN` | リフレッシュトークン | 認証フロー後に取得 |
| `TIKTOK_OPEN_ID` | ユーザーID | 認証フロー後に取得 |

⚠️ **セキュリティ注意**:
- `.env` ファイルは `.gitignore` に含めてください
- Client SecretやTokenは絶対に公開しないでください

---

## 🔑 認証フロー

### ステップ1: 認証URLを生成

```bash
python generate_auth_url.py
```

#### 出力例:
```
🚀 TikTok Production 認証URL生成
================================================================================
✅ Production認証URLを生成しました:
https://www.tiktok.com/v2/auth/authorize/?client_key=aw***&scope=user.info.basic,video.upload,video.publish&response_type=code&redirect_uri=https://google.com&state=random_state
```

### ステップ2: ブラウザで認証

1. 生成されたURLをコピー
2. ブラウザで開く
3. TikTokアカウントでログイン
4. アプリの権限を承認

### ステップ3: リダイレクトURLをコピー

承認後、以下のようなURLにリダイレクトされます:

```
https://google.com/?code=ABC123XYZ...&state=random_state&scopes=user.info.basic,video.upload,video.publish
```

このURL全体をコピーしてください。

### ステップ4: トークンを取得

```bash
python get_token.py
```

1. 認証URLが表示されます（ステップ1と同じ）
2. プロンプトでリダイレクトURLを貼り付け
3. アクセストークンが取得されます

#### 成功時の出力:
```
✅ トークン取得成功!

【ステップ3】 .envファイルを更新してください
--------------------------------------------------------------------------------
TIKTOK_ACCESS_TOKEN=act.*********************
TIKTOK_REFRESH_TOKEN=rft.*********************
TIKTOK_TOKEN_EXPIRES_IN=86400
TIKTOK_OPEN_ID=-000*********************
```

### ステップ5: `.env` ファイルを更新

取得したトークン情報を `.env` ファイルに追加:

```bash
TIKTOK_ACCESS_TOKEN=act.*********************
TIKTOK_REFRESH_TOKEN=rft.*********************
TIKTOK_TOKEN_EXPIRES_IN=86400
TIKTOK_OPEN_ID=-000*********************
```

---

## ✅ 接続テスト

トークンが正しく設定されているか確認:

```bash
python test_tiktok_connection.py
```

### 成功時の出力:
```
TikTok Production API 接続テスト
================================================================================
環境変数チェック
--------------------------------------------------------------------------------
  ✓ TIKTOK_CLIENT_KEY: aw***
    ✓ Production用のClient Key (正常)
  ✓ TIKTOK_ACCESS_TOKEN: act.***...
  ✓ TIKTOK_OPEN_ID: -000***

ユーザー情報取得テスト
--------------------------------------------------------------------------------
  ✓ API接続成功！

動画アップロード権限テスト
--------------------------------------------------------------------------------
  ✓ 動画アップロード権限あり！

✓ テスト完了: すべて正常
🚀 Production環境への接続が確認できました
```

---

## 🎬 動画アップロード

### 前提条件

1. ✅ 動画ファイルが生成されている（`out/MyComp.mp4`）
2. ✅ スクリプトファイルが存在する（`today_script.json`）
3. ✅ アクセストークンが有効
4. ✅ App Reviewが承認されている

### アップロード実行

```bash
python upload_tiktok_auto.py
```

### 確認プロンプト

⚠️ 本番環境への投稿前に確認が表示されます:

```
⚠️  本番環境への投稿を続行しますか？
   この動画は実際のTikTokアカウントに投稿されます。
続行する場合は 'yes' と入力してください:
```

`yes` と入力して続行してください。

### 成功時の出力:

```
🎉 TikTok Production環境へのアップロードが完了しました！
================================================================================
アップロード結果:
{
  "publish_id": "***",
  "status": "uploaded"
}

📱 本番環境に投稿されました
   実際のTikTokアカウントで動画が確認できます
```

### 動画の確認

TikTok Creator Centerで動画を確認:
https://www.tiktok.com/creator-center/content

---

## 🔄 トークンのリフレッシュ

アクセストークンは24時間で期限切れになります。

### 自動リフレッシュ

```bash
python refresh_tiktok_token.py
```

または

```bash
python refresh_tiktok_token_minimal.py
```

### リフレッシュ後

新しいトークンを `.env` ファイルに更新してください。

---

## 🐛 トラブルシューティング

### エラー: `invalid_client`

**原因**: Client KeyまたはClient Secretが間違っている

**解決方法**:
1. Developer Portal > **Production タブ**で正しい値を確認
2. `.env` ファイルの `TIKTOK_CLIENT_KEY_PROD` と `TIKTOK_CLIENT_SECRET_PROD` を更新
3. Client Keyが `aw` で始まることを確認（`sbaw` はSandbox用）

### エラー: `invalid_grant`

**原因**: 認証コードが無効または期限切れ

**解決方法**:
1. 認証コードは1回のみ使用可能
2. 認証コードは数分で期限切れ
3. `python generate_auth_url.py` を再実行して新しいコードを取得

### エラー: `redirect_uri_mismatch`

**原因**: Redirect URIが一致しない

**解決方法**:
1. Developer Portal > **Production タブ** > Redirect URI を確認
2. `.env` の `TIKTOK_REDIRECT_URI` と一致させる
3. スクリプトで使用しているRedirect URIと一致させる

### エラー: `insufficient_permissions` または `scope_not_authorized`

**原因**: App Reviewが承認されていない

**解決方法**:
1. Developer Portal > App Review を確認
2. `video.upload` と `video.publish` が承認されているか確認
3. 承認されていない場合は申請を送信
4. 承認されるまで待つ（1-2週間）

### エラー: Sandbox用のClient Keyを使用している

**症状**: Client Keyが `sbaw` で始まる

**解決方法**:
1. Developer Portal > **Production タブ**を選択
2. Production用のClient Key（`aw` で始まる）を取得
3. `.env` ファイルを更新

### 動画がアップロードされない

**確認事項**:
1. ✅ `test_tiktok_connection.py` が成功するか確認
2. ✅ 動画ファイル（`out/MyComp.mp4`）が存在するか確認
3. ✅ 動画サイズが500MB以下か確認
4. ✅ App Reviewが承認されているか確認
5. ✅ アクセストークンが期限切れでないか確認

---

## 📚 重要なポイント

### ✅ DO（推奨）

- ✅ **Production タブ**で設定を確認
- ✅ Client Keyが `aw` で始まることを確認
- ✅ App Reviewを申請・承認を待つ
- ✅ トークンを定期的にリフレッシュ
- ✅ `.env` ファイルをGit管理から除外
- ✅ 本番投稿前に確認プロンプトで内容を確認

### ❌ DON'T（非推奨）

- ❌ Sandbox用のClient Key（`sbaw`）を本番で使用
- ❌ App Review未承認で `video.upload` を使用
- ❌ Client SecretやTokenを公開
- ❌ 期限切れのトークンを使用
- ❌ Redirect URIの不一致

---

## 🔗 参考リンク

- [TikTok Developer Portal](https://developers.tiktok.com/apps)
- [TikTok API Documentation](https://developers.tiktok.com/doc/overview)
- [Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [Login Kit Web](https://developers.tiktok.com/doc/login-kit-web)
- [OAuth 2.0](https://developers.tiktok.com/doc/oauth-user-access-token-management)

---

## 📝 チェックリスト

### 初期設定

- [ ] TikTok Developer アカウント作成
- [ ] アプリ作成
- [ ] **Production タブ**でClient Key/Secret取得
- [ ] Redirect URI登録（Production タブ）
- [ ] Scopes設定（Production タブ）
- [ ] App Review申請
- [ ] App Review承認待ち
- [ ] `.env` ファイル設定

### 認証フロー

- [ ] `python generate_auth_url.py` 実行
- [ ] ブラウザで認証
- [ ] リダイレクトURLコピー
- [ ] `python get_token.py` 実行
- [ ] トークンを `.env` に保存

### テスト

- [ ] `python test_tiktok_connection.py` 成功
- [ ] ユーザー情報取得成功
- [ ] 動画アップロード権限確認

### 動画アップロード

- [ ] 動画ファイル生成（`out/MyComp.mp4`）
- [ ] スクリプトファイル作成（`today_script.json`）
- [ ] `python upload_tiktok_auto.py` 実行
- [ ] 確認プロンプトで `yes` 入力
- [ ] TikTok Creator Centerで動画確認

---

## 🎉 完了！

これで本番環境（Production）でTikTok APIを使用する準備が整いました！

⚠️ **重要な注意事項**:
- 本番環境では実際のTikTokアカウントに投稿されます
- App Reviewの承認が必要です
- トークンは24時間で期限切れになります
- 投稿前に必ず内容を確認してください

---

**作成日**: 2026-07-12  
**対象環境**: TikTok API v2 Production
