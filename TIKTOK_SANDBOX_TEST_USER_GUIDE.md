# 🧪 TikTok Sandbox テストユーザー登録ガイド

## 📌 問題の状況

### 現在のエラー
```
client_key is invalid
```

### 考えられる原因
1. ✅ **URLパラメータ**: 修正済み（`client_key`を使用）
2. ⚠️ **CLIENT_SECRET未設定**: `.env`に`TIKTOK_CLIENT_SECRET`が存在しない
3. ⚠️ **テストユーザー未登録**: Sandboxでテストアカウントが登録されていない可能性
4. ⚠️ **Login Kit未有効化**: Developer Portalで製品が有効化されていない

---

## 🎯 解決手順（優先順位順）

### ステップ1: CLIENT_SECRETの取得と設定 ⭐ 最優先

#### 1.1 Developer Portalでの確認

1. **TikTok Developer Portalにアクセス**
   ```
   https://developers.tiktok.com/apps/
   ```

2. **あなたのSandboxアプリを選択**
   - アプリ名をクリック

3. **Basic Informationタブを開く**
   - 左側メニューから「Basic Information」を選択

4. **Client Secretを確認**
   ```
   Client Key: sbaw1046rijsqctfgx  ← これは既に.envに設定済み
   Client Secret: [Show]ボタンをクリック
   ```

5. **Client Secretをコピー**
   - 「Show」ボタンをクリックして表示
   - 表示された文字列をコピー（例: `abc123def456...`）

#### 1.2 .envファイルへの追加

`.env`ファイルに以下の行を追加してください：

```bash
# TikTok Sandbox Credentials
TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx
TIKTOK_CLIENT_SECRET=ここにコピーしたClient Secretを貼り付け
```

**重要**: CLIENT_SECRETは認証コードをアクセストークンに交換する際に必須です。

---

### ステップ2: Login Kit (Web)の有効化確認

#### 2.1 製品の追加確認

1. **Developer Portalでアプリを開く**
   ```
   https://developers.tiktok.com/apps/
   ```

2. **「Products」タブを選択**
   - 左側メニューから「Products」をクリック

3. **Login Kit (Web)を確認**
   
   **既に追加されている場合:**
   ```
   ✅ Login Kit (Web)
      Status: Active
      Redirect URIs: https://google.com
   ```

   **まだ追加されていない場合:**
   ```
   1. 「+ Add Product」ボタンをクリック
   2. 「Login Kit」を選択
   3. 「Web」を選択
   4. 「Add」をクリック
   ```

#### 2.2 Redirect URIの設定

1. **Login Kit (Web)の設定を開く**
   - 「Login Kit (Web)」の「Settings」をクリック

2. **Redirect URIsを確認・追加**
   ```
   Redirect URIs:
   https://google.com  ← これを追加
   ```

3. **保存**
   - 「Save」ボタンをクリック
   - ⚠️ **重要**: 設定反映まで5〜10分待つ

---

### ステップ3: Sandboxテストユーザーの登録 🧪

TikTok Sandboxでは、**テストユーザーの事前登録が必要な場合があります**。

#### 3.1 テストユーザー登録の場所

**方法A: Sandbox Settingsから登録（推奨）**

1. **Developer Portalでアプリを開く**
   ```
   https://developers.tiktok.com/apps/
   ```

2. **「Sandbox」または「Testing」タブを探す**
   - 左側メニューに以下のいずれかがあるか確認：
     - 「Sandbox」
     - 「Testing」
     - 「Test Users」
     - 「Testers」

3. **テストユーザーを追加**
   
   **パターン1: TikTokアカウントで追加**
   ```
   1. 「Add Test User」または「Add Tester」をクリック
   2. あなたのTikTokユーザー名またはIDを入力
   3. 「Add」をクリック
   ```

   **パターン2: メールアドレスで招待**
   ```
   1. 「Invite Tester」をクリック
   2. TikTokアカウントに紐付いたメールアドレスを入力
   3. 招待メールを受信して承認
   ```

**方法B: App Settingsから登録**

1. **「Settings」タブを開く**
   - 左側メニューから「Settings」を選択

2. **「Authorized Test Accounts」セクションを探す**
   - ページをスクロールして探す

3. **テストアカウントを追加**
   ```
   1. 「+ Add Account」をクリック
   2. TikTokユーザー名を入力
   3. 保存
   ```

#### 3.2 テストユーザーの種類

TikTok Sandboxでは以下の種類のテストユーザーがあります：

| 種類 | 説明 | 用途 |
|------|------|------|
| **Developer** | アプリの開発者 | 全ての機能にアクセス可能 |
| **Tester** | テストユーザー | 認証とAPI呼び出しのテスト |
| **Advertiser** | 広告主（TikTok Ads API用） | 広告関連のテスト |

**Login Kit (Web)の場合**: 「Tester」として登録すれば十分です。

#### 3.3 テストユーザーが見つからない場合

**TikTok Developer Portalの構造は頻繁に変更されます**。以下の場所を確認してください：

```
✓ 左側メニュー:
  - Sandbox
  - Testing
  - Test Users
  - Testers
  - Settings → Test Accounts
  - Products → Login Kit → Test Users

✓ 上部タブ:
  - Sandbox Environment
  - Testing & QA
```

**それでも見つからない場合:**

TikTok Sandboxでは、**Developer自身のアカウントは自動的にテストユーザーとして扱われる**場合があります。この場合、明示的な登録は不要です。

---

### ステップ4: 認証URLの再テスト

#### 4.1 新しいURLを生成

```bash
python generate_auth_url_sandbox.py
```

**生成されるURL:**
```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```

#### 4.2 シークレットウィンドウでテスト

1. **ブラウザでシークレット/プライベートウィンドウを開く**
   - Chrome: `Ctrl+Shift+N` (Windows) / `Cmd+Shift+N` (Mac)
   - Firefox: `Ctrl+Shift+P` (Windows) / `Cmd+Shift+P` (Mac)

2. **URLを貼り付けてアクセス**

3. **期待される動作:**

   **✅ 成功した場合:**
   ```
   1. TikTokログイン画面が表示される
   2. ログイン後、アプリの承認画面が表示される
   3. 「Authorize」をクリック
   4. Google.comにリダイレクトされる
   5. URLに code= パラメータが含まれる
      例: https://google.com/?code=abc123...&state=random_state
   ```

   **❌ まだエラーが出る場合:**
   ```
   エラーメッセージ: "client_key is invalid"
   → ステップ5のトラブルシューティングへ
   ```

---

## 🔍 ステップ5: トラブルシューティング

### エラー: "client_key is invalid"

#### 原因1: CLIENT_SECRETが未設定
```bash
# .envファイルを確認
cat .env | grep TIKTOK_CLIENT_SECRET

# 出力がない場合は未設定
# → ステップ1に戻ってCLIENT_SECRETを追加
```

#### 原因2: Login Kit (Web)が有効化されていない
```
1. Developer Portal → Products
2. Login Kit (Web)が「Active」になっているか確認
3. なっていない場合は「Add Product」から追加
```

#### 原因3: Redirect URIが登録されていない
```
1. Developer Portal → Products → Login Kit (Web) → Settings
2. Redirect URIs: https://google.com が登録されているか確認
3. 登録されていない場合は追加して保存
4. 5〜10分待ってから再テスト
```

#### 原因4: Client Keyが間違っている
```bash
# .envファイルのCLIENT_KEYを確認
cat .env | grep TIKTOK_CLIENT_KEY

# 出力: TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx

# Developer Portalの値と一致しているか確認
# 一致していない場合は修正
```

#### 原因5: Sandboxアプリが無効化されている
```
1. Developer Portal → Apps
2. あなたのアプリのステータスを確認
3. 「Inactive」や「Suspended」になっていないか確認
4. なっている場合は有効化
```

#### 原因6: テストユーザーが登録されていない（可能性低）
```
1. Developer Portal → Sandbox/Testing
2. テストユーザーとして自分のTikTokアカウントを追加
3. 追加後、5分待ってから再テスト
```

---

## 📋 完全チェックリスト

### Developer Portal設定

```
□ Sandboxアプリが作成されている
□ Client Key: sbaw1046rijsqctfgx を確認
□ Client Secretを取得してコピー
□ Login Kit (Web)が追加されている
□ Login Kit (Web)のステータスが「Active」
□ Redirect URI: https://google.com が登録されている
□ 設定保存後、5〜10分経過している
□ （オプション）テストユーザーとして自分のアカウントを登録
```

### .envファイル設定

```bash
# 必須項目
□ TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx
□ TIKTOK_CLIENT_SECRET=（Developer Portalから取得）

# オプション（トークン取得後に自動設定される）
□ TIKTOK_OPEN_ID=...
□ TIKTOK_ACCESS_TOKEN=...
□ TIKTOK_REFRESH_TOKEN=...
□ TIKTOK_TOKEN_EXPIRES_IN=...
```

### コード設定

```
□ generate_auth_url_sandbox.py が最新版
□ パラメータ名が client_key になっている
□ 認証URLが www.tiktok.com になっている
□ URLエンコードが排除されている
```

---

## 🚀 次のステップ（成功後）

### 1. 認証コードの取得

```bash
# URLを生成
python generate_auth_url_sandbox.py

# ブラウザで開いてログイン
# リダイレクト後のURLをコピー
# 例: https://google.com/?code=abc123...&state=random_state
```

### 2. アクセストークンの取得

```bash
# リダイレクトURLを貼り付けてトークンを取得
python get_token_sandbox.py

# プロンプトが表示されたら、リダイレクトURLを貼り付け
# 成功すると.envファイルが自動更新される
```

### 3. 接続テスト

```bash
# TikTok APIへの接続をテスト
python test_tiktok_connection_sandbox.py

# 成功すると、あなたのTikTokユーザー情報が表示される
```

---

## 💡 重要なポイント

### CLIENT_SECRETについて

**CLIENT_SECRETは必須です**。以下の理由で重要です：

1. **トークン取得時に必要**
   ```python
   # get_token_sandbox.py で使用
   data = {
       'client_key': CLIENT_KEY,
       'client_secret': CLIENT_SECRET,  # ← これがないとエラー
       'code': auth_code,
       'grant_type': 'authorization_code',
       'redirect_uri': REDIRECT_URI
   }
   ```

2. **セキュリティ**
   - CLIENT_KEYは公開情報（URLに含まれる）
   - CLIENT_SECRETは秘密情報（サーバー側でのみ使用）
   - 両方が揃って初めてトークンを取得できる

3. **現在の状態**
   ```bash
   # あなたの.envファイル
   TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx  ✅ 設定済み
   TIKTOK_CLIENT_SECRET=                  ❌ 未設定
   ```

**今すぐCLIENT_SECRETを取得して.envに追加してください。**

### テストユーザー登録について

**TikTok Sandboxの仕様:**

- **一部のAPI**: テストユーザー登録が必須（例: TikTok Ads API）
- **Login Kit (Web)**: 通常は不要（Developer自身のアカウントで認証可能）
- **ただし**: エラーが続く場合は登録を試す価値あり

**推奨アプローチ:**

1. まず**CLIENT_SECRETを設定**（最優先）
2. 次に**Login Kit (Web)の有効化を確認**
3. それでもエラーが出る場合に**テストユーザー登録を試す**

---

## 📞 さらにサポートが必要な場合

### Developer Portalのスクリーンショット

以下の画面のスクリーンショットを共有していただければ、より具体的なアドバイスが可能です：

1. **Basic Information画面**
   - Client KeyとClient Secretが表示されている部分

2. **Products画面**
   - Login Kit (Web)のステータスが表示されている部分

3. **Login Kit Settings画面**
   - Redirect URIsが表示されている部分

4. **Sandbox/Testing画面（もしあれば）**
   - テストユーザー一覧が表示されている部分

### TikTok公式サポート

```
TikTok Developer Support:
https://developers.tiktok.com/support

よくある質問:
https://developers.tiktok.com/doc/faq
```

---

## 📚 関連ドキュメント

- [`TIKTOK_FIX_SUMMARY.md`](TIKTOK_FIX_SUMMARY.md) - 修正サマリー
- [`TIKTOK_CLIENT_KEY_FIX.md`](TIKTOK_CLIENT_KEY_FIX.md) - client_key修正の詳細
- [`TIKTOK_API_V2_LATEST_SPEC.md`](TIKTOK_API_V2_LATEST_SPEC.md) - API仕様
- [`TIKTOK_SANDBOX_AUTH_SOLUTION.md`](TIKTOK_SANDBOX_AUTH_SOLUTION.md) - 認証フロー

### 公式ドキュメント

- [Login Kit Web - Official Docs](https://developers.tiktok.com/doc/login-kit-web)
- [OAuth 2.0 - Official Docs](https://developers.tiktok.com/doc/oauth-user-access-token-management)
- [Sandbox Environment - Official Docs](https://developers.tiktok.com/doc/sandbox-environment)

---

**作成日時**: 2026-07-12 18:47 JST  
**作成者**: Claude (Code Mode)  
**ステータス**: ✅ 完成 - 実行可能
