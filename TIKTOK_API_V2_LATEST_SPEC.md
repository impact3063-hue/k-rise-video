# 🔍 TikTok API v2 最新仕様調査結果

## 📌 重大な発見：パラメータ名の誤り

### ❌ 誤った実装（以前）
```
https://www.tiktok.com/v2/auth/authorize/?client_id=sbaw1046rijsqctfgx&...
```
**パラメータ名**: `client_id` ← **これが間違い**

### ✅ 正しい実装（修正後）
```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&...
```
**パラメータ名**: `client_key` ← **これが正解**

---

## 🎯 根本原因の分析

### なぜ `client_id` と誤解されたのか？

1. **OAuth 2.0標準との混同**
   - OAuth 2.0標準では `client_id` が一般的
   - 多くのAPIプロバイダーが `client_id` を使用
   - TikTokは独自に `client_key` を採用

2. **ドキュメントの曖昧さ**
   - 一部のTikTokドキュメントで表記が混在
   - 古いバージョン（v1）との互換性情報が不明確

3. **エラーメッセージの誤解**
   - エラー: "client_key is invalid"
   - → パラメータ名が `client_key` であることを示唆していた

---

## 📚 TikTok API v2 認証仕様（確定版）

### 認証URLの構造

```
https://www.tiktok.com/v2/auth/authorize/
  ?client_key={CLIENT_KEY}
  &scope={SCOPES}
  &response_type=code
  &redirect_uri={REDIRECT_URI}
  &state={STATE}
```

### 必須パラメータ

| パラメータ | 説明 | 例 |
|-----------|------|-----|
| **client_key** | アプリのClient Key（`sbaw`で始まる） | `sbaw1046rijsqctfgx` |
| **scope** | 要求する権限（カンマ区切り） | `user.info.basic,video.upload` |
| **response_type** | 固定値 | `code` |
| **redirect_uri** | リダイレクト先URI | `https://google.com` |
| **state** | CSRF対策用のランダム文字列 | `random_state` |

### オプションパラメータ

| パラメータ | 説明 | 使用ケース |
|-----------|------|-----------|
| **code_challenge** | PKCE用のチャレンジ | モバイルアプリ、SPAで推奨 |
| **code_challenge_method** | チャレンジ方法 | `S256` または `plain` |

---

## 🔐 Sandbox環境の特殊仕様

### 1. Client Keyの接頭辞

| 環境 | 接頭辞 | 例 |
|------|--------|-----|
| **Sandbox** | `sbaw` | `sbaw1046rijsqctfgx` |
| **Production** | `aw` | `aw1234567890abcdef` |

### 2. エンドポイントの使い分け

| 処理 | Sandbox | Production |
|------|---------|------------|
| **認証URL** | `www.tiktok.com` | `www.tiktok.com` |
| **トークン取得** | `sandbox-open.tiktokapis.com` | `open.tiktokapis.com` |
| **API呼び出し** | `sandbox-open.tiktokapis.com` | `open.tiktokapis.com` |

### 3. Sandbox特有の制限

- ✅ Login Kit (Web) の有効化が必須
- ✅ Redirect URIの完全一致が必須（スキーム、ドメイン、パス）
- ✅ テストアカウントの使用を推奨
- ⚠️ 一部のスコープが制限される可能性

---

## 🛠️ トラブルシューティング

### エラー: "client_key is invalid"

#### 原因1: パラメータ名が間違っている
```diff
- ?client_id=sbaw1046rijsqctfgx
+ ?client_key=sbaw1046rijsqctfgx
```

#### 原因2: Client Keyが間違っている
- Developer Portalで正しいClient Keyを確認
- Sandbox用は `sbaw` で始まる必要がある

#### 原因3: Login Kit (Web) が有効化されていない
1. Developer Portal → Products
2. "Login Kit (Web)" を追加
3. Redirect URIを設定: `https://google.com`
4. 保存して数分待つ

#### 原因4: URLエンコードの問題
```python
# ❌ 間違い: URLエンコードする
redirect_uri = urllib.parse.quote("https://google.com")

# ✅ 正しい: 生の文字列を使用
redirect_uri = "https://google.com"
```

---

## 📋 完全な実装例

### Python実装

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Sandbox環境の設定
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")  # sbaw1046rijsqctfgx
REDIRECT_URI = "https://google.com"
SCOPES = ["user.info.basic"]

# 認証URL生成（エンコードなし）
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
scope_value = ",".join(SCOPES)

auth_url = (
    f"{AUTH_URL}"
    f"?client_key={CLIENT_KEY}"  # ← client_key を使用
    f"&scope={scope_value}"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&state=random_state"
)

print(auth_url)
```

### 生成されるURL

```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```

---

## 🔄 認証フロー全体

### ステップ1: 認証URLにアクセス
```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&...
```

### ステップ2: ユーザーが承認
- TikTokログイン画面が表示
- アプリの権限を確認
- 「承認」をクリック

### ステップ3: リダイレクト
```
https://google.com/?code=ABC123XYZ&state=random_state&scopes=user.info.basic
```

### ステップ4: トークン取得
```bash
POST https://sandbox-open.tiktokapis.com/v2/oauth/token/
Content-Type: application/x-www-form-urlencoded

client_key=sbaw1046rijsqctfgx
&client_secret=YOUR_SECRET
&code=ABC123XYZ
&grant_type=authorization_code
&redirect_uri=https://google.com
```

### ステップ5: レスポンス
```json
{
  "access_token": "act.sandbox_token...",
  "refresh_token": "rft.sandbox_refresh...",
  "open_id": "sandbox_open_id",
  "expires_in": 86400,
  "scope": "user.info.basic",
  "token_type": "Bearer"
}
```

---

## 🎯 チェックリスト

認証を開始する前に、以下を確認してください：

### Developer Portal設定
- [ ] Sandbox環境でアプリを作成済み
- [ ] Client Keyが `sbaw` で始まっている
- [ ] Client Secretを取得済み
- [ ] Login Kit (Web) を追加済み
- [ ] Redirect URI `https://google.com` を登録済み

### コード実装
- [ ] パラメータ名が `client_key` である（`client_id` ではない）
- [ ] URLエンコードを使用していない（生の文字列）
- [ ] 認証URLが `https://www.tiktok.com/v2/auth/authorize/` である
- [ ] トークンURLが `https://sandbox-open.tiktokapis.com/v2/oauth/token/` である

### 環境変数
- [ ] `.env` に `TIKTOK_CLIENT_KEY` を設定
- [ ] `.env` に `TIKTOK_CLIENT_SECRET` を設定
- [ ] `.env` に `TIKTOK_REDIRECT_URI` を設定

---

## 📖 公式ドキュメント参照

### 重要なリンク

1. **Login Kit Web**
   - https://developers.tiktok.com/doc/login-kit-web
   - 認証フローの詳細説明

2. **OAuth 2.0 Authorization**
   - https://developers.tiktok.com/doc/oauth-user-access-token-management
   - トークン管理の仕様

3. **Sandbox Environment**
   - https://developers.tiktok.com/doc/sandbox-environment
   - Sandbox環境の制限事項

4. **API Reference**
   - https://developers.tiktok.com/doc/web-api-reference-overview
   - 各エンドポイントの詳細

---

## 🚨 よくある間違い

### 間違い1: OAuth標準に従う
```python
# ❌ 間違い
params = {"client_id": CLIENT_KEY}  # OAuth標準

# ✅ 正しい
params = {"client_key": CLIENT_KEY}  # TikTok仕様
```

### 間違い2: URLエンコードする
```python
# ❌ 間違い
redirect_uri = urllib.parse.quote("https://google.com")

# ✅ 正しい
redirect_uri = "https://google.com"
```

### 間違い3: Sandbox専用の認証URLを使う
```python
# ❌ 間違い（存在しない）
AUTH_URL = "https://sandbox-www.tiktok.com/v2/auth/authorize/"

# ✅ 正しい（本番と同じ）
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
```

### 間違い4: Client Keyの接頭辞を間違える
```python
# ❌ 間違い（本番用）
CLIENT_KEY = "aw1234567890abcdef"

# ✅ 正しい（Sandbox用）
CLIENT_KEY = "sbaw1046rijsqctfgx"
```

---

## 🎉 成功の確認方法

### 認証URLにアクセスした時

✅ **成功**: TikTokログイン画面が表示される
❌ **失敗**: "client_key is invalid" エラー

### トークン取得時

✅ **成功**: 
```json
{
  "access_token": "act.sandbox_token...",
  "open_id": "sandbox_open_id"
}
```

❌ **失敗**:
```json
{
  "error": "invalid_client",
  "error_description": "client_key is invalid"
}
```

---

## 📊 修正の影響範囲

### 修正が必要なファイル

1. ✅ **generate_auth_url_sandbox.py** - 修正完了
   - `client_id` → `client_key` に変更

2. ⚠️ **generate_auth_url.py** - 確認が必要
   - 本番環境でも同じ修正が必要

3. ⚠️ **関連ドキュメント** - 更新が必要
   - TIKTOK_SANDBOX_AUTH_SOLUTION.md
   - TIKTOK_SETUP_GUIDE.md
   - その他のREADMEファイル

---

## 🔮 今後の対応

### 短期的な対応
1. ✅ `client_key` パラメータを使用
2. ✅ URLエンコードを排除
3. ⏳ シークレットウィンドウでテスト
4. ⏳ 成功を確認

### 中期的な対応
1. 本番環境用のスクリプトも修正
2. すべてのドキュメントを更新
3. テストスクリプトを作成

### 長期的な対応
1. TikTok API仕様の定期的な確認
2. 自動テストの導入
3. エラーハンドリングの強化

---

**最終更新**: 2026-07-12  
**検証ステータス**: ✅ パラメータ名を `client_key` に修正  
**次のステップ**: シークレットウィンドウでURLをテスト
