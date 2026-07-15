# TikTok Production 認証テスト（最小スコープ版）

## 📋 概要

App Review承認前でも認証フローをテストできるように、スコープを最小限の `user.info.basic` のみに絞った認証URLを生成します。

## 🎯 目的

- **App Review前のテスト**: `user.info.basic` はApp Review不要で使用可能
- **認証フローの確認**: トークン取得までの基本的な流れを確認
- **エラーの切り分け**: スコープ関連のエラーを回避してClient Key等の問題を特定

## ✅ 生成された認証URL

```
https://www.tiktok.com/v2/auth/authorize/?client_key=awh14qlqti6zxw90&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```

### 📊 URLの詳細

- **Client Key**: `awh14qlqti6zxw90` (Production用)
- **Scope**: `user.info.basic` のみ（App Review不要）
- **Redirect URI**: `https://google.com`

## 🔍 デベロッパーポータルで確認すべき設定

### 1. **Production環境の確認**

TikTok Developer Portal → あなたのアプリ → **Production タブ**

#### ✅ Client Key の確認
- Client Keyが `aw` で始まることを確認
- `awh14qlqti6zxw90` が正しく表示されているか

#### ✅ Redirect URI の登録
```
設定場所: Production → Login Kit → Redirect URI
登録すべきURI: https://google.com
```

**重要**: 
- Redirect URIは完全一致が必要
- `https://google.com` と `https://google.com/` は別物として扱われる
- 末尾のスラッシュに注意

#### ✅ Scopes の確認
```
設定場所: Production → Login Kit → Scopes
```

確認事項:
- `user.info.basic` が有効になっているか
- このスコープはデフォルトで有効（App Review不要）

### 2. **App Status の確認**

```
設定場所: Production → App Status
```

確認事項:
- アプリが **"Live"** または **"In Development"** 状態か
- **"Suspended"** や **"Rejected"** になっていないか

### 3. **API Products の確認**

```
設定場所: Production → API Products
```

確認事項:
- **Login Kit** が有効になっているか
- 少なくとも Login Kit は App Review なしで使用可能

## 🚀 テスト手順

### Step 1: 認証URLにアクセス

1. 上記の認証URLをコピー
2. **シークレットウィンドウ**で開く（キャッシュの影響を避けるため）
3. TikTokアカウントでログイン

### Step 2: 期待される動作

✅ **成功する場合**:
- TikTokのログイン画面が表示される
- アプリの権限承認画面が表示される
- 「基本情報へのアクセスを許可」のような表示
- 承認後、Google.comにリダイレクトされる
- URLに `code=...` パラメータが含まれる

❌ **失敗する場合**:
- `client_key` エラーが表示される
- 「アプリが見つかりません」エラー
- 無限リダイレクトループ

### Step 3: エラーが出た場合の対処

#### エラー: "Invalid client_key"

**原因の可能性**:
1. Client Keyが間違っている
2. Redirect URIが登録されていない
3. アプリがSuspended状態

**確認方法**:
```bash
# .envファイルの確認
cat .env | findstr TIKTOK_CLIENT_KEY_PROD
```

**対処法**:
1. Developer Portalで正しいClient Keyをコピー
2. `.env` ファイルの `TIKTOK_CLIENT_KEY_PROD` を更新
3. Redirect URI `https://google.com` が登録されているか確認

#### エラー: "Redirect URI mismatch"

**原因**: Redirect URIが登録されていない、または一致しない

**対処法**:
1. Developer Portal → Production → Login Kit → Redirect URI
2. `https://google.com` を追加（末尾スラッシュなし）
3. 保存後、数分待ってから再試行

#### エラー: "Scope not approved"

**原因**: `user.info.basic` 以外のスコープが含まれている

**対処法**:
1. `generate_auth_url.py` を確認
2. SCOPESが `["user.info.basic"]` のみになっているか確認
3. 他のスコープがコメントアウトされているか確認

## 📝 成功後の次のステップ

### 1. トークンの取得

リダイレクトされたURLをコピーして:

```bash
python get_token.py
```

例:
```
https://google.com/?code=ABC123XYZ&state=random_state&scopes=user.info.basic
```

### 2. トークンの確認

取得したトークンで基本情報を取得:

```bash
python test_tiktok_connection.py
```

### 3. App Reviewの申請

動画アップロード機能を使用する場合:

1. Developer Portal → Production → App Review
2. `video.upload` と `video.publish` スコープを申請
3. 審査に必要な情報を提供:
   - アプリの説明
   - 使用目的
   - スクリーンショット/デモ動画

## 🔧 トラブルシューティング

### 問題: シークレットウィンドウでも同じエラーが出る

**確認事項**:
1. Client Keyが本当に `aw` で始まるか（`sbaw` ではない）
2. Developer Portalで「Production」タブを見ているか（「Sandbox」ではない）
3. Redirect URIが完全一致しているか

### 問題: 認証画面は表示されるが、承認後にエラー

**原因**: Redirect URIの問題

**対処法**:
1. Developer Portalで登録されているRedirect URIを確認
2. 末尾のスラッシュの有無を確認
3. HTTPSであることを確認

### 問題: アプリが見つからないエラー

**原因**: アプリがLive状態ではない、またはClient Keyが無効

**対処法**:
1. Developer Portal → Production → App Status を確認
2. アプリを "Live" または "In Development" に設定
3. Client Keyを再確認

## 📚 参考情報

### TikTok API v2 仕様

- **認証URL**: `https://www.tiktok.com/v2/auth/authorize/`
- **トークンURL**: `https://open.tiktokapis.com/v2/oauth/token/`
- **パラメータ名**: `client_key`（`client_id` ではない）

### App Review不要なスコープ

- `user.info.basic` - ユーザーの基本情報（名前、プロフィール画像など）

### App Review必要なスコープ

- `video.upload` - 動画のアップロード
- `video.publish` - 動画の公開
- `video.list` - 動画リストの取得

## 💡 重要なポイント

1. **`user.info.basic` はApp Review不要**: すぐにテスト可能
2. **Client Keyは環境ごとに異なる**: Production用は `aw` で始まる
3. **Redirect URIは完全一致が必要**: 末尾のスラッシュにも注意
4. **シークレットウィンドウでテスト**: キャッシュの影響を避ける
5. **App Reviewは時間がかかる**: 数日〜数週間かかる場合がある

## 🎯 次のアクション

1. ✅ 上記の認証URLでテスト
2. ✅ トークン取得まで成功したら、基本情報取得をテスト
3. ✅ 成功を確認後、App Reviewを申請
4. ✅ App Review承認後、`video.upload` と `video.publish` を追加

---

**最終更新**: 2026-07-12
**対象環境**: TikTok Production (本番環境)
**スコープ**: user.info.basic のみ
