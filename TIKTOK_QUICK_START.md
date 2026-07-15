# TikTok アップロード クイックスタートガイド

## 🚨 現在の問題

```
[ERROR] TikTokへのアップロードに失敗しました
原因: video.upload 権限が不足しています
```

## ⚡ 今すぐ解決する方法

### ステップ1: 問題を診断（完了済み）

```bash
python test_tiktok_connection.py
```

**診断結果:**
- ✅ トークンは有効
- ✅ ユーザー情報取得可能
- ❌ **video.upload 権限が不足**

### ステップ2: 新しいトークンを取得

#### 方法A: 自動スクリプト（推奨）

```bash
python refresh_tiktok_token.py
```

このスクリプトが自動的に：
1. 認証URLを生成
2. ブラウザを開く
3. 認証コードを取得
4. トークンに交換
5. `.env` を更新

#### 方法B: 手動で取得

1. **認証URLにアクセス:**

```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbawl046rijsqctfgx&scope=user.info.basic,video.upload,video.publish&response_type=code&redirect_uri=https://google.com
```

2. **TikTokで認証:**
   - ログイン
   - **すべての権限を承認**（特に video.upload）
   - リダイレクト先のURLから `code` をコピー

3. **get_token.py を更新:**

```python
CODE = "ここに新しいコードを貼り付け"
```

4. **トークンを取得:**

```bash
python get_token.py
```

5. **`.env` を更新:**

```env
TIKTOK_ACCESS_TOKEN=act.新しいトークン
TIKTOK_OPEN_ID=-000新しいID
```

### ステップ3: 接続を確認

```bash
python test_tiktok_connection.py
```

**期待される結果:**
```
✓ 環境変数チェック - 成功
✓ トークン形式チェック - 成功
✓ ユーザー情報取得テスト - 成功
✓ 動画アップロード権限テスト - 成功  ← これが重要！

✓ テスト完了: すべて正常
```

### ステップ4: 動画をアップロード

```bash
python upload_tiktok_auto.py
```

---

## 📚 利用可能なツール

### 1. `test_tiktok_connection.py` - API接続テスト

**用途:** トークンの有効性と権限を確認

```bash
python test_tiktok_connection.py
```

**チェック項目:**
- 環境変数の設定
- トークン形式
- ユーザー情報取得
- 動画アップロード権限

### 2. `refresh_tiktok_token.py` - トークン更新（自動）

**用途:** 新しいアクセストークンを自動取得

```bash
python refresh_tiktok_token.py
```

**機能:**
- 認証URL自動生成
- ブラウザ自動起動
- トークン自動取得
- `.env` 自動更新

### 3. `get_token.py` - トークン取得（手動）

**用途:** 認証コードを手動でトークンに交換

```bash
# 1. CODE を更新
# 2. 実行
python get_token.py
```

### 4. `check_tiktok_setup.py` - セットアップ確認

**用途:** すべての設定を確認

```bash
python check_tiktok_setup.py
```

**チェック項目:**
- Pythonパッケージ
- 環境変数
- 必要なファイル
- 動画ファイルサイズ

### 5. `upload_tiktok_auto.py` - 動画アップロード

**用途:** 生成した動画をTikTokにアップロード

```bash
python upload_tiktok_auto.py
```

**前提条件:**
- `today_script.json` が存在
- `out/MyComp.mp4` が存在
- 有効なアクセストークン
- video.upload 権限

---

## 🔄 完全なワークフロー

### 初回セットアップ

```bash
# 1. 依存関係をインストール
pip install -r requirements.txt

# 2. セットアップを確認
python check_tiktok_setup.py

# 3. トークンを取得
python refresh_tiktok_token.py

# 4. 接続をテスト
python test_tiktok_connection.py
```

### 動画作成とアップロード

```bash
# 1. スクリプトを生成
python make_script_auto.py

# 2. 字幕を生成
python make_subtitles_auto.py

# 3. 動画をレンダリング
npx remotion render

# 4. TikTokにアップロード
python upload_tiktok_auto.py
```

### トークンが期限切れの場合

```bash
# 1. 問題を診断
python test_tiktok_connection.py

# 2. トークンを更新
python refresh_tiktok_token.py

# 3. 再度テスト
python test_tiktok_connection.py

# 4. アップロード再試行
python upload_tiktok_auto.py
```

---

## ⚠️ よくあるエラーと解決方法

### エラー: "scope_not_authorized"

**原因:** video.upload 権限がない

**解決方法:**
```bash
python refresh_tiktok_token.py
# 認証時に「すべての権限」を承認
```

### エラー: "invalid_token"

**原因:** トークンが無効または期限切れ

**解決方法:**
```bash
python refresh_tiktok_token.py
```

### エラー: "動画ファイルが見つかりません"

**原因:** 動画がレンダリングされていない

**解決方法:**
```bash
npx remotion render
```

### エラー: "スクリプトファイルが見つかりません"

**原因:** スクリプトが生成されていない

**解決方法:**
```bash
python make_script_auto.py
```

---

## 📋 チェックリスト

アップロード前に確認：

- [ ] `.env` ファイルに `TIKTOK_ACCESS_TOKEN` が設定されている
- [ ] `.env` ファイルに `TIKTOK_OPEN_ID` が設定されている
- [ ] `python test_tiktok_connection.py` がすべて成功
- [ ] `today_script.json` が存在する
- [ ] `out/MyComp.mp4` が存在する
- [ ] 動画サイズが500MB以下

すべてチェックできたら：

```bash
python upload_tiktok_auto.py
```

---

## 🔗 詳細ドキュメント

- **詳細な手順:** [`TIKTOK_TOKEN_REFRESH_GUIDE.md`](TIKTOK_TOKEN_REFRESH_GUIDE.md)
- **セットアップガイド:** [`TIKTOK_SETUP_GUIDE.md`](TIKTOK_SETUP_GUIDE.md)
- **プロジェクト全体:** [`README.md`](README.md)

---

## 💡 ヒント

### トークンの有効期限を確認

```bash
python test_tiktok_connection.py
```

レスポンスに `expires_in` が含まれます（秒単位）

### 定期的なトークン更新

トークンは24時間で期限切れになるため、毎日アップロードする場合は：

1. リフレッシュトークンを保存
2. 自動更新スクリプトを作成
3. または毎回 `refresh_tiktok_token.py` を実行

### デバッグモード

詳細なログを確認したい場合は、スクリプト内の `log_info` 関数を確認してください。

---

**最終更新:** 2026-07-12
**問題が解決しない場合:** `python test_tiktok_connection.py` の出力を確認してください
