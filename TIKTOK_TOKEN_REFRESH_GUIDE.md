# TikTok アクセストークン更新ガイド

## 🔍 問題の診断結果

テスト結果により、以下のことが判明しました：

- ✅ **トークンは有効です** - ユーザー情報の取得に成功
- ❌ **`video.upload` 権限がありません** - 動画アップロードに必要な権限が不足

## 📋 必要な権限（Scopes）

TikTokへの動画アップロードには、以下の権限が必要です：

1. `user.info.basic` - ユーザー基本情報（✅ 取得済み）
2. `video.upload` - 動画アップロード（❌ 未取得）
3. `video.publish` - 動画公開（❌ 未取得）

## 🔧 解決方法

### オプション1: TikTok Developer Portalで権限を追加（推奨）

#### ステップ1: Developer Portalにアクセス

1. [TikTok Developer Portal](https://developers.tiktok.com/) にアクセス
2. ログインして、あなたのアプリを選択

#### ステップ2: 権限（Scopes）を確認・追加

1. アプリの設定ページで **"Scopes"** または **"Permissions"** セクションを探す
2. 以下の権限を有効にする：
   - ✅ `user.info.basic`
   - ✅ `video.upload`
   - ✅ `video.publish`
3. 変更を保存

#### ステップ3: 新しいトークンを取得

権限を追加した後は、**必ず新しいアクセストークンを取得**する必要があります。

```bash
python refresh_tiktok_token.py
```

このスクリプトが以下を実行します：
1. 認証URLを生成
2. ブラウザで認証ページを開く
3. 認証コードを取得
4. アクセストークンに交換
5. `.env` ファイルを自動更新

#### ステップ4: 接続テストを実行

```bash
python test_tiktok_connection.py
```

すべてのテストが成功すれば、動画アップロードが可能になります。

---

### オプション2: 手動でトークンを取得

#### ステップ1: 認証URLを生成

以下のURLをブラウザで開きます（CLIENT_KEYは自動的に設定されます）：

```
https://www.tiktok.com/v2/auth/authorize/?client_key=sbawl046rijsqctfgx&scope=user.info.basic,video.upload,video.publish&response_type=code&redirect_uri=https://google.com
```

#### ステップ2: 認証を承認

1. TikTokアカウントでログイン
2. アプリの権限リクエストを確認
3. **すべての権限を承認**（特に video.upload と video.publish）
4. 「承認」をクリック

#### ステップ3: 認証コードを取得

リダイレクト先のURLから `code` パラメータをコピーします：

```
https://google.com/?code=XXXXX&state=XXXXX&scopes=user.info.basic,video.upload,video.publish
```

`code=` の後の値（`XXXXX` の部分）をコピーしてください。

#### ステップ4: get_token.py を更新

[`get_token.py`](get_token.py) を開いて、`CODE` の値を更新します：

```python
# 2. 抽出した最新のコード
CODE = "ここに新しいコードを貼り付け"
```

#### ステップ5: トークンを取得

```bash
python get_token.py
```

成功すると、以下のような出力が表示されます：

```json
{
    "access_token": "act.XXXXX...",
    "open_id": "-000XXXXX...",
    "scope": "user.info.basic,video.upload,video.publish",
    "expires_in": 86400,
    "refresh_token": "rft.XXXXX..."
}
```

#### ステップ6: .env ファイルを更新

取得した `access_token` と `open_id` を [`.env`](.env) ファイルに設定します：

```env
TIKTOK_ACCESS_TOKEN=act.XXXXX...
TIKTOK_OPEN_ID=-000XXXXX...
```

---

## 🧪 テストと確認

### 1. 接続テストを実行

```bash
python test_tiktok_connection.py
```

**期待される結果：**

```
✓ 環境変数チェック - 成功
✓ トークン形式チェック - 成功
✓ ユーザー情報取得テスト - 成功
✓ 動画アップロード権限テスト - 成功

✓ テスト完了: すべて正常
```

### 2. セットアップ確認

```bash
python check_tiktok_setup.py
```

### 3. 動画アップロードを試す

```bash
python upload_tiktok_auto.py
```

---

## 📝 重要な注意事項

### トークンの有効期限

- **アクセストークン**: 通常24時間（86400秒）で期限切れ
- **リフレッシュトークン**: より長期間有効（通常30日）

### トークンのリフレッシュ

トークンが期限切れになった場合、リフレッシュトークンを使用して新しいアクセストークンを取得できます：

```python
# refresh_token.py を作成して実行
import requests

url = "https://open.tiktokapis.com/v2/oauth/token/"
data = {
    "client_key": "sbawl046rijsqctfgx",
    "client_secret": "ycxooL6kRrWlFXq8epIlEvBQtk42uQex",
    "grant_type": "refresh_token",
    "refresh_token": "あなたのリフレッシュトークン"
}

response = requests.post(url, data=data)
print(response.json())
```

### セキュリティ

- ⚠️ **アクセストークンは機密情報です** - 公開しないでください
- ⚠️ **`.env` ファイルを Git にコミットしないでください**
- ✅ `.gitignore` に `.env` が含まれていることを確認

---

## 🔗 参考リンク

- [TikTok Developer Portal](https://developers.tiktok.com/)
- [TikTok Content Posting API Documentation](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [TikTok OAuth 2.0 Documentation](https://developers.tiktok.com/doc/oauth-user-access-token-management)

---

## 🆘 トラブルシューティング

### エラー: "scope_not_authorized"

**原因**: トークンに必要な権限がありません

**解決方法**: 
1. Developer Portalで権限を追加
2. 新しいトークンを取得（上記の手順に従う）

### エラー: "invalid_token" または "token_expired"

**原因**: トークンが無効または期限切れ

**解決方法**:
1. リフレッシュトークンを使用して更新
2. または新しいトークンを取得

### エラー: "code_expired"

**原因**: 認証コードの有効期限が切れています（通常5分）

**解決方法**:
1. 認証プロセスを最初からやり直す
2. コードを取得したらすぐに使用する

### 動画アップロードが失敗する

**確認事項**:
1. 動画ファイルが存在するか（`out/MyComp.mp4`）
2. 動画サイズが500MB以下か
3. すべての権限が付与されているか
4. トークンが有効か

---

## 📞 サポート

問題が解決しない場合：

1. `python test_tiktok_connection.py` の出力を確認
2. エラーメッセージを記録
3. [TikTok Developer Support](https://developers.tiktok.com/support) に問い合わせ

---

**最終更新**: 2026-07-12
