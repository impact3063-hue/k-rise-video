# 🎯 TikTok Sandbox 認証問題の完全解決ガイド

## 📌 問題の要約

### 発生していたエラー
1. **DNSエラー**: `https://sandbox-www.tiktok.com/` にアクセスできない
2. **client_keyエラー**: `https://www.tiktok.com/` を使うとclient_keyエラー

### 根本原因
**TikTok Sandboxの認証URLに関する誤解**がありました。

## ✅ 正しい仕様（TikTok公式）

### 認証フローの構造

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 認証URL（Authorization）                                  │
│    https://www.tiktok.com/v2/auth/authorize/                │
│    ↑ 本番・Sandbox共通（Client Keyで自動判別）              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. トークン取得（Token Exchange）                            │
│    Sandbox: https://sandbox-open.tiktokapis.com/v2/oauth/token/ │
│    Production: https://open.tiktokapis.com/v2/oauth/token/  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. API呼び出し（API Calls）                                  │
│    Sandbox: https://sandbox-open.tiktokapis.com/v2/...      │
│    Production: https://open.tiktokapis.com/v2/...           │
└─────────────────────────────────────────────────────────────┘
```

### 重要なポイント

| 項目 | Sandbox | Production | 備考 |
|------|---------|------------|------|
| **認証URL** | `www.tiktok.com` | `www.tiktok.com` | **同じURL** |
| **Client Key接頭辞** | `sbaw` | `aw` | これで環境を判別 |
| **トークンURL** | `sandbox-open.tiktokapis.com` | `open.tiktokapis.com` | 異なる |
| **API URL** | `sandbox-open.tiktokapis.com` | `open.tiktokapis.com` | 異なる |

## 🔧 修正内容

### 修正前（誤り）
```python
# ❌ このドメインは存在しない
SANDBOX_AUTH_URL = "https://sandbox-www.tiktok.com/v2/auth/authorize/"
```

### 修正後（正解）
```python
# ✅ 本番と同じURLを使用（Client Keyで環境判別）
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
```

## 📝 正しい認証手順

### ステップ1: 認証URLを生成

```bash
python generate_auth_url_sandbox.py
```

**生成されるURL:**
```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```

### ステップ2: ブラウザで認証

1. 上記URLをブラウザで開く
2. TikTokアカウントでログイン
3. アプリを承認
4. リダイレクトURLをコピー

**リダイレクト例:**
```
https://google.com/?code=ABC123XYZ&state=random_state&scopes=user.info.basic
```

### ステップ3: トークンを取得

```bash
python get_token_sandbox.py
```

リダイレクトURLを貼り付けると、自動的に以下のSandbox APIエンドポイントにリクエストします：
```
https://sandbox-open.tiktokapis.com/v2/oauth/token/
```

## 🔍 なぜこの仕様なのか？

### TikTokの設計思想

1. **ユーザー体験の統一**
   - 認証画面は本番環境と同じUIを使用
   - ユーザーは常に同じログイン体験

2. **Client Keyによる環境判別**
   - `sbaw` で始まる → Sandbox環境として処理
   - `aw` で始まる → Production環境として処理
   - サーバー側で自動的に適切な環境にルーティング

3. **APIエンドポイントの分離**
   - トークン取得やAPI呼び出しは完全に分離
   - Sandboxデータと本番データの混在を防止

## 🚨 よくある誤解

### 誤解1: Sandbox専用の認証URLがある
❌ **誤り**: `https://sandbox-www.tiktok.com/` を使う必要がある
✅ **正解**: 認証URLは本番と同じ。Client Keyで判別される

### 誤解2: すべてのエンドポイントが同じ
❌ **誤り**: 認証もAPIも同じドメインを使う
✅ **正解**: 認証は `www.tiktok.com`、APIは `sandbox-open.tiktokapis.com`

### 誤解3: Client Keyだけ変えればいい
❌ **誤り**: Client Keyを変えるだけで環境が切り替わる
✅ **正解**: Client Key + 適切なAPIエンドポイントの両方が必要

## 📊 環境別の完全な設定

### Sandbox環境
```python
# 認証URL
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"

# Client Key（sbawで始まる）
CLIENT_KEY = "sbaw1046rijsqctfgx"

# トークンURL
TOKEN_URL = "https://sandbox-open.tiktokapis.com/v2/oauth/token/"

# API Base URL
API_BASE = "https://sandbox-open.tiktokapis.com/v2"
```

### Production環境
```python
# 認証URL（Sandboxと同じ）
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"

# Client Key（awで始まる）
CLIENT_KEY = "aw1234567890abcdef"

# トークンURL
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"

# API Base URL
API_BASE = "https://open.tiktokapis.com/v2"
```

## 🎯 トラブルシューティング

### エラー: "このサイトにアクセスできません"（DNS）
**原因**: `sandbox-www.tiktok.com` を使用している
**解決**: `www.tiktok.com` に変更

### エラー: "client_key"
**原因**: 以下のいずれか
1. Client Keyが間違っている
2. Client Keyが `sbaw` で始まっていない（Sandbox用でない）
3. Developer Portalの設定が不完全

**解決**:
```bash
# 1. Client Keyを確認
echo $TIKTOK_CLIENT_KEY
# → sbaw1046rijsqctfgx

# 2. Developer Portalで確認
# https://developers.tiktok.com/apps/

# 3. Login Kit (Web) が追加されているか確認
```

### エラー: "redirect_uri_mismatch"
**原因**: Developer Portalに登録されたRedirect URIと異なる

**解決**:
1. Developer Portal → Products → Login Kit (Web)
2. Redirect URI: `https://google.com` を確認
3. 保存後、ページをリロードして確認

## 📚 参考リンク

- [TikTok Sandbox Environment](https://developers.tiktok.com/doc/sandbox-environment)
- [OAuth 2.0 Authorization](https://developers.tiktok.com/doc/oauth-user-access-token-management)
- [Login Kit Web](https://developers.tiktok.com/doc/login-kit-web)

## ✅ チェックリスト

認証を開始する前に、以下を確認してください：

- [ ] Client Keyが `sbaw` で始まっている
- [ ] `.env` ファイルに `TIKTOK_CLIENT_KEY` が設定されている
- [ ] `.env` ファイルに `TIKTOK_CLIENT_SECRET` が設定されている
- [ ] Developer Portalで Login Kit (Web) が追加されている
- [ ] Redirect URI `https://google.com` が登録されている
- [ ] 認証URLが `https://www.tiktok.com/v2/auth/authorize/` である
- [ ] トークンURLが `https://sandbox-open.tiktokapis.com/v2/oauth/token/` である

## 🎉 成功の確認

認証が成功すると、以下が取得できます：

```json
{
  "access_token": "act.sandbox_token_here...",
  "refresh_token": "rft.sandbox_refresh_token_here...",
  "open_id": "sandbox_open_id_here",
  "expires_in": 86400,
  "scope": "user.info.basic",
  "token_type": "Bearer"
}
```

これらの値を `.env` ファイルに保存すれば、API呼び出しが可能になります。

---

**最終更新**: 2026-07-12  
**対象環境**: TikTok Sandbox  
**ステータス**: ✅ 検証済み
