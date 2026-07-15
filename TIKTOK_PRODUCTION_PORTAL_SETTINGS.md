# 🔧 TikTok Developer Portal - Production設定ガイド

Developer Portalで**今すぐ設定すべき項目**の完全リストです。

---

## 🎯 最重要: Productionタブを選択

⚠️ **必ず「Production」タブを選択してください**

Developer Portalには2つのタブがあります:
- **Sandbox** タブ（テスト環境用）
- **Production** タブ（本番環境用）← **こちらを使用**

---

## 📋 設定すべき項目一覧

### 1. Client Credentials（認証情報）

**場所**: Developer Portal > アプリ選択 > **Production タブ** > Client Credentials

#### 確認・取得する情報:

```
Client Key:    aw***************
Client Secret: ****************
```

#### 重要なポイント:
- ✅ Client Keyが **`aw`** で始まることを確認
- ❌ `sbaw` で始まる場合はSandboxタブを見ています
- 🔒 Client Secretは絶対に公開しない

#### `.env` ファイルへの設定:

```bash
TIKTOK_CLIENT_KEY_PROD=aw***************
TIKTOK_CLIENT_SECRET_PROD=****************
```

---

### 2. Redirect URI（リダイレクトURI）

**場所**: Developer Portal > アプリ選択 > **Production タブ** > Redirect URI

#### 登録するURI:

```
https://google.com
```

#### 設定手順:
1. Redirect URIセクションを見つける
2. 「Add Redirect URI」または「+」ボタンをクリック
3. `https://google.com` を入力
4. 「Save」または「保存」をクリック

#### 重要なポイント:
- ✅ **Productionタブ**で登録すること
- ✅ 完全一致が必要（末尾の `/` も含めて）
- ✅ 複数のURIを登録可能
- ❌ Sandboxタブで登録しても本番環境では使えません

#### `.env` ファイルへの設定:

```bash
TIKTOK_REDIRECT_URI=https://google.com
```

---

### 3. Scopes（権限）

**場所**: Developer Portal > アプリ選択 > **Production タブ** > Scopes

#### 有効化すべきスコープ:

- ✅ **`user.info.basic`** - ユーザー基本情報（必須）
- ✅ **`video.upload`** - 動画アップロード
- ✅ **`video.publish`** - 動画公開

#### 設定手順:
1. Scopesセクションを見つける
2. 上記3つのスコープにチェックを入れる
3. 「Save」または「保存」をクリック

#### 重要なポイント:
- ⚠️ `video.upload` と `video.publish` は **App Reviewの承認が必要**
- ✅ `user.info.basic` のみならApp Review不要
- ⚠️ App Review未承認の場合、動画アップロードはできません

---

### 4. App Review（アプリ審査）

**場所**: Developer Portal > アプリ選択 > App Review

#### 申請が必要なスコープ:

- `video.upload` - 動画アップロード
- `video.publish` - 動画公開

#### 申請手順:

1. **App Reviewセクションに移動**
   - Developer Portal > アプリ選択 > App Review

2. **スコープを選択**
   - `video.upload` にチェック
   - `video.publish` にチェック

3. **アプリの用途を説明**
   
   例文（英語）:
   ```
   Our application automatically generates and posts short-form videos 
   to TikTok for marketing purposes. We need video.upload and 
   video.publish permissions to enable automated content posting 
   for our users.
   ```
   
   例文（日本語の場合は英訳が必要）:
   ```
   私たちのアプリケーションは、マーケティング目的でショート動画を
   自動生成しTikTokに投稿します。ユーザーの自動コンテンツ投稿を
   可能にするため、video.uploadとvideo.publishの権限が必要です。
   ```

4. **デモ動画・スクリーンショットを提供**
   - アプリの動作を示す動画またはスクリーンショット
   - 動画アップロード機能の使用方法を示す

5. **申請を送信**
   - 「Submit for Review」をクリック

#### 承認までの期間:
- 通常: **1-2週間**
- 場合によっては数日～1ヶ月

#### App Review未承認の場合:
- `user.info.basic` のみ使用可能
- ユーザー情報の取得のみ可能
- 動画のアップロードは**できません**

---

## 🔍 設定の確認方法

### チェックリスト

Developer Portal > **Productionタブ**で以下を確認:

#### Client Credentials
- [ ] Client Keyが表示されている
- [ ] Client Keyが `aw` で始まる（`sbaw` ではない）
- [ ] Client Secretが表示されている
- [ ] `.env` ファイルに設定済み

#### Redirect URI
- [ ] `https://google.com` が登録されている
- [ ] **Productionタブ**で登録されている
- [ ] `.env` ファイルに設定済み

#### Scopes
- [ ] `user.info.basic` が有効
- [ ] `video.upload` が有効
- [ ] `video.publish` が有効

#### App Review
- [ ] `video.upload` の申請済み
- [ ] `video.publish` の申請済み
- [ ] 承認状態を確認（Approved / Pending / Not Submitted）

---

## 📊 設定状態の確認表

| 項目 | 設定場所 | 必須 | 状態 |
|------|---------|------|------|
| Client Key | Productionタブ > Client Credentials | ✅ 必須 | [ ] 完了 |
| Client Secret | Productionタブ > Client Credentials | ✅ 必須 | [ ] 完了 |
| Redirect URI | Productionタブ > Redirect URI | ✅ 必須 | [ ] 完了 |
| user.info.basic | Productionタブ > Scopes | ✅ 必須 | [ ] 完了 |
| video.upload | Productionタブ > Scopes | ⚠️ 動画投稿に必要 | [ ] 完了 |
| video.publish | Productionタブ > Scopes | ⚠️ 動画投稿に必要 | [ ] 完了 |
| App Review申請 | App Review | ⚠️ 動画投稿に必要 | [ ] 完了 |
| App Review承認 | App Review | ⚠️ 動画投稿に必要 | [ ] 待機中 |

---

## 🚨 よくある間違い

### ❌ 間違い1: Sandboxタブで設定している

**症状**: 
- Client Keyが `sbaw` で始まる
- 設定したのに認証エラーが出る

**解決方法**:
- **Productionタブ**を選択し直す
- Production用のClient Key（`aw`で始まる）を取得

---

### ❌ 間違い2: Redirect URIをSandboxタブに登録

**症状**:
- `redirect_uri_mismatch` エラー
- 認証後にエラーが表示される

**解決方法**:
- **Productionタブ**のRedirect URIセクションに登録
- Sandboxタブの設定は本番環境では使えません

---

### ❌ 間違い3: App Reviewを申請していない

**症状**:
- `insufficient_permissions` エラー
- 動画アップロードができない

**解決方法**:
- App Reviewセクションで申請
- 承認を待つ（1-2週間）
- 承認されるまで `user.info.basic` のみ使用可能

---

## 📝 `.env` ファイルの完全な設定例

```bash
# ============================================================================
# TikTok Production Credentials
# ============================================================================

# Production用のClient Key ('aw'で始まる)
TIKTOK_CLIENT_KEY_PROD=aw***************

# Production用のClient Secret
TIKTOK_CLIENT_SECRET_PROD=****************

# Redirect URI (Developer Portalに登録したもの)
TIKTOK_REDIRECT_URI=https://google.com

# ============================================================================
# TikTok Tokens (認証後に自動設定)
# ============================================================================

# アクセストークン (get_token.py で取得)
TIKTOK_ACCESS_TOKEN=

# リフレッシュトークン (get_token.py で取得)
TIKTOK_REFRESH_TOKEN=

# トークン有効期限 (get_token.py で取得)
TIKTOK_TOKEN_EXPIRES_IN=

# Open ID (get_token.py で取得)
TIKTOK_OPEN_ID=

# ============================================================================
# Sandbox Credentials (オプション - 残しておいてもOK)
# ============================================================================

# Sandbox用のClient Key ('sbaw'で始まる)
TIKTOK_CLIENT_KEY=sbaw***************

# Sandbox用のClient Secret
TIKTOK_CLIENT_SECRET=****************
```

---

## 🔗 Developer Portalへのアクセス

### メインページ
https://developers.tiktok.com/apps

### アプリ管理
1. 上記URLにアクセス
2. アプリを選択
3. **「Production」タブ**を選択
4. 各セクションで設定

### 設定セクションの場所

```
Developer Portal
  └── Apps
      └── [あなたのアプリ]
          ├── Sandbox タブ（使用しない）
          └── Production タブ ← ここで設定
              ├── Client Credentials
              ├── Redirect URI
              ├── Scopes
              └── App Review
```

---

## ✅ 設定完了後の次のステップ

すべての設定が完了したら:

1. **認証URLを生成**
   ```bash
   python generate_auth_url.py
   ```

2. **トークンを取得**
   ```bash
   python get_token.py
   ```

3. **接続をテスト**
   ```bash
   python test_tiktok_connection.py
   ```

4. **App Reviewの承認を待つ**
   - 動画アップロードする場合は必須
   - 承認まで1-2週間

5. **動画をアップロード**（App Review承認後）
   ```bash
   python upload_tiktok_auto.py
   ```

---

## 📚 関連ドキュメント

- [`TIKTOK_PRODUCTION_QUICK_START.md`](./TIKTOK_PRODUCTION_QUICK_START.md) - クイックスタートガイド
- [`TIKTOK_PRODUCTION_SETUP_GUIDE.md`](./TIKTOK_PRODUCTION_SETUP_GUIDE.md) - 完全セットアップガイド
- [TikTok Developer Portal](https://developers.tiktok.com/apps)

---

**作成日**: 2026-07-12  
**対象**: TikTok Developer Portal Production環境の設定
