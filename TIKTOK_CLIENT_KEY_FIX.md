# 🔧 TikTok認証エラー完全解決ガイド

## 🎯 問題の本質

### エラーメッセージ
```
client_key is invalid
```

### 根本原因
**パラメータ名が間違っていました**: `client_id` ではなく `client_key` を使用する必要があります。

---

## ✅ 解決方法

### 修正前（❌ 間違い）
```
https://www.tiktok.com/v2/auth/authorize/?client_id=sbaw1046rijsqctfgx&...
                                          ^^^^^^^^^^
                                          これが間違い
```

### 修正後（✅ 正解）
```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&...
                                          ^^^^^^^^^^^
                                          これが正解
```

---

## 🚀 今すぐ試す

### ステップ1: 新しいURLを生成

```bash
python generate_auth_url_sandbox.py
```

### ステップ2: 生成されたURLをコピー

```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```

### ステップ3: シークレットウィンドウで開く

1. ブラウザでシークレット/プライベートウィンドウを開く
2. 上記URLを貼り付けてアクセス
3. TikTokログイン画面が表示されるはず

### ステップ4: 結果を確認

#### ✅ 成功した場合
- TikTokのログイン画面が表示される
- アプリの承認画面が表示される
- Google.comにリダイレクトされる

#### ❌ まだエラーが出る場合
次のセクションを確認してください

---

## 🔍 追加の確認事項

### 1. Developer Portalの設定

#### Login Kit (Web) が有効化されているか？

1. https://developers.tiktok.com/apps/ にアクセス
2. あなたのアプリを選択
3. 左メニュー「Products」をクリック
4. 「Login Kit (Web)」が追加されているか確認

**追加されていない場合:**
```
1. 「+ Add products」をクリック
2. 「Login Kit (Web)」を選択
3. 「Add」をクリック
```

#### Redirect URIが正しく設定されているか？

1. Products → Login Kit (Web)
2. Redirect URI: `https://google.com` が登録されているか確認
3. **完全一致**が必要（末尾のスラッシュも含めて）

**設定方法:**
```
1. Redirect URI欄に「https://google.com」を入力
2. 「Save」をクリック
3. ページをリロードして確認
```

### 2. Client Keyの確認

#### 正しいClient Keyを使用しているか？

```bash
# .envファイルを確認
cat .env | grep TIKTOK_CLIENT_KEY
```

**期待される出力:**
```
TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx
```

#### Sandbox用のClient Keyか？

- ✅ `sbaw` で始まる → Sandbox用（正しい）
- ❌ `aw` で始まる → Production用（間違い）

### 3. URLの構造を確認

#### 正しいURL構造

```
https://www.tiktok.com/v2/auth/authorize/
  ?client_key=sbaw1046rijsqctfgx          ← client_key を使用
  &scope=user.info.basic
  &response_type=code
  &redirect_uri=https://google.com        ← エンコードなし
  &state=random_state
```

#### よくある間違い

```diff
# 間違い1: パラメータ名
- ?client_id=sbaw1046rijsqctfgx
+ ?client_key=sbaw1046rijsqctfgx

# 間違い2: URLエンコード
- &redirect_uri=https%3A%2F%2Fgoogle.com
+ &redirect_uri=https://google.com

# 間違い3: 存在しないドメイン
- https://sandbox-www.tiktok.com/v2/auth/authorize/
+ https://www.tiktok.com/v2/auth/authorize/
```

---

## 📋 完全チェックリスト

認証を試す前に、以下をすべて確認してください：

### Developer Portal
- [ ] Sandboxアプリを作成済み
- [ ] Client Keyが `sbaw` で始まっている
- [ ] Client Secretを取得済み
- [ ] Login Kit (Web) を追加済み
- [ ] Redirect URI `https://google.com` を登録済み
- [ ] 設定を保存して5分以上経過している

### コード
- [ ] `generate_auth_url_sandbox.py` を最新版に更新
- [ ] パラメータ名が `client_key` である
- [ ] URLエンコードを使用していない
- [ ] 認証URLが `https://www.tiktok.com/v2/auth/authorize/` である

### 環境変数
- [ ] `.env` ファイルが存在する
- [ ] `TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx` が設定されている
- [ ] `TIKTOK_CLIENT_SECRET` が設定されている

---

## 🧪 テスト手順

### 1. URLを生成

```bash
python generate_auth_url_sandbox.py
```

**期待される出力:**
```
✅ Sandbox認証URLを生成しました:
================================================================================
https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
================================================================================
```

### 2. URLをテスト

```bash
# URLをクリップボードにコピー
# シークレットウィンドウで開く
```

### 3. 結果を記録

#### ケース1: TikTokログイン画面が表示される
→ ✅ **成功！** 次のステップに進む

#### ケース2: "client_key is invalid" エラー
→ ❌ Developer Portalの設定を再確認

#### ケース3: "redirect_uri_mismatch" エラー
→ ❌ Redirect URIの設定を再確認

#### ケース4: その他のエラー
→ ❌ エラーメッセージをコピーして調査

---

## 🔧 トラブルシューティング

### エラー: "client_key is invalid"

#### 解決策1: パラメータ名を確認
```bash
# URLに client_key が含まれているか確認
echo "URL" | grep "client_key="
```

#### 解決策2: Login Kit (Web) を再追加
```
1. Developer Portal → Products
2. Login Kit (Web) を削除
3. 5分待つ
4. Login Kit (Web) を再追加
5. Redirect URIを再設定
6. 保存して5分待つ
```

#### 解決策3: 新しいSandboxアプリを作成
```
1. Developer Portal → Apps
2. 「Create new app」
3. 環境: Sandbox を選択
4. アプリ名を入力
5. Login Kit (Web) を追加
6. 新しいClient Keyを取得
7. .envファイルを更新
```

### エラー: "redirect_uri_mismatch"

#### 解決策: 完全一致を確認
```python
# コード内
REDIRECT_URI = "https://google.com"

# Developer Portal
Redirect URI: https://google.com

# 注意: 以下は不一致
# https://google.com/  ← 末尾のスラッシュ
# https://www.google.com  ← www付き
# http://google.com  ← httpスキーム
```

---

## 📊 修正内容のまとめ

### 変更されたファイル

1. **generate_auth_url_sandbox.py**
   - Line 67: `client_id` → `client_key`
   - Line 84: 表示メッセージを修正
   - Line 134: コメントを修正

2. **generate_auth_url.py**
   - Line 26: `sandbox-www.tiktok.com` → `www.tiktok.com`
   - Line 36: `client_key` パラメータを使用（既に正しかった）

3. **新規ドキュメント**
   - TIKTOK_API_V2_LATEST_SPEC.md（詳細仕様）
   - TIKTOK_CLIENT_KEY_FIX.md（このファイル）

---

## 🎯 次のステップ

### 認証が成功したら

1. リダイレクトURLをコピー
   ```
   https://google.com/?code=ABC123XYZ&state=random_state&scopes=user.info.basic
   ```

2. トークンを取得
   ```bash
   python get_token_sandbox.py
   ```

3. リダイレクトURLを貼り付け

4. アクセストークンを取得
   ```json
   {
     "access_token": "act.sandbox_token...",
     "refresh_token": "rft.sandbox_refresh...",
     "open_id": "sandbox_open_id"
   }
   ```

5. `.env`ファイルに保存

---

## 📚 参考資料

### 公式ドキュメント
- [Login Kit Web](https://developers.tiktok.com/doc/login-kit-web)
- [OAuth 2.0](https://developers.tiktok.com/doc/oauth-user-access-token-management)
- [Sandbox Environment](https://developers.tiktok.com/doc/sandbox-environment)

### プロジェクト内ドキュメント
- `TIKTOK_API_V2_LATEST_SPEC.md` - 最新仕様の詳細
- `TIKTOK_SANDBOX_AUTH_SOLUTION.md` - 認証フローの説明
- `TIKTOK_SANDBOX_QUICK_START.md` - クイックスタートガイド

---

## ✅ 成功の確認

### 認証URLにアクセスした時

✅ **期待される動作:**
1. TikTokログイン画面が表示される
2. ユーザー名/パスワードを入力
3. アプリの承認画面が表示される
4. 「承認」をクリック
5. Google.comにリダイレクトされる
6. URLに `code=` パラメータが含まれる

❌ **エラーが出る場合:**
- このドキュメントのチェックリストを再確認
- Developer Portalの設定を再確認
- 5-10分待ってから再試行

---

## 💡 重要なポイント

### TikTok API v2の特徴

1. **パラメータ名は `client_key`**
   - OAuth 2.0標準の `client_id` ではない
   - TikTok独自の仕様

2. **認証URLは本番・Sandbox共通**
   - `www.tiktok.com` を使用
   - `sandbox-www.tiktok.com` は存在しない
   - Client Keyの接頭辞で環境を判別

3. **URLエンコードは不要**
   - ブラウザが自動的にエンコード
   - 手動でエンコードすると二重エンコードになる

4. **Redirect URIは完全一致**
   - スキーム、ドメイン、パスすべて一致が必要
   - 大文字小文字も区別される

---

**最終更新**: 2026-07-12  
**修正内容**: `client_id` → `client_key` パラメータに変更  
**検証ステータス**: ✅ コード修正完了、テスト待ち
