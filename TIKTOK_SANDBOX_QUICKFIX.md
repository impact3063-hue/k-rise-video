# 🚨 TikTok Sandbox「client_key」エラー - 即座の解決策

## 📊 診断結果

```bash
python check_sandbox_setup.py
```

**結果:**
```
✅ TIKTOK_CLIENT_KEY: 設定済み
❌ TIKTOK_CLIENT_SECRET: 未設定 ← これが原因！
```

---

## 🎯 解決策（3ステップ）

### ステップ1: CLIENT_SECRETを取得 ⭐ 最重要

1. **TikTok Developer Portalを開く**
   ```
   https://developers.tiktok.com/apps/
   ```

2. **あなたのSandboxアプリをクリック**

3. **Basic Informationタブを開く**
   - 左側メニュー → "Basic Information"

4. **Client Secretを表示**
   ```
   Client Key: sbaw1046rijsqctfgx  ← 既に設定済み
   Client Secret: [Show] ← このボタンをクリック
   ```

5. **表示された値をコピー**
   - 長い英数字の文字列（例: `abc123def456ghi789...`）

### ステップ2: .envファイルに追加

[`.env`](.env) ファイルを開いて、以下の行を編集：

```bash
# 現在（CLIENT_SECRETが空）
TIKTOK_CLIENT_SECRET=

# ↓ 修正後（コピーした値を貼り付け）
TIKTOK_CLIENT_SECRET=ここにコピーしたClient Secretを貼り付け
```

**保存してください！**

### ステップ3: 設定を確認

```bash
python check_sandbox_setup.py
```

**期待される結果:**
```
✅ TIKTOK_CLIENT_KEY: 設定済み
✅ TIKTOK_CLIENT_SECRET: 設定済み
✅ 必須項目は全て設定されています！
```

---

## 🔍 なぜCLIENT_SECRETが必要なのか？

### 認証フロー

```
1. ブラウザでログイン → 認証コード取得
   ↓ CLIENT_KEYのみ使用（URLに含まれる）
   
2. 認証コードをトークンに交換
   ↓ CLIENT_KEY + CLIENT_SECRET が必要 ← ここでエラー！
   
3. アクセストークン取得
   ↓ APIを呼び出せるようになる
```

**現在の状態:**
- ステップ1は成功している可能性が高い
- ステップ2でCLIENT_SECRETがないため失敗
- 結果として「client_key is invalid」エラーが表示される

**CLIENT_SECRETがないと:**
```python
# get_token_sandbox.py で実行されるコード
data = {
    'client_key': 'sbaw1046rijsqctfgx',  # ✅ 設定済み
    'client_secret': None,                # ❌ 未設定 → エラー
    'code': 'abc123...',
    'grant_type': 'authorization_code'
}
# → TikTok APIが「client_key is invalid」を返す
```

---

## 🧪 テストユーザー登録について

### 結論: 通常は不要

**Login Kit (Web)の場合:**
- Developer自身のTikTokアカウントで認証可能
- テストユーザー登録は**オプション**

**テストユーザー登録が必要なケース:**
- TikTok Ads API を使用する場合
- 複数のテストアカウントでテストする場合
- Developer Portalで明示的に要求された場合

### もしテストユーザー登録が必要な場合

**Developer Portalで探す場所:**

```
左側メニュー:
□ Sandbox
□ Testing
□ Test Users
□ Testers
□ Settings → Test Accounts
□ Products → Login Kit → Test Users
```

**見つからない場合:**
- 多くの場合、明示的な登録は不要
- まずCLIENT_SECRETを設定してテストしてください

---

## ✅ 完全チェックリスト

### Developer Portal

```
□ Sandboxアプリが作成されている
□ Client Key: sbaw1046rijsqctfgx を確認
□ Client Secretを取得してコピー ← 最重要
□ Login Kit (Web)が追加されている
□ Login Kit (Web)のステータスが「Active」
□ Redirect URI: https://google.com が登録されている
□ 設定保存後、5〜10分経過している
```

### .envファイル

```bash
# 必須
□ TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx
□ TIKTOK_CLIENT_SECRET=（Developer Portalから取得） ← 最重要
```

---

## 🚀 CLIENT_SECRET設定後の手順

### 1. 設定確認

```bash
python check_sandbox_setup.py
```

### 2. 認証URL生成

```bash
python generate_auth_url_sandbox.py
```

**生成されるURL:**
```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```

### 3. ブラウザでテスト

1. **シークレットウィンドウを開く**
   - Chrome: `Ctrl+Shift+N`
   - Firefox: `Ctrl+Shift+P`

2. **URLを貼り付けてアクセス**

3. **期待される動作:**
   ```
   ✅ TikTokログイン画面が表示される
   ✅ ログイン後、アプリの承認画面が表示される
   ✅ 「Authorize」をクリック
   ✅ Google.comにリダイレクトされる
   ✅ URLに code= パラメータが含まれる
   ```

### 4. トークン取得

```bash
python get_token_sandbox.py
```

リダイレクトURLを貼り付けると、`.env`ファイルが自動更新されます。

### 5. 接続テスト

```bash
python test_tiktok_connection_sandbox.py
```

成功すると、あなたのTikTokユーザー情報が表示されます。

---

## 🔧 それでもエラーが出る場合

### エラー: "client_key is invalid"

**チェック項目:**

1. **CLIENT_SECRETが正しく設定されているか**
   ```bash
   python check_sandbox_setup.py
   ```

2. **Login Kit (Web)が有効化されているか**
   ```
   Developer Portal → Products → Login Kit (Web)
   Status: Active になっているか確認
   ```

3. **Redirect URIが登録されているか**
   ```
   Developer Portal → Products → Login Kit (Web) → Settings
   Redirect URIs: https://google.com が登録されているか確認
   ```

4. **設定が反映されているか**
   ```
   設定変更後、5〜10分待ってから再テスト
   ```

5. **Client Keyが正しいか**
   ```bash
   # .envファイルを確認
   TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx
   
   # Developer Portalの値と一致しているか確認
   ```

---

## 📚 詳細ドキュメント

### 包括的なガイド
- [`TIKTOK_SANDBOX_TEST_USER_GUIDE.md`](TIKTOK_SANDBOX_TEST_USER_GUIDE.md) - テストユーザー登録の詳細
- [`TIKTOK_FIX_SUMMARY.md`](TIKTOK_FIX_SUMMARY.md) - 修正サマリー
- [`TIKTOK_CLIENT_KEY_FIX.md`](TIKTOK_CLIENT_KEY_FIX.md) - client_key修正の詳細

### 公式ドキュメント
- [Login Kit Web](https://developers.tiktok.com/doc/login-kit-web)
- [OAuth 2.0](https://developers.tiktok.com/doc/oauth-user-access-token-management)
- [Sandbox Environment](https://developers.tiktok.com/doc/sandbox-environment)

---

## 💡 重要なポイント

### CLIENT_SECRETについて

```
CLIENT_KEY (公開情報):
- URLに含まれる
- ブラウザで見える
- 誰でも見ることができる
- 例: sbaw1046rijsqctfgx

CLIENT_SECRET (秘密情報):
- サーバー側でのみ使用
- 絶対に公開しない
- GitHubにコミットしない
- 誰にも共有しない
- 例: abc123def456ghi789...
```

### セキュリティ

```bash
# .gitignore に .env が含まれていることを確認
cat .gitignore | grep .env

# 出力: .env
# → 含まれていればOK
```

---

## 🎯 まとめ

### 問題の本質

**「client_key is invalid」エラーの真の原因:**
- CLIENT_KEYは正しい
- URLの構造も正しい
- **CLIENT_SECRETが未設定** ← これが原因！

### 解決策

1. **Developer PortalでCLIENT_SECRETを取得**
2. **`.env`ファイルに追加**
3. **再テスト**

### テストユーザー登録

- **通常は不要**
- まずCLIENT_SECRETを設定してテスト
- それでもエラーが出る場合のみ検討

---

**作成日時**: 2026-07-12 18:50 JST  
**作成者**: Claude (Code Mode)  
**ステータス**: ✅ 即座に実行可能
