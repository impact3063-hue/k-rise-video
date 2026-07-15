# 🚀 TikTok Production環境 クイックスタート

Sandbox環境から本番環境（Production）に切り替えるための最速ガイドです。

---

## ⚡ 5分でできる本番環境セットアップ

### ステップ1: Developer Portalで本番用の認証情報を取得

1. https://developers.tiktok.com/apps にアクセス
2. アプリを選択
3. **「Production」タブ**を選択（Sandboxタブではない！）
4. 以下をコピー:
   - Client Key（`aw` で始まる）
   - Client Secret

### ステップ2: `.env` ファイルを更新

```bash
# 本番用の認証情報を追加
TIKTOK_CLIENT_KEY_PROD=aw***************  # Productionタブから取得
TIKTOK_CLIENT_SECRET_PROD=****************  # Productionタブから取得
TIKTOK_REDIRECT_URI=https://google.com

# 既存のSandbox設定はそのまま残してOK
TIKTOK_CLIENT_KEY=sbaw***************  # Sandbox用
TIKTOK_CLIENT_SECRET=****************  # Sandbox用
```

### ステップ3: Redirect URIを登録

Developer Portal > **Production タブ** > Redirect URI セクション:

```
https://google.com
```

を追加して保存。

### ステップ4: 認証URLを生成

```bash
python generate_auth_url.py
```

生成されたURLをブラウザで開き、TikTokアカウントで承認。

### ステップ5: トークンを取得

```bash
python get_token.py
```

リダイレクトされたURL全体を貼り付け。

取得したトークンを `.env` に追加:

```bash
TIKTOK_ACCESS_TOKEN=act.*********************
TIKTOK_REFRESH_TOKEN=rft.*********************
TIKTOK_TOKEN_EXPIRES_IN=86400
TIKTOK_OPEN_ID=-000*********************
```

### ステップ6: 接続テスト

```bash
python test_tiktok_connection.py
```

すべて ✓ になればOK！

### ステップ7: 動画をアップロード

```bash
python upload_tiktok_auto.py
```

確認プロンプトで `yes` と入力。

---

## ⚠️ 重要な注意事項

### 1. Client Keyの違い

| 環境 | Client Key | 使用するタブ |
|------|-----------|------------|
| Sandbox | `sbaw` で始まる | Sandboxタブ |
| **Production** | **`aw` で始まる** | **Productionタブ** |

### 2. App Reviewが必要

`video.upload` と `video.publish` を使用するには、**App Reviewの承認が必須**です。

#### App Review未承認の場合:
- `user.info.basic` のみ使用可能
- 動画のアップロードはできません

#### App Reviewの申請方法:
1. Developer Portal > App Review
2. 使用したいスコープを選択
3. アプリの用途を説明
4. 申請を送信
5. 承認を待つ（1-2週間）

### 3. 本番環境への投稿

⚠️ **Production環境では実際のTikTokアカウントに投稿されます**

- テスト環境ではありません
- 投稿は公開される可能性があります
- 投稿前に必ず内容を確認してください

---

## 🔍 Sandbox vs Production 比較表

| 項目 | Sandbox | Production |
|------|---------|------------|
| Client Key | `sbaw***` | `aw***` |
| Developer Portalのタブ | Sandboxタブ | **Productionタブ** |
| API Base URL | `sandbox-open.tiktokapis.com` | `open.tiktokapis.com` |
| 認証URL | 共通 | 共通 |
| App Review | 不要 | **必須** |
| 投稿先 | テスト環境 | **本番TikTok** |
| テストユーザー | 必要 | 不要 |
| Redirect URI登録場所 | Sandboxタブ | **Productionタブ** |

---

## 🐛 よくあるエラーと解決方法

### エラー: `client_key` エラー

**原因**: Sandbox用のClient Keyを使用している

**解決方法**:
```bash
# .envファイルを確認
TIKTOK_CLIENT_KEY_PROD=aw***  # 'aw'で始まることを確認
```

Developer Portal > **Productionタブ**で正しいClient Keyを取得。

### エラー: `invalid_client`

**原因**: Client KeyまたはClient Secretが間違っている

**解決方法**:
1. Developer Portal > **Productionタブ**を確認
2. `.env` の `TIKTOK_CLIENT_KEY_PROD` と `TIKTOK_CLIENT_SECRET_PROD` を更新

### エラー: `redirect_uri_mismatch`

**原因**: Redirect URIが登録されていない

**解決方法**:
1. Developer Portal > **Productionタブ** > Redirect URI
2. `https://google.com` を追加
3. 保存

### エラー: `insufficient_permissions`

**原因**: App Reviewが承認されていない

**解決方法**:
1. Developer Portal > App Review を確認
2. `video.upload` と `video.publish` が承認されているか確認
3. 未承認の場合は申請を送信

---

## 📝 チェックリスト

### 初期設定
- [ ] Developer Portal > **Productionタブ**でClient Key取得（`aw`で始まる）
- [ ] `.env` に `TIKTOK_CLIENT_KEY_PROD` を設定
- [ ] `.env` に `TIKTOK_CLIENT_SECRET_PROD` を設定
- [ ] Developer Portal > **Productionタブ**でRedirect URI登録
- [ ] App Review申請（動画アップロードする場合）

### 認証
- [ ] `python generate_auth_url.py` 実行
- [ ] ブラウザで認証
- [ ] `python get_token.py` でトークン取得
- [ ] トークンを `.env` に保存

### テスト
- [ ] `python test_tiktok_connection.py` 成功

### アップロード
- [ ] 動画ファイル準備（`out/MyComp.mp4`）
- [ ] `python upload_tiktok_auto.py` 実行

---

## 📚 詳細ガイド

より詳しい情報は以下を参照:

- [`TIKTOK_PRODUCTION_SETUP_GUIDE.md`](./TIKTOK_PRODUCTION_SETUP_GUIDE.md) - 完全なセットアップガイド
- [TikTok Developer Portal](https://developers.tiktok.com/apps)
- [TikTok API Documentation](https://developers.tiktok.com/doc/overview)

---

## 🎯 まとめ

### Sandboxから本番環境への切り替え手順:

1. ✅ Developer Portal > **Productionタブ**で認証情報取得
2. ✅ `.env` に `TIKTOK_CLIENT_KEY_PROD` と `TIKTOK_CLIENT_SECRET_PROD` を設定
3. ✅ Redirect URIを**Productionタブ**に登録
4. ✅ `python generate_auth_url.py` で認証
5. ✅ `python get_token.py` でトークン取得
6. ✅ `python test_tiktok_connection.py` でテスト
7. ✅ App Reviewの承認を待つ（動画アップロードする場合）
8. ✅ `python upload_tiktok_auto.py` で動画アップロード

### 最も重要なポイント:

⚠️ **Developer Portalで「Productionタブ」を選択すること！**

Sandboxタブではなく、**Productionタブ**で:
- Client Key/Secret を取得
- Redirect URI を登録
- Scopes を設定

これだけで、Sandbox環境の問題を回避して本番環境で動作します。

---

**作成日**: 2026-07-12  
**対象**: Sandbox環境から本番環境への移行
