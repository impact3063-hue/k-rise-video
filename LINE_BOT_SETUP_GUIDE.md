# LINE Bot セットアップガイド

このガイドでは、LINE Botの完全なセットアップ手順を1ステップずつ説明します。

---

## 📋 必要なもの

- LINEアカウント
- Cloudflareアカウント（無料）
- ブラウザ（Chrome、Firefox、Edgeなど）

---

## ステップ 1: Cloudflare R2 Object Storage の設定

### 1-1. Cloudflare ダッシュボードにアクセス

1. ブラウザで以下のURLを開いてください：
   ```
   https://dash.cloudflare.com/
   ```

2. Cloudflareアカウントでログイン
   - アカウントがない場合は「Sign Up」から無料登録

### 1-2. R2 を有効化

1. 左サイドバーから **「R2」** をクリック

2. 初回の場合、**「R2を有効にする」** ボタンが表示されるのでクリック
   - クレジットカード情報の入力が求められる場合がありますが、無料枠内であれば課金されません

### 1-3. バケットを作成

1. **「バケットを作成」** ボタンをクリック

2. バケット名を入力：
   ```
   k-rise-video-storage
   ```
   （または任意の名前）

3. リージョン: **「自動」** のまま

4. **「作成」** ボタンをクリック

### 1-4. R2 API トークンを作成

1. R2 ダッシュボードで **「設定」** タブをクリック

2. **「R2 API トークンを管理」** をクリック

3. **「APIトークンを作成」** ボタンをクリック

4. トークン名を入力：
   ```
   k-rise-video-token
   ```

5. 権限を選択：
   - **「オブジェクトの読み取りと書き込み」** を選択

6. **「続行」** → **「作成」** をクリック

7. 表示された以下の情報を **メモ帳などにコピー** してください：
   ```
   Account ID: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Access Key ID: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Secret Access Key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   
   ⚠️ **重要**: Secret Access Key は一度しか表示されません！必ずコピーしてください。

### 1-5. R2 Public URL を取得（オプション）

1. 作成したバケット（k-rise-video-storage）をクリック

2. **「設定」** タブを開く

3. **「パブリックアクセス」** セクションで **「カスタムドメインを接続」** または **「R2.dev サブドメインを許可」** をクリック

4. R2.dev サブドメインを有効化した場合、以下のような URL が表示されます：
   ```
   https://pub-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.r2.dev
   ```
   この URL をコピーしてメモしてください。

---

## ステップ 2: LINE Developers の設定

### 2-1. LINE Developers コンソールにアクセス

1. ブラウザで以下のURLを開いてください：
   ```
   https://developers.line.biz/console/
   ```

2. **「ログイン」** ボタンをクリック

3. LINEアカウントでログイン
   - メールアドレスとパスワード、またはQRコードでログイン

### 2-2. プロバイダーを作成（初回のみ）

1. **「新規プロバイダー作成」** をクリック

2. プロバイダー名を入力：
   ```
   K-Rise Video
   ```
   （または任意の名前）

3. **「作成」** ボタンをクリック

### 2-3. Messaging API チャネルを作成

1. 作成したプロバイダーの画面で **「Messaging APIチャネルを作成」** をクリック

2. 以下の情報を入力：

   | 項目 | 入力内容 |
   |------|----------|
   | チャネル名 | `K-Rise Video Bot` |
   | チャネル説明 | `動画生成Bot` |
   | 大業種 | 適切なカテゴリを選択（例: 個人） |
   | 小業種 | 適切なカテゴリを選択（例: 個人（その他）） |
   | メールアドレス | あなたのメールアドレス |

3. 利用規約を確認し、チェックボックスにチェック

4. **「作成」** ボタンをクリック

---

## ステップ 3: Channel Secret の取得

### 3-1. Channel Secret を表示

1. 作成したチャネル（K-Rise Video Bot）をクリック

2. **「チャネル基本設定」** タブを開く（デフォルトで開いています）

3. 下にスクロールして **「Channel Secret」** セクションを探す

4. **「表示」** ボタンをクリック

5. 表示された値（32文字の英数字）を **コピー** してメモ帳に貼り付けてください：
   ```
   例: 1234567890abcdef1234567890abcdef
   ```

---

## ステップ 4: Channel Access Token の取得

### 4-1. Channel Access Token を発行

1. **「Messaging API設定」** タブをクリック

2. 下にスクロールして **「チャネルアクセストークン（長期）」** セクションを探す

3. **「発行」** ボタンをクリック

4. 表示されたトークン（長い英数字の文字列）を **コピー** してメモ帳に貼り付けてください：
   ```
   例: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...（非常に長い文字列）
   ```

   ⚠️ **重要**: このトークンは一度しか表示されません！必ずコピーしてください。

---

## ステップ 5: .env ファイルの作成

### 5-1. .env ファイルを編集

1. プロジェクトフォルダ（`k-rise-video`）内の **`.env`** ファイルを開く
   - ファイルが存在しない場合は新規作成

2. 以下の内容を貼り付けて、`xxxxx` の部分を実際の値に置き換えてください：

```env
# Cloudflare R2 Configuration
R2_ACCOUNT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
R2_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
R2_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
R2_BUCKET_NAME=k-rise-video-storage
R2_PUBLIC_URL=https://pub-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.r2.dev

# LINE Messaging API Configuration
LINE_CHANNEL_SECRET=1234567890abcdef1234567890abcdef
LINE_CHANNEL_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional: TikTok Configuration (後で設定可能)
# TIKTOK_CLIENT_KEY=
# TIKTOK_CLIENT_SECRET=
# TIKTOK_ACCESS_TOKEN=
# TIKTOK_REFRESH_TOKEN=
```

3. ファイルを **保存** してください

---

## ステップ 6: Webhook URL の設定（後で実施）

Cloudflare Workers をデプロイした後に、以下の手順で Webhook URL を設定します：

1. LINE Developers コンソールで **「Messaging API設定」** タブを開く

2. **「Webhook URL」** セクションで **「編集」** をクリック

3. デプロイした Workers の URL を入力：
   ```
   https://your-worker-name.your-subdomain.workers.dev/webhook
   ```

4. **「Webhookの利用」** を **「オン」** に設定

5. **「検証」** ボタンをクリックして接続を確認

---

## ✅ セットアップ完了チェックリスト

以下の項目がすべて完了していることを確認してください：

- [ ] Cloudflare R2 バケットを作成した
- [ ] R2 API トークンを作成し、情報をメモした
- [ ] LINE Messaging API チャネルを作成した
- [ ] Channel Secret を取得してメモした
- [ ] Channel Access Token を発行してメモした
- [ ] `.env` ファイルに全ての情報を入力した

---

## 🚀 次のステップ

1. **Cloudflare Workers のデプロイ**
   - LINE Bot のバックエンドをデプロイ

2. **Webhook URL の設定**
   - LINE Developers コンソールで Webhook URL を設定

3. **Bot のテスト**
   - LINE Bot を友だち追加してメッセージを送信

詳細は `SETUP_GUIDE.md` を参照してください。

---

## ❓ トラブルシューティング

### Q: R2 の無料枠はどのくらいですか？

A: Cloudflare R2 の無料枠：
- ストレージ: 10 GB/月
- クラス A 操作: 100万リクエスト/月
- クラス B 操作: 1000万リクエスト/月

通常の使用では無料枠内で十分です。

### Q: Channel Access Token を紛失しました

A: 新しいトークンを発行できます：
1. LINE Developers コンソールで「Messaging API設定」タブを開く
2. 「チャネルアクセストークン（長期）」セクションで「再発行」をクリック
3. 新しいトークンをコピーして `.env` ファイルを更新

### Q: .env ファイルはどこにありますか？

A: プロジェクトのルートディレクトリ（`k-rise-video` フォルダ）にあります。
ファイルが見えない場合は、隠しファイルを表示する設定にしてください。

---

## 📞 サポート

問題が発生した場合は、以下のドキュメントを参照してください：
- [Cloudflare R2 ドキュメント](https://developers.cloudflare.com/r2/)
- [LINE Messaging API ドキュメント](https://developers.line.biz/ja/docs/messaging-api/)
