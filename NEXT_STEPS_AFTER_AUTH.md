# 🚀 認証成功後の実行手順

## ⏰ 現在の状況

- ✅ `.env`のシークレット修正完了（l→1）
- ✅ URLの完璧な設定完了
- ✅ プログラム側とポータル側の設定統一
- ⏳ **TikTok側の反映待ち（15-30分）**

---

## 📋 15-30分後に実行する手順

### ステップ1: 認証URLの再試行 🔐

```bash
python generate_auth_url_sandbox.py
```

**出力されるURL例:**
```
https://sandbox-www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic,video.list,video.upload&response_type=code&redirect_uri=https://google.com&state=random_state_string
```

**実行:**
1. シークレットウィンドウで上記URLを開く
2. TikTokアカウントでログイン
3. 権限を承認
4. リダイレクト先のURL全体をコピー

---

### ステップ2: トークン取得 🎫

```bash
python get_token_sandbox.py
```

**プロンプトが表示されたら:**
- コピーしたリダイレクトURLを貼り付け
- Enterキーを押す

**成功すると:**
```
✅ トークン取得成功！
📝 .env ファイルに以下を追加してください:
TIKTOK_ACCESS_TOKEN=act.xxx...
TIKTOK_REFRESH_TOKEN=rft.xxx...
TIKTOK_OPEN_ID=xxx...
```

**自動更新を選択:**
```
💾 .env ファイルを自動的に更新しますか？
更新する (y/N): y
```

---

### ステップ3: 接続テスト ✅

```bash
# 基本的な接続テスト
python test_tiktok_connection_sandbox.py

# 統合テストフロー（推奨）
python test_sandbox_flow.py
```

**期待される結果:**
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

### ステップ4: 動画の検証 🎬

```bash
python validate_video.py out/MyComp.mp4
```

**検証項目:**
- ✅ ファイル存在
- ✅ ファイル形式（MP4）
- ✅ ファイルサイズ（< 500MB）
- ✅ 動画長さ（3秒〜10分）
- ✅ 解像度
- ✅ アスペクト比
- ✅ フレームレート
- ✅ ビットレート

---

### ステップ5: 動画アップロード 🚀

```bash
python upload_tiktok_sandbox.py
```

**確認プロンプト:**
```
⚠️  Sandbox環境にアップロードします。
   この動画は公開されず、テスト環境内でのみ確認できます。

続行しますか？ (y/N): y
```

**成功すると:**
```
🎉 TikTok Sandboxへのアップロードが完了しました！

📊 アップロード結果:
{
  "status": "success",
  "publish_id": "xxx...",
  "video_size": 12345678,
  "title": "...",
  "description": "..."
}
```

---

## 🔧 トラブルシューティング

### 問題: 認証URLで依然として「client_key」エラー

**対処法:**
```bash
# 1. さらに15分待機
# 2. ブラウザのキャッシュをクリア
# 3. 別のブラウザで試す
# 4. Developer Portalで設定を再確認
```

---

### 問題: トークン取得時のエラー

**エラー例:**
```json
{
  "error": "invalid_grant",
  "error_description": "Authorization code is invalid or expired"
}
```

**対処法:**
```bash
# 認証コードは5分で期限切れ
# 新しい認証コードを取得
python generate_auth_url_sandbox.py
# → すぐにトークン取得を実行
python get_token_sandbox.py
```

---

### 問題: 動画アップロード失敗

**エラー例:**
```
❌ 初期化に失敗しました: HTTP 401
```

**対処法:**
```bash
# 1. トークンの確認
python test_sandbox_flow.py

# 2. トークンの権限確認
# Developer Portalで以下の権限が有効か確認:
# - user.info.basic
# - video.list
# - video.upload
# - video.publish

# 3. 必要に応じて再認証
python generate_auth_url_sandbox.py
python get_token_sandbox.py
```

---

## 📊 作成済みファイル一覧

### 実行スクリプト
| ファイル | 用途 |
|---------|------|
| [`generate_auth_url_sandbox.py`](generate_auth_url_sandbox.py) | 認証URL生成 |
| [`get_token_sandbox.py`](get_token_sandbox.py) | トークン取得 |
| [`test_tiktok_connection_sandbox.py`](test_tiktok_connection_sandbox.py) | 基本接続テスト |
| [`test_sandbox_flow.py`](test_sandbox_flow.py) | 統合テスト |
| [`validate_video.py`](validate_video.py) | 動画検証 |
| [`upload_tiktok_sandbox.py`](upload_tiktok_sandbox.py) | 動画アップロード |

### ドキュメント
| ファイル | 内容 |
|---------|------|
| [`TIKTOK_SANDBOX_COMPLETE_GUIDE.md`](TIKTOK_SANDBOX_COMPLETE_GUIDE.md) | 完全ガイド |
| [`TIKTOK_SANDBOX_WAIT_PLAN.md`](TIKTOK_SANDBOX_WAIT_PLAN.md) | 待機中作業計画 |
| [`NEXT_STEPS_AFTER_AUTH.md`](NEXT_STEPS_AFTER_AUTH.md) | 本ファイル |

---

## ✨ 新機能・改善点

### 1. Sandbox専用アップロードスクリプト
- ✅ Sandbox環境専用エンドポイント
- ✅ 自動リトライ機能（最大3回）
- ✅ 詳細なログ出力
- ✅ エラーハンドリング強化

### 2. 統合テストフロー
- ✅ 6つのテスト項目
- ✅ 環境変数の自動検証
- ✅ API接続の確認
- ✅ トークン有効性チェック

### 3. 動画バリデーション
- ✅ 8つの検証項目
- ✅ ffmpeg/ffprobe連携
- ✅ 詳細な要件チェック
- ✅ 推奨事項の表示

---

## 🎯 成功の確認方法

### すべてのテストが成功した場合

```
✅ 環境変数の検証完了
✅ 接続テスト成功
✅ 動画検証合格
✅ アップロード完了

→ Sandbox環境でのテストが完了！
→ 本番環境への移行を検討できます
```

---

## 📞 次のアクション

### Sandbox環境で成功後

1. **本番環境への移行準備**
   - 本番アプリの作成
   - App Reviewの申請
   - 本番用の`.env`設定

2. **自動化の実装**
   - スケジュール投稿
   - バッチ処理
   - エラー通知システム

3. **モニタリング**
   - アップロード成功率
   - エラーログ
   - パフォーマンス

---

## ⏰ タイムライン

```
現在時刻: 19:14 JST
↓
15-30分待機
↓
19:30-19:45 JST: 認証URL再試行
↓
トークン取得（5分以内）
↓
接続テスト（2-3分）
↓
動画検証（1分）
↓
動画アップロード（3-5分）
↓
完了！ 🎉
```

---

## 📝 チェックリスト

認証成功後、以下を順番に実行してください：

- [ ] 認証URL生成（`generate_auth_url_sandbox.py`）
- [ ] ブラウザで認証
- [ ] トークン取得（`get_token_sandbox.py`）
- [ ] `.env`ファイル更新確認
- [ ] 接続テスト（`test_sandbox_flow.py`）
- [ ] 動画検証（`validate_video.py`）
- [ ] 動画アップロード（`upload_tiktok_sandbox.py`）
- [ ] Developer Portalで確認

---

**準備完了！** 🚀  
15-30分後に上記の手順を実行してください。

**作成日時:** 2026-07-12 19:14 JST
