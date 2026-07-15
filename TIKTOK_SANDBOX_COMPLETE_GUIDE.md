# 🎯 TikTok Sandbox 完全ガイド

## 📋 目次

1. [認証待機中に完了した作業](#認証待機中に完了した作業)
2. [新規作成ファイル一覧](#新規作成ファイル一覧)
3. [認証成功後の実行フロー](#認証成功後の実行フロー)
4. [トラブルシューティング](#トラブルシューティング)
5. [API仕様準拠の確認](#api仕様準拠の確認)

---

## ✅ 認証待機中に完了した作業

### 1. **Sandbox専用アップロードスクリプト** ✅
- **ファイル:** [`upload_tiktok_sandbox.py`](upload_tiktok_sandbox.py)
- **機能:**
  - Sandbox環境専用エンドポイント使用
  - 動画ファイルの自動検証
  - リトライロジック実装（最大3回）
  - 詳細なログ出力
  - エラーハンドリング強化

### 2. **統合テストフロー** ✅
- **ファイル:** [`test_sandbox_flow.py`](test_sandbox_flow.py)
- **テスト項目:**
  - 環境変数の確認
  - ファイル構造の検証
  - APIエンドポイントの確認
  - トークン有効性チェック
  - ユーザー情報取得API
  - 動画リスト取得API

### 3. **動画バリデーションツール** ✅
- **ファイル:** [`validate_video.py`](validate_video.py)
- **検証項目:**
  - ファイル存在確認
  - ファイル形式（MP4, MOV, WEBM）
  - ファイルサイズ（最大500MB）
  - 動画長さ（3秒〜10分）
  - 解像度（540x960 〜 4096x4096）
  - アスペクト比（9:16推奨）
  - フレームレート（24/30/60fps推奨）
  - ビットレート（最大50Mbps）
  - 音声ストリーム

---

## 📁 新規作成ファイル一覧

| ファイル名 | 説明 | 用途 |
|-----------|------|------|
| `upload_tiktok_sandbox.py` | Sandbox専用アップロード | 動画投稿 |
| `test_sandbox_flow.py` | 統合テストスクリプト | 全体動作確認 |
| `validate_video.py` | 動画バリデーションツール | アップロード前検証 |
| `TIKTOK_SANDBOX_WAIT_PLAN.md` | 待機中作業計画 | 作業ガイド |
| `TIKTOK_SANDBOX_COMPLETE_GUIDE.md` | 完全ガイド（本ファイル） | 総合ドキュメント |

---

## 🚀 認証成功後の実行フロー

### Phase 1: 認証とトークン取得（15-30分後）

```bash
# ステップ1: 認証URLを生成
python generate_auth_url_sandbox.py

# ステップ2: ブラウザで認証URLにアクセス
# → TikTokアカウントでログイン
# → 権限を承認
# → リダイレクトURLをコピー

# ステップ3: トークンを取得
python get_token_sandbox.py
# → リダイレクトURLを貼り付け
# → .envファイルに自動保存
```

### Phase 2: 接続テストと検証

```bash
# ステップ4: 基本的な接続テスト
python test_tiktok_connection_sandbox.py

# ステップ5: 統合テストフロー実行
python test_sandbox_flow.py

# ステップ6: 動画ファイルの検証
python validate_video.py out/MyComp.mp4
```

### Phase 3: 動画アップロード

```bash
# ステップ7: Sandbox環境に動画をアップロード
python upload_tiktok_sandbox.py
```

---

## 🔧 各スクリプトの詳細

### 1. upload_tiktok_sandbox.py

**主な機能:**
- Sandbox API エンドポイント使用
- 環境変数の自動検証
- 動画ファイルの詳細検証
- スクリプトデータからタイトル・説明文を自動生成
- リトライロジック（最大3回、指数バックオフ）
- 詳細なログ出力

**使用方法:**
```bash
python upload_tiktok_sandbox.py
```

**必要な環境変数:**
- `TIKTOK_ACCESS_TOKEN` - アクセストークン
- `TIKTOK_OPEN_ID` - ユーザーのOpen ID（オプション）

**必要なファイル:**
- `out/MyComp.mp4` - アップロードする動画
- `today_script.json` - スクリプトデータ（オプション）
- `video_config.json` - 動画設定（オプション）

---

### 2. test_sandbox_flow.py

**テスト項目:**

1. **環境変数の確認**
   - `TIKTOK_ACCESS_TOKEN`
   - `TIKTOK_OPEN_ID`
   - `TIKTOK_CLIENT_KEY`

2. **ファイル構造の確認**
   - 必要なスクリプトファイルの存在確認

3. **APIエンドポイントの確認**
   - User Info API
   - Video List API
   - Video Query API

4. **トークン有効性チェック**
   - 有効期限の確認
   - 警告表示（24時間未満の場合）

5. **ユーザー情報取得API**
   - ユーザープロフィール取得
   - フォロワー数、動画数などの表示

6. **動画リスト取得API**
   - アップロード済み動画の一覧取得

**使用方法:**
```bash
python test_sandbox_flow.py
```

**出力例:**
```
✅ PASS  環境変数
✅ PASS  ファイル構造
✅ PASS  エンドポイント
✅ PASS  トークン有効性
✅ PASS  ユーザー情報API
✅ PASS  動画リストAPI

合計: 6/6 テスト成功
```

---

### 3. validate_video.py

**検証項目:**

1. **ファイル存在確認**
   - ファイルパスの検証

2. **ファイル形式確認**
   - サポート形式: MP4, MOV, WEBM

3. **ファイルサイズ確認**
   - 最大: 500MB
   - 空ファイルチェック

4. **動画プロパティ確認**（ffmpeg/ffprobe使用）
   - 動画長さ: 3秒〜10分
   - 解像度: 540x960 〜 4096x4096
   - アスペクト比: 9:16推奨
   - フレームレート: 24/30/60fps推奨
   - ビットレート: 最大50Mbps
   - 音声ストリーム

**使用方法:**
```bash
# 引数で指定
python validate_video.py out/MyComp.mp4

# または対話的に入力
python validate_video.py
```

**注意:**
- ffmpeg/ffprobeがインストールされていない場合、基本的な検証のみ実行
- 詳細な検証にはffmpegのインストールを推奨

---

## 🔍 トラブルシューティング

### 問題1: 認証URLで「client_key」エラー

**原因:**
- TikTok側の設定反映遅延（15-30分）

**解決策:**
1. 15-30分待機
2. ブラウザのキャッシュをクリア
3. シークレットウィンドウで再試行

---

### 問題2: トークン取得時のエラー

**原因:**
- 認証コードの期限切れ（通常5分）
- Client Secretの誤り
- Redirect URIの不一致

**解決策:**
```bash
# 1. 新しい認証コードを取得
python generate_auth_url_sandbox.py

# 2. .envファイルのClient Secretを確認
# TIKTOK_CLIENT_SECRET=ycxoo16kRrW1FXq8epI1EvBQtk42uQex

# 3. Redirect URIを確認
# TIKTOK_REDIRECT_URI=https://google.com
```

---

### 問題3: 動画アップロード失敗

**原因:**
- トークンの権限不足
- 動画ファイルの要件不適合
- ネットワークエラー

**解決策:**
```bash
# 1. トークンの権限を確認
python test_sandbox_flow.py

# 2. 動画ファイルを検証
python validate_video.py out/MyComp.mp4

# 3. 動画を再エンコード（必要に応じて）
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium \
       -c:a aac -b:a 128k output.mp4
```

---

## 📊 API仕様準拠の確認

### Content Posting API v2 準拠

すべてのスクリプトは TikTok Content Posting API v2 に準拠しています。

**エンドポイント:**
- Sandbox: `https://sandbox-open.tiktokapis.com/v2`
- 本番: `https://open.tiktokapis.com/v2`

**主要API:**
1. **OAuth Token**
   - `POST /oauth/token/` - トークン取得

2. **User Info**
   - `POST /user/info/` - ユーザー情報取得

3. **Video List**
   - `POST /video/list/` - 動画リスト取得

4. **Video Upload**
   - `POST /post/publish/video/init/` - アップロード初期化
   - `PUT [upload_url]` - 動画ファイルアップロード

**必要な権限（Scopes）:**
- `user.info.basic` - ユーザー情報取得
- `video.list` - 動画リスト取得
- `video.upload` - 動画アップロード
- `video.publish` - 動画公開

---

## 📈 次のステップ

### 認証成功後（即座に実行）

1. **接続テスト**
   ```bash
   python test_sandbox_flow.py
   ```

2. **動画検証**
   ```bash
   python validate_video.py out/MyComp.mp4
   ```

3. **テストアップロード**
   ```bash
   python upload_tiktok_sandbox.py
   ```

### Sandbox環境で確認後

1. **本番環境への移行準備**
   - 本番アプリの作成
   - App Reviewの申請
   - 本番用スクリプトの準備

2. **自動化の実装**
   - スケジュール投稿
   - バッチ処理
   - エラー通知

---

## 🎓 学習リソース

### 公式ドキュメント
- [TikTok for Developers](https://developers.tiktok.com/)
- [Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [OAuth 2.0 Guide](https://developers.tiktok.com/doc/oauth-user-access-token-management)

### プロジェクト内ドキュメント
- [`TIKTOK_SANDBOX_QUICK_START.md`](TIKTOK_SANDBOX_QUICK_START.md) - クイックスタート
- [`TIKTOK_SANDBOX_README.md`](TIKTOK_SANDBOX_README.md) - 詳細説明
- [`TIKTOK_API_V2_LATEST_SPEC.md`](TIKTOK_API_V2_LATEST_SPEC.md) - API仕様

---

## ⚠️ 重要な注意事項

### Sandbox環境の制限
- テストユーザーのみアクセス可能
- 動画は公開されない（テスト環境内のみ）
- 一部機能が制限される可能性
- レート制限が本番環境と異なる場合がある

### セキュリティ
- `.env`ファイルをGitにコミットしない
- アクセストークンを公開しない
- Client Secretを安全に管理

### トークン管理
- アクセストークン有効期限: 通常24時間
- リフレッシュトークン有効期限: 通常365日
- 定期的な更新が必要

---

## 📞 サポート

### 問題が発生した場合

1. **ログを確認**
   - スクリプトの詳細なログ出力を確認

2. **テストを実行**
   ```bash
   python test_sandbox_flow.py
   ```

3. **ドキュメントを参照**
   - プロジェクト内のMDファイル
   - TikTok公式ドキュメント

4. **設定を再確認**
   - `.env`ファイル
   - TikTok Developer Portal

---

**作成日時:** 2026-07-12 19:13 JST  
**バージョン:** 1.0  
**ステータス:** 認証待機中の準備完了 ✅
