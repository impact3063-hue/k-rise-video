# TikTok Sandbox Redirect URI 設定ガイド

## 🔴 現在のエラー原因

「client_key」エラーが出続ける原因は、**TikTok Developer Portalに登録されているRedirect URIと、実際に使用しているRedirect URIが完全一致していない**可能性が高いです。

## 📋 現在の設定

```
Client Key:    sbaw1046rijsqctfgx
Redirect URI:  https://google.com
```

## ✅ 解決手順

### ステップ1: Developer Portalでの確認

1. **TikTok Developer Portalにアクセス**
   - URL: https://developers.tiktok.com/
   - ログインしてダッシュボードを開く

2. **アプリを選択**
   - 左メニューから「My apps」をクリック
   - Sandbox環境のアプリ（Client Key: `sbaw1046rijsqctfgx`）を選択

3. **Login Kit設定を開く**
   - 左メニューから「Products」→「Login Kit」をクリック
   - または「Manage apps」→「Login Kit」タブ

4. **Redirect URIを確認**
   - 「Redirect URI」セクションを探す
   - 現在登録されているURIを**正確に**確認してください
   
   **確認ポイント:**
   - ✓ `https://google.com` なのか `https://www.google.com` なのか
   - ✓ 末尾にスラッシュ `/` があるか: `https://google.com/`
   - ✓ 大文字・小文字の違い
   - ✓ プロトコル（http vs https）

### ステップ2: Redirect URIの修正（3つの選択肢）

#### 選択肢A: Developer Portalで修正（推奨）

現在登録されているRedirect URIが異なる場合、以下のように修正してください：

1. Developer Portalの「Login Kit」設定画面で「Edit」をクリック
2. Redirect URIを以下のいずれかに設定：
   ```
   https://google.com
   ```
   または
   ```
   https://www.google.com
   ```
3. 「Save」をクリック
4. **保存後、5-10分待つ**（設定が反映されるまで時間がかかる場合があります）

#### 選択肢B: 複数のRedirect URIを登録

より確実な方法として、複数のURIを登録できます：

```
https://google.com
https://www.google.com
https://google.com/
https://www.google.com/
```

#### 選択肢C: ローカルホスト用URIを追加（開発用）

開発環境では、ローカルホストも追加すると便利です：

```
http://localhost:3000/callback
http://127.0.0.1:3000/callback
https://google.com
```

### ステップ3: .envファイルの更新

Developer Portalで確認・修正したRedirect URIと**完全に一致する**ように、`.env`ファイルを更新します：

```bash
# 例1: google.comの場合
TIKTOK_REDIRECT_URI=https://google.com

# 例2: www.google.comの場合
TIKTOK_REDIRECT_URI=https://www.google.com

# 例3: 末尾スラッシュありの場合
TIKTOK_REDIRECT_URI=https://google.com/
```

### ステップ4: 新しい認証URLの生成

1. スクリプトを実行：
   ```bash
   python generate_auth_url_sandbox.py
   ```

2. 生成されたURLを確認：
   ```
   https://www.tiktok.com/v2/auth/authorize/?client_id=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https%3A%2F%2Fgoogle.com&state=random_state
   ```

3. **重要**: URLの `redirect_uri` パラメータがURLエンコードされていることを確認
   - `https://google.com` → `https%3A%2F%2Fgoogle.com`

### ステップ5: 認証テスト

1. **シークレットウィンドウ**で新しい認証URLを開く
2. TikTokアカウントでログイン
3. 権限を承認
4. エラーが出ないことを確認

## 🔍 トラブルシューティング

### エラーが続く場合

#### 1. Developer Portalの設定を再確認

- Redirect URIが**完全に一致**しているか
- 設定を保存してから**5-10分待った**か
- アプリのステータスが「Active」になっているか

#### 2. URLエンコーディングの確認

現在のスクリプトは自動的にURLエンコードしていますが、手動で確認する場合：

```python
import urllib.parse
uri = "https://google.com"
encoded = urllib.parse.quote(uri, safe='')
print(encoded)  # https%3A%2F%2Fgoogle.com
```

#### 3. ブラウザキャッシュのクリア

- シークレットウィンドウを閉じて新しく開く
- または通常ブラウザのキャッシュをクリア

#### 4. 別のRedirect URIを試す

Developer Portalで以下のような別のURIを試してみる：

```
https://example.com
https://localhost:3000/callback
```

## 📝 よくある間違い

| ❌ 間違い | ✅ 正しい |
|---------|---------|
| `http://google.com` | `https://google.com` |
| `https://www.google.com` | `https://google.com` |
| `https://google.com/` | `https://google.com` |
| Developer Portalに未登録 | 必ず事前登録が必要 |
| 設定後すぐにテスト | 5-10分待つ |

## 🎯 次のアクション

1. **今すぐ実行**: Developer Portalで現在のRedirect URI設定を確認
2. **確認内容を報告**: 登録されているURIを正確に教えてください
3. **必要に応じて修正**: 不一致があれば上記の手順で修正

---

## 📞 確認が必要な情報

以下の情報を確認して報告してください：

1. **Developer Portalに登録されているRedirect URI**
   - 例: `https://google.com` または `https://www.google.com` など

2. **複数のURIが登録されている場合**
   - すべてのURIをリストアップ

3. **Login Kitのステータス**
   - 「Active」「Pending」「Disabled」など

この情報があれば、正確な修正方法を指示できます。
