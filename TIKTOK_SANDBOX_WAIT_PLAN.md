# 🕐 TikTok Sandbox 認証待機中の作業計画

## 📊 現状分析

### ✅ 完了済み
- `.env`のシークレット誤字修正（l→1）
- URLの完璧な設定
- プログラム側とポータル側の設定統一

### ⏳ 待機中
- TikTok側の認証URL反映（15-30分程度）
- `client_key`エラーの解消

---

## 🎯 待機中に進める作業

### 1. **Sandbox専用アップロードスクリプトの作成** ⭐ 最優先

**問題点:**
- 現在の`upload_tiktok_auto.py`は本番環境用
- Sandbox環境のエンドポイントが異なる

**作成するファイル:**
- `upload_tiktok_sandbox.py` - Sandbox専用アップロードスクリプト

**主な違い:**
```python
# 本番環境
TIKTOK_API_BASE = 'https://open.tiktokapis.com/v2'

# Sandbox環境
TIKTOK_API_BASE = 'https://sandbox-open.tiktokapis.com/v2'
```

---

### 2. **トークン取得後のテストフロー整備**

**作成するファイル:**
- `test_sandbox_flow.py` - 認証からアップロードまでの統合テスト

**テスト項目:**
1. トークン取得の確認
2. ユーザー情報取得（`/v2/user/info/`）
3. 動画情報取得（`/v2/video/list/`）
4. 動画アップロード初期化テスト

---

### 3. **エラーハンドリングとログ機能の強化**

**改善点:**
- より詳細なエラーメッセージ
- リトライロジックの実装
- レート制限対応
- タイムアウト処理の最適化

---

### 4. **API v2仕様への完全準拠**

**確認・更新項目:**
- Content Posting API v2の最新仕様
- 必須パラメータの確認
- レスポンス形式の検証
- エラーコードの網羅

---

### 5. **動画アップロード前のバリデーション**

**追加する検証:**
- 動画フォーマット（MP4, MOV, WEBM）
- 動画サイズ（最大500MB）
- 動画長さ（最小3秒、最大10分）
- 解像度（最小540x960、最大4096x4096）
- ビットレート、フレームレート

---

## 📝 次のステップ（認証成功後）

### Phase 1: トークン取得
```bash
# 1. 認証URLにアクセス（15-30分後）
python generate_auth_url_sandbox.py

# 2. リダイレクトURLからトークン取得
python get_token_sandbox.py

# 3. .envファイルに自動保存
```

### Phase 2: 接続テスト
```bash
# 4. API接続確認
python test_tiktok_connection_sandbox.py

# 5. 統合フローテスト
python test_sandbox_flow.py
```

### Phase 3: 動画アップロード
```bash
# 6. テスト動画のアップロード
python upload_tiktok_sandbox.py
```

---

## 🔧 推奨する作業順序

1. **今すぐ実施:** Sandbox専用アップロードスクリプト作成
2. **今すぐ実施:** 統合テストスクリプト作成
3. **今すぐ実施:** バリデーション機能追加
4. **15-30分後:** 認証URL再試行
5. **認証成功後:** トークン取得とテスト実行

---

## ⚠️ 注意事項

### Sandbox環境の制限
- テストユーザーのみアクセス可能
- 動画は公開されない（テスト環境内のみ）
- 一部機能が制限される可能性

### トークンの有効期限
- アクセストークン: 通常24時間
- リフレッシュトークン: 通常365日
- 定期的な更新が必要

---

## 📚 参考資料

- [TikTok Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [TikTok OAuth 2.0](https://developers.tiktok.com/doc/oauth-user-access-token-management)
- [Video Upload Specifications](https://developers.tiktok.com/doc/content-posting-api-reference-upload-video)

---

**作成日時:** 2026-07-12 19:08 JST
