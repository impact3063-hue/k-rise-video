@echo off
chcp 65001 > nul
echo ========================================
echo LINE Bot セットアップウィザード
echo ========================================
echo.
echo このウィザードでは、以下の設定を行います：
echo 1. Cloudflare R2 Object Storage の設定
echo 2. LINE Developers の設定
echo 3. 環境変数ファイル (.env) の作成
echo.
pause

echo.
echo ========================================
echo ステップ 1: Cloudflare R2 の設定
echo ========================================
echo.
echo まず、Cloudflare R2 Object Storage を有効化します。
echo.
echo 【手順】
echo 1. ブラウザで https://dash.cloudflare.com/ を開いてください
echo 2. 左サイドバーから「R2」をクリック
echo 3. 「R2を有効にする」ボタンをクリック（初回のみ）
echo 4. 「バケットを作成」をクリック
echo 5. バケット名を入力（例: k-rise-video-storage）
echo 6. 「作成」をクリック
echo.
pause

echo.
echo 次に、R2 API トークンを作成します。
echo.
echo 【手順】
echo 1. R2 ダッシュボードで「設定」タブをクリック
echo 2. 「R2 API トークンを管理」をクリック
echo 3. 「APIトークンを作成」をクリック
echo 4. 権限: 「オブジェクトの読み取りと書き込み」を選択
echo 5. 「続行」→「作成」をクリック
echo.
pause

echo.
set /p R2_ACCOUNT_ID="R2 Account ID を入力してください: "
set /p R2_ACCESS_KEY_ID="R2 Access Key ID を入力してください: "
set /p R2_SECRET_ACCESS_KEY="R2 Secret Access Key を入力してください: "
set /p R2_BUCKET_NAME="R2 Bucket Name を入力してください: "
set /p R2_PUBLIC_URL="R2 Public URL を入力してください（例: https://pub-xxxxx.r2.dev）: "

echo.
echo ========================================
echo ステップ 2: LINE Developers の設定
echo ========================================
echo.
echo LINE Messaging API チャネルを作成します。
echo.
echo 【手順】
echo 1. ブラウザで https://developers.line.biz/console/ を開いてください
echo 2. 「ログイン」してLINEアカウントでログイン
echo 3. 「新規プロバイダー作成」をクリック（初回のみ）
echo 4. プロバイダー名を入力（例: K-Rise Video）→「作成」
echo 5. 「Messaging APIチャネルを作成」をクリック
echo.
pause

echo.
echo チャネル情報を入力します。
echo.
echo 【手順】
echo - チャネル名: K-Rise Video Bot（任意の名前）
echo - チャネル説明: 動画生成Bot（任意の説明）
echo - 大業種: 適切なカテゴリを選択
echo - 小業種: 適切なカテゴリを選択
echo - メールアドレス: あなたのメールアドレス
echo.
echo 利用規約に同意して「作成」をクリックしてください。
echo.
pause

echo.
echo ========================================
echo ステップ 3: Channel Secret の取得
echo ========================================
echo.
echo 【手順】
echo 1. 作成したチャネルをクリック
echo 2. 「チャネル基本設定」タブを開く
echo 3. 「Channel Secret」の右側にある「表示」ボタンをクリック
echo 4. 表示された値をコピー
echo.
set /p LINE_CHANNEL_SECRET="Channel Secret を貼り付けてください: "

echo.
echo ========================================
echo ステップ 4: Channel Access Token の取得
echo ========================================
echo.
echo 【手順】
echo 1. 「Messaging API設定」タブをクリック
echo 2. 下にスクロールして「チャネルアクセストークン（長期）」セクションを探す
echo 3. 「発行」ボタンをクリック
echo 4. 表示されたトークンをコピー（このトークンは一度しか表示されません！）
echo.
set /p LINE_CHANNEL_ACCESS_TOKEN="Channel Access Token を貼り付けてください: "

echo.
echo ========================================
echo ステップ 5: Webhook URL の設定
echo ========================================
echo.
echo 後でCloudflare Workersをデプロイした後、Webhook URLを設定します。
echo 今はスキップして、.envファイルを作成します。
echo.
pause

echo.
echo ========================================
echo .env ファイルを作成しています...
echo ========================================
echo.

(
echo # Cloudflare R2 Configuration
echo R2_ACCOUNT_ID=%R2_ACCOUNT_ID%
echo R2_ACCESS_KEY_ID=%R2_ACCESS_KEY_ID%
echo R2_SECRET_ACCESS_KEY=%R2_SECRET_ACCESS_KEY%
echo R2_BUCKET_NAME=%R2_BUCKET_NAME%
echo R2_PUBLIC_URL=%R2_PUBLIC_URL%
echo.
echo # LINE Messaging API Configuration
echo LINE_CHANNEL_SECRET=%LINE_CHANNEL_SECRET%
echo LINE_CHANNEL_ACCESS_TOKEN=%LINE_CHANNEL_ACCESS_TOKEN%
echo.
echo # Optional: TikTok Configuration ^(後で設定可能^)
echo # TIKTOK_CLIENT_KEY=
echo # TIKTOK_CLIENT_SECRET=
echo # TIKTOK_ACCESS_TOKEN=
echo # TIKTOK_REFRESH_TOKEN=
) > .env

echo.
echo ✓ .env ファイルが作成されました！
echo.
echo ========================================
echo セットアップ完了！
echo ========================================
echo.
echo 次のステップ:
echo 1. Cloudflare Workers をデプロイ
echo 2. Webhook URL を LINE Developers に設定
echo 3. LINE Bot を友だち追加してテスト
echo.
echo 詳細は SETUP_GUIDE.md を参照してください。
echo.
pause
