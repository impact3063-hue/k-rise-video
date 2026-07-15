# TikTok Scope エラーの解決方法

## 問題の概要

[`refresh_tiktok_token.py`](refresh_tiktok_token.py:1) を実行した際に、TikTok側で以下のエラーが表示される：

```
TikTokにログインできません。アプリの設定が原因かもしれません。
修正してください： scope
```

これは、TikTok Developer Portal側でアプリに必要な権限（scope）が承認されていないことが原因です。

---

## 解決方法

### 方法1: 最小限の権限でトークンを取得（推奨・即座に実行可能）

最小限の権限（`user.info.basic`のみ）でトークンを取得し、API接続をテストします。

#### 手順

1. **現在実行中のスクリプトを中止**
   - ターミナルで `Ctrl+C` を押してスクリプトを停止

2. **最小権限版スクリプトを実行**
   ```bash
   python refresh_tiktok_token_minimal.py
   ```

3. **ブラウザで認証**
   - スクリプトの指示に従ってブラウザで認証
   - `user.info.basic` のみの権限なので、エラーなく承認できるはずです

4. **接続テスト**
   ```bash
   python test_tiktok_connection.py
   ```

#### 制限事項
- この方法では**動画アップロードはできません**
- API接続のテストと基本的なユーザー情報の取得のみ可能

---

### 方法2: TikTok Developer Portalで権限を申請（動画アップロードに必要）

動画アップロード機能を使用するには、TikTok Developer Portal側で追加の権限を申請・承認する必要があります。

#### 必要な権限（Scopes）

- ✅ `user.info.basic` - ユーザー基本情報（通常は自動承認）
- ⚠️ `video.upload` - 動画アップロード（申請が必要）
- ⚠️ `video.publish` - 動画公開（申請が必要）

#### TikTok Developer Portalでの設定手順

1. **TikTok for Developers にログイン**
   - URL: https://developers.tiktok.com/
   - アプリを作成したアカウントでログイン

2. **アプリの管理画面を開く**
   - 「Manage apps」をクリック
   - 該当するアプリ（Client Key: `sbawl046rijsqctfgx`）を選択

3. **Products タブを確認**
   - 左側メニューから「Products」または「Add products」を選択
   - 以下のプロダクトを追加：
     - **Content Posting API** - 動画アップロードに必要

4. **Scopes（権限）を確認・申請**
   - 「Scopes」または「Permissions」タブを開く
   - 以下の権限が有効になっているか確認：
     - `user.info.basic` ✅
     - `video.upload` ⚠️
     - `video.publish` ⚠️
   
   - 権限が無効の場合：
     - 「Request」または「Apply」ボタンをクリック
     - 使用目的を記入（例：「個人の教育コンテンツを自動投稿するため」）
     - 申請を送信

5. **審査を待つ**
   - TikTokの審査には通常 **1〜7営業日** かかります
   - 審査状況はDeveloper Portalで確認できます

6. **承認後、トークンを再取得**
   - 権限が承認されたら、元のスクリプトを実行：
   ```bash
   python refresh_tiktok_token.py
   ```

---

## 現在の状況確認

### アプリの設定を確認するスクリプト

TikTok Developer Portalにアクセスせずに、現在のアプリ設定を確認できます：

```bash
python check_tiktok_setup.py
```

このスクリプトは以下を表示します：
- Client Key
- Redirect URI
- 現在の `.env` ファイルの設定
- 必要な権限のリスト

---

## トラブルシューティング

### Q1: スクリプトを中止する方法は？

**A:** ターミナルで `Ctrl+C` を押してください。スクリプトが即座に停止します。

### Q2: 最小権限版でも同じエラーが出る場合は？

**A:** 以下を確認してください：
1. TikTok Developer Portalでアプリが「Published」状態になっているか
2. Redirect URI が正しく設定されているか（`https://google.com`）
3. Client Key と Client Secret が正しいか

### Q3: 権限申請が却下された場合は？

**A:** 以下の対策を試してください：
1. 申請理由をより詳しく記載する
2. アプリの説明を充実させる
3. プライバシーポリシーとサービス利用規約のURLを追加
4. 個人利用の場合は、その旨を明記する

### Q4: 動画アップロードを今すぐ試したい場合は？

**A:** 残念ながら、TikTokの審査を待つ必要があります。代替案：
1. 最小権限版でAPI接続をテストする
2. 動画生成部分（Remotion）のみを先に完成させる
3. 審査が通るまで、手動でTikTokに動画をアップロードする

---

## 推奨される作業フロー

### 今すぐできること（審査不要）

1. ✅ 最小権限版でトークンを取得
   ```bash
   python refresh_tiktok_token_minimal.py
   ```

2. ✅ API接続をテスト
   ```bash
   python test_tiktok_connection.py
   ```

3. ✅ 動画生成機能を完成させる
   ```bash
   python make_script_auto.py
   python make_subtitles_auto.py
   npm run build
   ```

### 審査後にできること

4. ⏳ 権限が承認されたら、完全版のトークンを取得
   ```bash
   python refresh_tiktok_token.py
   ```

5. ⏳ 動画アップロードをテスト
   ```bash
   python upload_tiktok_auto.py
   ```

---

## まとめ

- **即座に実行可能**: [`refresh_tiktok_token_minimal.py`](refresh_tiktok_token_minimal.py:1) で最小権限のトークンを取得
- **動画アップロードには**: TikTok Developer Portalで `video.upload` と `video.publish` の権限を申請
- **審査期間**: 通常1〜7営業日
- **スクリプトの中止**: `Ctrl+C` で即座に停止可能

---

## 参考リンク

- [TikTok for Developers](https://developers.tiktok.com/)
- [TikTok API Documentation](https://developers.tiktok.com/doc/overview)
- [Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started)
