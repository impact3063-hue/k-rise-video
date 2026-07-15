# 🎯 TikTok Sandbox 認証エラー - 解決完了

## 📋 問題の概要

**発生していたエラー:**
```
TikTokにログインできません。アプリの設定が原因かもしれません。
あなたが開発者の場合は、以下を修正してもう一度お試しください。
・client_key
```

**原因:**
Sandbox環境では、本番環境とは**異なるドメイン**を使用する必要があります。

## ✅ 解決方法

### 🔴 間違っていたURL（本番環境）
```
https://www.tiktok.com/v2/auth/authorize/
```

### 🟢 正しいURL（Sandbox環境）
```
https://sandbox-www.tiktok.com/v2/auth/authorize/
```

**重要:** `sandbox-www` プレフィックスが必要です！

---

## 🚀 クイックスタート（3ステップ）

### ステップ 1: Sandbox認証URLを生成

```bash
python generate_auth_url.py
```

または

```bash
python generate_auth_url_sandbox.py
```

**出力例:**
```
https://sandbox-www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```

### ステップ 2: ブラウザで認証

1. 生成されたURLをブラウザで開く
2. TikTokアカウントでログイン
3. アプリの権限を承認
4. リダイレクトされたURLをコピー

**リダイレクト例:**
```
https://google.com/?code=ABC123XYZ&state=random_state&scopes=user.info.basic
```

### ステップ 3: アクセストークンを取得

```bash
python get_token_sandbox.py
```

リダイレクトURLを貼り付けると、自動的に `.env` ファイルが更新されます！

---

## 📁 作成されたファイル

### 1. [`TIKTOK_SANDBOX_QUICK_START.md`](TIKTOK_SANDBOX_QUICK_START.md)
   - **最も重要**: 3ステップで認証を完了
   - トラブルシューティング付き
   - 初めての方はこちらから

### 2. [`TIKTOK_SANDBOX_AUTH_FIX.md`](TIKTOK_SANDBOX_AUTH_FIX.md)
   - 詳細な技術解説
   - Sandbox vs Production の違い
   - エラーの原因と対処法

### 3. [`generate_auth_url_sandbox.py`](generate_auth_url_sandbox.py)
   - Sandbox専用の認証URL生成スクリプト
   - Client Keyの検証機能付き

### 4. [`generate_auth_url.py`](generate_auth_url.py) ⭐ 更新
   - 自動的にSandbox/Productionを判定
   - Client Keyの形式から環境を検出
   - 適切なURLを生成

### 5. [`get_token_sandbox.py`](get_token_sandbox.py)
   - Sandbox用のトークン取得スクリプト
   - `.env` ファイルを自動更新
   - エラーハンドリング付き

### 6. [`test_tiktok_connection_sandbox.py`](test_tiktok_connection_sandbox.py)
   - Sandbox API接続テスト
   - トークンの検証
   - 権限チェック

---

## 🔍 Sandbox vs Production

| 項目 | Sandbox | Production |
|------|---------|------------|
| **認証URL** | `https://sandbox-www.tiktok.com/v2/auth/authorize/` | `https://www.tiktok.com/v2/auth/authorize/` |
| **API Base** | `https://sandbox-open.tiktokapis.com/v2` | `https://open.tiktokapis.com/v2` |
| **Client Key** | `sbaw` で始まる | `aw` で始まる |
| **Client Secret** | Sandbox専用 | Production専用 |
| **テスト環境** | ✅ 開発・テスト用 | ❌ 本番のみ |
| **App Review** | ❌ 不要 | ✅ 必要 |
| **投稿先** | テスト環境のみ | 本番TikTok |

---

## 📝 使用方法

### 基本的な流れ

```bash
# 1. 認証URLを生成（自動判定）
python generate_auth_url.py

# 2. ブラウザで認証（URLをコピーして開く）

# 3. トークンを取得
python get_token_sandbox.py

# 4. 接続テスト
python test_tiktok_connection_sandbox.py

# 5. 動画をアップロード（テスト）
python upload_tiktok_auto.py
```

### 環境変数の設定

`.env` ファイルに以下を設定:

```bash
# Sandbox環境用
TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx
TIKTOK_CLIENT_SECRET=your_sandbox_client_secret

# 認証後に自動設定される
TIKTOK_ACCESS_TOKEN=act.sandbox_token_here
TIKTOK_REFRESH_TOKEN=rft.sandbox_refresh_token_here
TIKTOK_OPEN_ID=sandbox_open_id_here
TIKTOK_TOKEN_EXPIRES_IN=86400
```

---

## 🛠️ トラブルシューティング

### エラー: "client_key"

**原因:** 本番環境のURLでSandbox用Client Keyを使用

**解決方法:**
```bash
python generate_auth_url.py
```
自動的にSandbox URLが生成されます。

### エラー: "redirect_uri_mismatch"

**原因:** Developer Portalの設定と異なる

**解決方法:**
1. [TikTok Developer Portal](https://developers.tiktok.com/apps/) にアクセス
2. Products → Login Kit (Web)
3. Redirect URI: `https://google.com` を確認・保存

### エラー: "invalid_scope"

**原因:** 必要なProductが追加されていない

**解決方法:**
1. Developer Portal → Products
2. Login Kit を追加
3. Content Posting API を追加（動画投稿用）

### エラー: "Client Secret が設定されていません"

**解決方法:**
```bash
# .env ファイルに追加
TIKTOK_CLIENT_SECRET=your_client_secret_here
```

---

## 🎯 次のステップ

### 1. Sandbox環境でテスト

```bash
# 動画を生成
python make_script_auto.py
python make_subtitles_auto.py
npx remotion render

# Sandboxにアップロード
python upload_tiktok_auto.py
```

### 2. 本番環境への移行

1. **App Reviewを申請**
   - TikTok Developer Portalから申請
   - 必要な権限を説明
   - 審査には数日〜数週間

2. **本番用の認証情報を取得**
   - Client Key: `aw` で始まる
   - Client Secret: 本番用

3. **本番環境で再認証**
   ```bash
   # .env を本番用に更新
   TIKTOK_CLIENT_KEY=aw_production_key
   TIKTOK_CLIENT_SECRET=production_secret
   
   # 本番用URLで認証
   python generate_auth_url.py
   ```

4. **本番環境でアップロード**
   ```bash
   python upload_tiktok_auto.py
   ```

---

## 📚 参考リンク

- [TikTok for Developers](https://developers.tiktok.com/)
- [Sandbox Environment Documentation](https://developers.tiktok.com/doc/sandbox-environment)
- [OAuth 2.0 Guide](https://developers.tiktok.com/doc/oauth-user-access-token-management)
- [Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started)

---

## 💡 重要なポイント

### ✅ Sandbox環境の利点

- App Review不要で即座にテスト可能
- 本番環境に影響を与えない
- 開発・デバッグが容易

### ⚠️ Sandbox環境の制限

- 本番のTikTokには投稿されない
- テスト用アカウントが必要
- 一部の機能が制限される場合がある

### 🚀 本番環境への移行時の注意

- Client KeyとClient Secretを本番用に変更
- 認証URLも本番用に変更
- App Reviewが必要
- トークンを再取得

---

## 🆘 サポート

問題が解決しない場合:

1. [`TIKTOK_SANDBOX_QUICK_START.md`](TIKTOK_SANDBOX_QUICK_START.md) を確認
2. [`TIKTOK_SANDBOX_AUTH_FIX.md`](TIKTOK_SANDBOX_AUTH_FIX.md) の詳細解説を確認
3. [TikTok Developer Community](https://developers.tiktok.com/community/)
4. TikTok Developer Support（アプリダッシュボードから）

---

**作成日:** 2026-07-12  
**対象環境:** TikTok Sandbox  
**ステータス:** ✅ 解決済み
