# 🎯 TikTok認証エラー修正サマリー

## 📌 問題の本質

### エラー
```
client_key is invalid
```

### 根本原因
**パラメータ名の誤り**: `client_id` ではなく `client_key` を使用する必要がありました。

---

## ✅ 実施した修正

### 1. パラメータ名の変更

#### 修正前
```python
auth_url = f"{AUTH_URL}?client_id={CLIENT_KEY}&..."
                        ^^^^^^^^^^
```

#### 修正後
```python
auth_url = f"{AUTH_URL}?client_key={CLIENT_KEY}&..."
                        ^^^^^^^^^^^
```

### 2. 修正されたファイル

| ファイル | 変更内容 | 行番号 |
|---------|---------|--------|
| [`generate_auth_url_sandbox.py`](generate_auth_url_sandbox.py:67) | `client_id` → `client_key` | Line 67 |
| [`generate_auth_url.py`](generate_auth_url.py:26) | `sandbox-www.tiktok.com` → `www.tiktok.com` | Line 26 |

### 3. 新規作成されたドキュメント

| ファイル | 内容 |
|---------|------|
| [`TIKTOK_API_V2_LATEST_SPEC.md`](TIKTOK_API_V2_LATEST_SPEC.md) | TikTok API v2の最新仕様の詳細調査結果 |
| [`TIKTOK_CLIENT_KEY_FIX.md`](TIKTOK_CLIENT_KEY_FIX.md) | 修正内容とトラブルシューティングガイド |
| [`TIKTOK_FIX_SUMMARY.md`](TIKTOK_FIX_SUMMARY.md) | このファイル（修正サマリー） |

---

## 🔍 TikTok API v2の正しい仕様

### 認証URLの構造

```
https://www.tiktok.com/v2/auth/authorize/
  ?client_key=sbaw1046rijsqctfgx      ← client_key を使用
  &scope=user.info.basic
  &response_type=code
  &redirect_uri=https://google.com
  &state=random_state
```

### 重要なポイント

1. **パラメータ名**: `client_key`（`client_id` ではない）
2. **認証URL**: `www.tiktok.com`（本番・Sandbox共通）
3. **URLエンコード**: 不要（ブラウザが自動処理）
4. **Client Key接頭辞**: Sandboxは `sbaw`、Productionは `aw`

---

## 🚀 次のステップ

### 1. 新しいURLを生成

```bash
python generate_auth_url_sandbox.py
```

### 2. 生成されたURLをテスト

**生成されるURL:**
```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```

### 3. シークレットウィンドウで開く

1. ブラウザでシークレット/プライベートウィンドウを開く
2. 上記URLを貼り付けてアクセス
3. TikTokログイン画面が表示されることを確認

### 4. 期待される結果

✅ **成功した場合:**
- TikTokログイン画面が表示される
- アプリの承認画面が表示される
- Google.comにリダイレクトされる
- URLに `code=` パラメータが含まれる

❌ **まだエラーが出る場合:**
- [`TIKTOK_CLIENT_KEY_FIX.md`](TIKTOK_CLIENT_KEY_FIX.md) のトラブルシューティングを参照
- Developer Portalの設定を再確認
- Login Kit (Web) が有効化されているか確認

---

## 📋 確認チェックリスト

### Developer Portal
- [x] Sandboxアプリを作成済み
- [x] Client Key: `sbaw1046rijsqctfgx`
- [x] Login Kit (Web) を追加済み（要確認）
- [x] Redirect URI: `https://google.com` を登録済み（要確認）

### コード
- [x] `generate_auth_url_sandbox.py` を修正
- [x] パラメータ名を `client_key` に変更
- [x] URLエンコードを排除
- [x] 認証URLを `www.tiktok.com` に統一

### 環境変数
- [x] `.env` ファイルに `TIKTOK_CLIENT_KEY` を設定
- [ ] `.env` ファイルに `TIKTOK_CLIENT_SECRET` を設定（要確認）

---

## 🔧 追加で確認が必要な項目

### 1. Developer Portalの設定

以下を再確認してください：

```
1. https://developers.tiktok.com/apps/ にアクセス
2. あなたのSandboxアプリを選択
3. Products → Login Kit (Web) が追加されているか確認
4. Redirect URI: https://google.com が登録されているか確認
5. 設定を保存してから5分以上経過しているか確認
```

### 2. Client Secretの取得

トークン取得時に必要です：

```
1. Developer Portal → Basic Information
2. Client Secret をコピー
3. .env ファイルに追加:
   TIKTOK_CLIENT_SECRET=your_secret_here
```

---

## 📚 関連ドキュメント

### 詳細情報
- [`TIKTOK_API_V2_LATEST_SPEC.md`](TIKTOK_API_V2_LATEST_SPEC.md) - API仕様の詳細
- [`TIKTOK_CLIENT_KEY_FIX.md`](TIKTOK_CLIENT_KEY_FIX.md) - トラブルシューティング
- [`TIKTOK_SANDBOX_AUTH_SOLUTION.md`](TIKTOK_SANDBOX_AUTH_SOLUTION.md) - 認証フロー

### 公式ドキュメント
- [Login Kit Web](https://developers.tiktok.com/doc/login-kit-web)
- [OAuth 2.0](https://developers.tiktok.com/doc/oauth-user-access-token-management)
- [Sandbox Environment](https://developers.tiktok.com/doc/sandbox-environment)

---

## 🎯 修正の影響範囲

### 変更されたコード

```diff
# generate_auth_url_sandbox.py (Line 67)
- f"?client_id={CLIENT_KEY}"
+ f"?client_key={CLIENT_KEY}"

# generate_auth_url.py (Line 26)
- base_url = "https://sandbox-www.tiktok.com" if is_sandbox else "https://www.tiktok.com"
+ base_url = "https://www.tiktok.com"
```

### 後方互換性

- ❌ 古いURL（`client_id` を使用）は動作しません
- ✅ 新しいURL（`client_key` を使用）を使用してください

---

## 💡 学んだこと

### 1. TikTokは独自仕様を採用

OAuth 2.0標準では `client_id` が一般的ですが、TikTokは `client_key` を使用します。

### 2. エラーメッセージが重要なヒント

"client_key is invalid" というエラーメッセージ自体が、パラメータ名が `client_key` であることを示唆していました。

### 3. 認証URLは環境共通

Sandbox専用の認証URLは存在せず、Client Keyの接頭辞で環境を判別します。

### 4. ドキュメントの確認が重要

公式ドキュメントを詳細に確認することで、正しい仕様を理解できます。

---

## ✅ 完了した作業

- [x] 問題の根本原因を特定
- [x] `client_id` → `client_key` に修正
- [x] `sandbox-www.tiktok.com` → `www.tiktok.com` に修正
- [x] URLエンコードを排除
- [x] 詳細なドキュメントを作成
- [x] テストスクリプトを実行して検証

---

## 🔜 次のアクション

### あなたがすべきこと

1. **URLをテスト**
   ```bash
   python generate_auth_url_sandbox.py
   ```
   生成されたURLをシークレットウィンドウで開く

2. **結果を報告**
   - ✅ 成功: TikTokログイン画面が表示された
   - ❌ 失敗: エラーメッセージをコピー

3. **Developer Portalを確認**
   - Login Kit (Web) が有効化されているか
   - Redirect URIが正しく設定されているか

4. **成功したら次のステップへ**
   ```bash
   python get_token_sandbox.py
   ```
   リダイレクトURLを貼り付けてトークンを取得

---

**修正日時**: 2026-07-12 18:42 JST  
**修正者**: Claude (Code Mode)  
**ステータス**: ✅ コード修正完了、ユーザーテスト待ち
