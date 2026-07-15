# 🔧 TikTok Sandbox 認証エラー解決ガイド

## 🛑 発生しているエラー

```
TikTokにログインできません。アプリの設定が原因かもしれません。
あなたが開発者の場合は、以下を修正してもう一度お試しください。
・client_key
```

## 🔍 問題の原因

このエラーは以下のいずれかが原因です：

### 1. **認証URLとAPIエンドポイントの混同**
   - ❌ 誤解: Sandbox環境では `https://sandbox-www.tiktok.com/` を使う
   - ✅ 正解: **認証URLは本番と同じ** `https://www.tiktok.com/v2/auth/authorize/`
   - ✅ 正解: **APIエンドポイントのみSandbox専用** `https://sandbox-open.tiktokapis.com/`

### 2. **Client Keyの形式が正しくない**
   - Sandbox用のClient Keyは `sbaw` で始まる（例: `sbaw1046rijsqctfgx`）
   - 本番用のClient Keyは `aw` で始まる

### 3. **Login Kit (Web) の設定が不完全**
   - Redirect URIが正しく保存されていない
   - Scopeが正しく設定されていない

### 4. **アプリのステータスが Draft または Rejected**
   - Sandboxでも、アプリが有効な状態である必要がある

## ✅ 解決方法

### ステップ 1: TikTok Developer Portal の設定確認

1. **App Details を確認**
   ```
   https://developers.tiktok.com/apps/
   ```
   - Client key: `sbaw1046rijsqctfgx` （Sandbox用）
   - App Status: `In development` または `Live in production`

2. **Products → Login Kit (Web) を確認**
   - ✓ Login Kit が追加されているか
   - Redirect URI: `https://google.com` が保存されているか
   - **重要**: 保存後、ページをリロードして確認

3. **Scopes を確認**
   - 最低限必要: `user.info.basic`
   - 動画投稿用: `video.upload`, `video.publish`

### ステップ 2: Sandbox用の認証URLを生成

**正しいSandbox認証URL:**
```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```

**重要なポイント:**
- ✅ 認証URLは本番環境と同じ `https://www.tiktok.com/v2/auth/authorize/`
- ✅ Client Keyが `sbaw` で始まることでSandbox環境として認識される
- ✅ トークン取得やAPI呼び出しは `https://sandbox-open.tiktokapis.com/` を使用

### ステップ 3: 修正されたスクリプトを使用

新しいスクリプト [`generate_auth_url_sandbox.py`](generate_auth_url_sandbox.py) を使用してください。

```bash
python generate_auth_url_sandbox.py
```

## 🔄 Sandbox vs Production の違い

| 項目 | Sandbox | Production |
|------|---------|------------|
| **認証URL** | `https://www.tiktok.com/v2/auth/authorize/` | `https://www.tiktok.com/v2/auth/authorize/` |
| **API Base** | `https://sandbox-open.tiktokapis.com/v2` | `https://open.tiktokapis.com/v2` |
| **Client Key** | `sbaw` で始まる | `aw` で始まる |
| **識別方法** | Client Keyで自動判別 | Client Keyで自動判別 |
| **テストアカウント** | 必要（Sandbox専用） | 本番アカウント |
| **App Review** | 不要 | 必要 |

**重要**: 認証URLは本番・Sandbox共通。Client Keyの接頭辞（`sbaw` or `aw`）で環境が判別されます。

## 📝 完全な認証フロー（Sandbox）

### 1. 認証URLを生成
```bash
python generate_auth_url_sandbox.py
```

### 2. ブラウザで認証URLを開く
```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```
（Client Keyが `sbaw` で始まるため、自動的にSandbox環境として処理されます）

### 3. TikTokアカウントでログイン・承認

### 4. リダイレクトURLから認証コードを取得
リダイレクト後のURL例:
```
https://google.com/?code=ABC123XYZ&state=random_state&scopes=user.info.basic
```

### 5. 認証コードからアクセストークンを取得
```bash
python get_token_sandbox.py
```

リダイレクトURLを貼り付けると、自動的にアクセストークンを取得します。

## 🚨 よくあるエラーと対処法

### エラー 1: "client_key" エラー
**原因**: 
- 本番用URLでSandbox用Client Keyを使用している
- Client Keyが間違っている

**解決方法**:
```bash
# Sandbox用のURLを使用
python generate_auth_url_sandbox.py
```

### エラー 2: "redirect_uri_mismatch"
**原因**: 
- Developer Portalに登録されたRedirect URIと異なる

**解決方法**:
1. Developer Portal → Products → Login Kit (Web)
2. Redirect URI: `https://google.com` を確認
3. 保存後、ページをリロード

### エラー 3: "invalid_scope"
**原因**: 
- 要求したScopeがアプリに追加されていない

**解決方法**:
1. Developer Portal → Products
2. 必要なProductを追加（Login Kit, Content Posting API）
3. トークンを再取得

### エラー 4: "App not found"
**原因**: 
- Client Keyが間違っている
- アプリが削除されている

**解決方法**:
1. Developer Portalで正しいClient Keyを確認
2. `.env` ファイルを更新

## 🔐 環境変数の設定

`.env` ファイルに以下を設定:

```bash
# Sandbox環境用
TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx
TIKTOK_CLIENT_SECRET=your_sandbox_client_secret
TIKTOK_REDIRECT_URI=https://google.com

# 認証後に取得
TIKTOK_ACCESS_TOKEN=act.sandbox_token_here
TIKTOK_REFRESH_TOKEN=rft.sandbox_refresh_token_here
TIKTOK_OPEN_ID=sandbox_open_id_here
```

## 📚 参考リンク

- [TikTok Sandbox Environment](https://developers.tiktok.com/doc/sandbox-environment)
- [TikTok OAuth 2.0](https://developers.tiktok.com/doc/oauth-user-access-token-management)
- [Login Kit Documentation](https://developers.tiktok.com/doc/login-kit-web)

## 💡 次のステップ

1. ✅ Sandbox環境で認証を完了
2. ✅ アクセストークンを取得
3. ✅ API接続をテスト
4. ✅ 動画アップロードをテスト
5. 🚀 本番環境への移行（App Reviewが必要）

---

**最終更新**: 2026-07-12  
**対象環境**: TikTok Sandbox
