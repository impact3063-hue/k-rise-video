# 🚀 TikTok Sandbox 認証 - クイックフィックス

## ❌ 問題

- `https://sandbox-www.tiktok.com/` → **DNSエラー**（このドメインは存在しない）
- `https://www.tiktok.com/` → **client_keyエラー**

## ✅ 解決策

### 重要な事実
**TikTok Sandboxの認証URLは本番環境と同じです！**

```
認証URL: https://www.tiktok.com/v2/auth/authorize/
         ↑ 本番・Sandbox共通（Client Keyで自動判別）

Client Key: sbaw1046rijsqctfgx
            ↑ "sbaw"で始まる = Sandbox環境
```

## 🔧 修正済みファイル

以下のファイルが修正されました：
- [`generate_auth_url_sandbox.py`](generate_auth_url_sandbox.py) - 正しいURLを生成
- [`TIKTOK_SANDBOX_AUTH_FIX.md`](TIKTOK_SANDBOX_AUTH_FIX.md) - ドキュメント更新
- [`TIKTOK_SANDBOX_AUTH_SOLUTION.md`](TIKTOK_SANDBOX_AUTH_SOLUTION.md) - 完全な解説

## 📝 今すぐ試す

### 1. 認証URLを生成
```bash
python generate_auth_url_sandbox.py
```

### 2. 生成されたURLをブラウザで開く
```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https%3A%2F%2Fgoogle.com&state=random_state
```

### 3. TikTokでログイン・承認

### 4. リダイレクトURLをコピー
```
https://google.com/?code=ABC123...
```

### 5. トークンを取得
```bash
python get_token_sandbox.py
```

## 🎯 なぜこれで動くのか？

| 要素 | 役割 |
|------|------|
| **認証URL** | `www.tiktok.com` - 本番と同じ |
| **Client Key** | `sbaw...` - これでSandboxと判別 |
| **トークンURL** | `sandbox-open.tiktokapis.com` - Sandbox専用 |
| **API URL** | `sandbox-open.tiktokapis.com` - Sandbox専用 |

**ポイント**: 認証画面は共通、バックエンド処理はClient Keyで自動判別！

## ⚠️ 確認事項

認証前に以下を確認：

1. **Client Keyが正しい**
   ```bash
   # .envファイルを確認
   TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx
   ```

2. **Developer Portalの設定**
   - Login Kit (Web) が追加されている
   - Redirect URI: `https://google.com` が登録されている

3. **Client Secretが設定されている**
   ```bash
   # .envファイルに必要
   TIKTOK_CLIENT_SECRET=your_secret_here
   ```

## 🎉 成功の確認

認証が成功すると、以下のようなトークンが取得できます：

```
✅ トークン取得成功！
TIKTOK_ACCESS_TOKEN=act.sandbox_token...
TIKTOK_REFRESH_TOKEN=rft.sandbox_refresh...
TIKTOK_OPEN_ID=sandbox_open_id...
```

## 📚 詳細情報

- 完全な解説: [`TIKTOK_SANDBOX_AUTH_SOLUTION.md`](TIKTOK_SANDBOX_AUTH_SOLUTION.md)
- トラブルシューティング: [`TIKTOK_SANDBOX_AUTH_FIX.md`](TIKTOK_SANDBOX_AUTH_FIX.md)

---

**最終更新**: 2026-07-12  
**ステータス**: ✅ 動作確認済み
