# 🔍 Redirect URI 統一確認レポート

**作成日時**: 2026-07-12  
**目的**: Production・Sandbox両環境のRedirect URI設定が完全に統一されているか確認

---

## ✅ 確認結果：完全に統一されています

### 📋 現在の設定状況

#### .env ファイル
```
TIKTOK_REDIRECT_URI=https://google.com
```
- ✅ 両環境共通の設定として定義済み
- ✅ URLエンコードなし（生の文字列）
- ✅ スキーム・ドメインが正確

---

## 📝 各スクリプトの検証結果

### 1. generate_auth_url.py (Production用)
**ファイル**: [`generate_auth_url.py`](generate_auth_url.py)

**Redirect URI取得方法**:
```python
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://google.com")
```

**生成されるURL**:
```
https://www.tiktok.com/v2/auth/authorize/?client_key={PROD_KEY}&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```

**検証結果**: ✅ 完全一致
- .envから `https://google.com` を読み込み
- フォールバック値も `https://google.com`
- URLエンコードなし

---

### 2. generate_auth_url_sandbox.py (Sandbox用)
**ファイル**: [`generate_auth_url_sandbox.py`](generate_auth_url_sandbox.py)

**Redirect URI取得方法**:
```python
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://google.com")
```

**生成されるURL**:
```
https://www.tiktok.com/v2/auth/authorize/?client_key={SANDBOX_KEY}&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=random_state
```

**検証結果**: ✅ 完全一致
- .envから `https://google.com` を読み込み
- フォールバック値も `https://google.com`
- URLエンコードなし

---

### 3. get_token.py (Production用)
**ファイル**: [`get_token.py`](get_token.py)

**Redirect URI取得方法**:
```python
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://google.com")
```

**トークン取得リクエスト**:
```python
data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "code": code,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI,  # https://google.com
}
```

**検証結果**: ✅ 完全一致
- 認証URL生成時と同じRedirect URIを使用
- TikTok APIの要件（完全一致）を満たす

---

### 4. get_token_sandbox.py (Sandbox用)
**ファイル**: [`get_token_sandbox.py`](get_token_sandbox.py)

**Redirect URI取得方法**:
```python
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://google.com")
```

**トークン取得リクエスト**:
```python
data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "code": auth_code,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI  # https://google.com
}
```

**検証結果**: ✅ 完全一致
- 認証URL生成時と同じRedirect URIを使用
- TikTok APIの要件（完全一致）を満たす

---

## 🎯 TikTok API仕様との適合性

### Redirect URIの要件
TikTok API v2では、以下の要件があります：

1. **完全一致が必須**
   - 認証URL生成時のRedirect URI
   - トークン取得時のRedirect URI
   - Developer Portalに登録したRedirect URI
   - これら3つが**一言一句完全に一致**する必要がある

2. **URLエンコードの扱い**
   - 認証URL内では生の文字列を使用（ブラウザが自動エンコード）
   - トークン取得時も生の文字列を使用
   - **手動でURLエンコードしてはいけない**

3. **スキーム・ドメイン・パスの一致**
   - `https://google.com` と `https://google.com/` は**別物**
   - `https://google.com` と `http://google.com` も**別物**
   - 大文字小文字も区別される

### 現在の実装の適合性

✅ **すべての要件を満たしています**

| 要件 | 状態 | 詳細 |
|------|------|------|
| 完全一致 | ✅ | すべてのスクリプトが同じ値を使用 |
| URLエンコード | ✅ | 手動エンコードなし |
| スキーム | ✅ | `https://` で統一 |
| ドメイン | ✅ | `google.com` で統一 |
| パス | ✅ | パスなし（末尾スラッシュなし）で統一 |

---

## 🔐 両環境で同じRedirect URIを使用することの妥当性

### TikTok API仕様の確認

**公式ドキュメント**: [TikTok Login Kit Web](https://developers.tiktok.com/doc/login-kit-web)

#### 環境の判別方法
TikTok APIは**Client Keyの接頭辞**で環境を自動判別します：

| 環境 | Client Key接頭辞 | 例 |
|------|-----------------|-----|
| Production | `aw` | `awh14qlqti6zxw90` |
| Sandbox | `sbaw` | `sbaw1046rijsqctfgx` |

#### Redirect URIの扱い
- Redirect URI自体は環境を判別する要素ではない
- 両環境で**同じRedirect URIを使用可能**
- Developer Portalの各環境タブで個別に登録が必要

### ✅ 結論：問題なし

**両環境で `https://google.com` を使用する方針は完全に問題ありません**

理由：
1. TikTok API仕様上、Redirect URIは環境判別に使用されない
2. Client Keyで環境が自動判別される
3. 設定を統一することで、混乱を防げる
4. 公式ドキュメントでも制限は記載されていない

---

## 📊 Developer Portalでの設定手順

### Production環境
1. [TikTok Developer Portal](https://developers.tiktok.com/apps/) にアクセス
2. アプリを選択
3. **「Products」タブ** を開く（Sandboxタブではない）
4. 「Login Kit (Web)」を探す
5. 「Redirect URIs」に以下を入力：
   ```
   https://google.com
   ```
6. 「Save」をクリック

### Sandbox環境
1. 同じアプリの **「Sandbox」タブ** を開く
2. 「Login Kit (Web)」を探す
3. 「Redirect URIs」に以下を入力：
   ```
   https://google.com
   ```
4. 「Save」をクリック

### ⚠️ 重要な注意点
- 両方のタブで**完全に同じURL**を入力する
- 末尾のスラッシュ（`/`）は**付けない**
- 保存後、数分待つ（設定の反映に時間がかかる場合がある）

---

## 🧪 動作確認方法

### 1. Production環境のテスト
```bash
# 認証URL生成
python generate_auth_url.py

# 生成されたURLをブラウザで開く
# → TikTokログイン画面が表示されればOK
# → "client_key is invalid" エラーが出る場合は設定を確認

# リダイレクト後のURLをコピー
# 例: https://google.com/?code=ABC123&state=random_state&scopes=...

# トークン取得
python get_token.py
# → リダイレクトURLを貼り付け
# → アクセストークンが取得できればOK
```

### 2. Sandbox環境のテスト
```bash
# 認証URL生成
python generate_auth_url_sandbox.py

# 生成されたURLをブラウザで開く
# → TikTokログイン画面が表示されればOK

# リダイレクト後のURLをコピー
# 例: https://google.com/?code=XYZ789&state=random_state&scopes=...

# トークン取得
python get_token_sandbox.py
# → リダイレクトURLを貼り付け
# → アクセストークンが取得できればOK
```

---

## 📋 最終チェックリスト

### Developer Portal設定
- [ ] Production環境の「Login Kit (Web)」に `https://google.com` を登録
- [ ] Sandbox環境の「Login Kit (Web)」に `https://google.com` を登録
- [ ] 両方の環境で**完全に同じURL**を入力したことを確認
- [ ] 設定を保存し、数分待った

### ローカル環境設定
- [x] `.env` ファイルに `TIKTOK_REDIRECT_URI=https://google.com` を設定
- [x] `generate_auth_url.py` が正しいRedirect URIを使用
- [x] `generate_auth_url_sandbox.py` が正しいRedirect URIを使用
- [x] `get_token.py` が正しいRedirect URIを使用
- [x] `get_token_sandbox.py` が正しいRedirect URIを使用

### コードの一貫性
- [x] すべてのスクリプトが `.env` から読み込み
- [x] フォールバック値も `https://google.com` で統一
- [x] URLエンコードを使用していない
- [x] 末尾スラッシュなし

---

## 🎉 結論

### ✅ 現在の状態
**すべてのスクリプトが既に完全に統一されています**

- Production用スクリプト: `https://google.com` を使用
- Sandbox用スクリプト: `https://google.com` を使用
- 認証URL生成: `https://google.com` を使用
- トークン取得: `https://google.com` を使用

### 📝 必要な作業
**ローカル側の修正は不要です**

唯一必要な作業は：
1. **Developer Portalで両環境に `https://google.com` を登録**
2. 設定が反映されるまで数分待つ
3. 各環境で認証フローをテスト

### 🚀 次のステップ
1. Developer Portalにアクセス
2. Production・Sandbox両方のタブで Redirect URI を `https://google.com` に設定
3. 保存して数分待つ
4. `python generate_auth_url.py` でProduction環境をテスト
5. `python generate_auth_url_sandbox.py` でSandbox環境をテスト

---

**検証完了日時**: 2026-07-12  
**検証結果**: ✅ すべてのスクリプトが完全に統一されている  
**必要な修正**: なし（Developer Portal側の設定のみ）
