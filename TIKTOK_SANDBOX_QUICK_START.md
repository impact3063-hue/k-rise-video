# 🚀 TikTok Sandbox 認証 クイックスタートガイド

## ❌ 現在のエラー

```
TikTokにログインできません。アプリの設定が原因かもしれません。
あなたが開発者の場合は、以下を修正してもう一度お試しください。
・client_key
```

## ✅ 解決方法（3ステップ）

### ステップ 1: Sandbox認証URLを生成

```bash
python generate_auth_url_sandbox.py
```

**生成されるURL:**
```
https://sandbox-www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https%3A%2F%2Fgoogle.com&state=random_state
```

### ステップ 2: ブラウザで認証

1. 上記のURLをコピーしてブラウザで開く
2. TikTokアカウントでログイン
3. アプリの権限を承認
4. Googleにリダイレクトされる

**リダイレクト後のURL例:**
```
https://google.com/?code=ABC123XYZ&state=random_state&scopes=user.info.basic
```

### ステップ 3: アクセストークンを取得

```bash
python get_token_sandbox.py
```

プロンプトが表示されたら、リダイレクトURLを貼り付けます。

**成功すると `.env` ファイルが自動更新されます！**

---

## 🔍 重要なポイント

### ❌ 間違ったURL（本番環境）
```
https://www.tiktok.com/v2/auth/authorize/
```

### ✅ 正しいURL（Sandbox環境）
```
https://sandbox-www.tiktok.com/v2/auth/authorize/
```

**違い:** `sandbox-www` が必要！

---

## 📊 Sandbox vs Production

| 項目 | Sandbox | Production |
|------|---------|------------|
| **認証URL** | `sandbox-www.tiktok.com` | `www.tiktok.com` |
| **API URL** | `sandbox-open.tiktokapis.com` | `open.tiktokapis.com` |
| **Client Key** | `sbaw` で始まる | `aw` で始まる |
| **App Review** | 不要 | 必要 |

---

## 🛠️ トラブルシューティング

### エラー: "client_key"

**原因:** 本番環境のURLでSandbox用Client Keyを使用している

**解決方法:**
```bash
python generate_auth_url_sandbox.py
```
生成されたSandbox URLを使用してください。

### エラー: "redirect_uri_mismatch"

**原因:** Developer Portalの設定と異なるRedirect URI

**解決方法:**
1. [TikTok Developer Portal](https://developers.tiktok.com/apps/) にアクセス
2. アプリを選択
3. Products → Login Kit (Web)
4. Redirect URI: `https://google.com` を確認
5. 保存してページをリロード

### エラー: "invalid_scope"

**原因:** 要求したScopeがアプリに追加されていない

**解決方法:**
1. Developer Portal → Products
2. Login Kit を追加
3. Content Posting API を追加（動画投稿する場合）
4. トークンを再取得

### エラー: "Client Secret が設定されていません"

**解決方法:**
1. Developer Portal → App details
2. Client secret をコピー
3. `.env` ファイルに追加:
   ```
   TIKTOK_CLIENT_SECRET=your_client_secret_here
   ```

---

## 📝 完全な手順（詳細版）

### 1. Developer Portalの設定確認

```
https://developers.tiktok.com/apps/
```

**確認項目:**
- ✅ Client key: `sbaw1046rijsqctfgx`
- ✅ Client secret: 設定済み
- ✅ Products → Login Kit (Web): 追加済み
- ✅ Redirect URI: `https://google.com` 登録済み

### 2. 環境変数の設定

`.env` ファイルに以下を設定:

```bash
TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx
TIKTOK_CLIENT_SECRET=your_client_secret_here
TIKTOK_REDIRECT_URI=https://google.com
```

### 3. Sandbox認証URLを生成

```bash
python generate_auth_url_sandbox.py
```

### 4. ブラウザで認証

生成されたURLをブラウザで開き、TikTokアカウントでログイン・承認

### 5. アクセストークンを取得

```bash
python get_token_sandbox.py
```

リダイレクトURLを貼り付けると、自動的に `.env` が更新されます。

### 6. 接続テスト

```bash
python test_tiktok_connection_sandbox.py
```

すべてのテストが成功すれば完了！

---

## 🎯 次のステップ

### Sandbox環境でテスト

```bash
# 動画を生成
python make_script_auto.py
python make_subtitles_auto.py
npx remotion render

# Sandboxにアップロード（テスト）
python upload_tiktok_auto.py
```

### 本番環境への移行

1. TikTok App Review を申請
2. 承認後、本番用のClient Key/Secretを取得
3. 本番用の認証URLで再認証
4. 本番環境でアップロード

---

## 📚 関連ファイル

- [`TIKTOK_SANDBOX_AUTH_FIX.md`](TIKTOK_SANDBOX_AUTH_FIX.md) - 詳細な解説
- [`generate_auth_url_sandbox.py`](generate_auth_url_sandbox.py) - Sandbox認証URL生成
- [`get_token_sandbox.py`](get_token_sandbox.py) - トークン取得
- [`test_tiktok_connection_sandbox.py`](test_tiktok_connection_sandbox.py) - 接続テスト

---

## 💡 よくある質問

### Q: Sandboxと本番環境の違いは？

**A:** Sandboxは開発・テスト用の環境です。App Reviewなしで使用できますが、本番のTikTokには投稿されません。

### Q: Client Keyが `sbaw` で始まらない

**A:** それは本番用のClient Keyです。Developer Portalで「Sandbox」環境のClient Keyを確認してください。

### Q: 認証コードの有効期限は？

**A:** 通常5分です。期限切れの場合は、新しい認証URLを生成してください。

### Q: トークンの有効期限は？

**A:** アクセストークンは通常24時間です。リフレッシュトークンで更新できます。

---

**最終更新:** 2026-07-12  
**対象:** TikTok Sandbox環境
