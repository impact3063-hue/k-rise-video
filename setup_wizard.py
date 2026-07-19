#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LINE Bot セットアップウィザード
対話型で環境変数を設定します
"""

import os
import sys

def print_header(text):
    """ヘッダーを表示"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")

def print_step(step_num, title):
    """ステップタイトルを表示"""
    print(f"\n{'=' * 60}")
    print(f"ステップ {step_num}: {title}")
    print("=" * 60 + "\n")

def get_input(prompt, required=True):
    """ユーザー入力を取得"""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("⚠️  この項目は必須です。入力してください。\n")

def main():
    print_header("LINE Bot セットアップウィザード")
    
    print("このウィザードでは、以下の設定を行います：")
    print("1. Cloudflare R2 Object Storage の設定")
    print("2. LINE Developers の設定")
    print("3. 環境変数ファイル (.env) の作成")
    print("\n準備ができたら Enter キーを押してください...")
    input()

    # ステップ 1: Cloudflare R2 の設定
    print_step(1, "Cloudflare R2 の設定")
    
    print("まず、Cloudflare R2 Object Storage を有効化します。\n")
    print("【手順】")
    print("1. ブラウザで https://dash.cloudflare.com/ を開いてください")
    print("2. 左サイドバーから「R2」をクリック")
    print("3. 「R2を有効にする」ボタンをクリック（初回のみ）")
    print("4. 「バケットを作成」をクリック")
    print("5. バケット名を入力（例: k-rise-video-storage）")
    print("6. 「作成」をクリック")
    print("\n完了したら Enter キーを押してください...")
    input()

    print("\n次に、R2 API トークンを作成します。\n")
    print("【手順】")
    print("1. R2 ダッシュボードで「設定」タブをクリック")
    print("2. 「R2 API トークンを管理」をクリック")
    print("3. 「APIトークンを作成」をクリック")
    print("4. 権限: 「オブジェクトの読み取りと書き込み」を選択")
    print("5. 「続行」→「作成」をクリック")
    print("6. 表示された情報をメモしてください")
    print("\n完了したら Enter キーを押してください...")
    input()

    print("\n取得した情報を入力してください：\n")
    r2_account_id = get_input("R2 Account ID: ")
    r2_access_key_id = get_input("R2 Access Key ID: ")
    r2_secret_access_key = get_input("R2 Secret Access Key: ")
    r2_bucket_name = get_input("R2 Bucket Name: ")
    r2_public_url = get_input("R2 Public URL (例: https://pub-xxxxx.r2.dev): ")

    # ステップ 2: LINE Developers の設定
    print_step(2, "LINE Developers の設定")
    
    print("LINE Messaging API チャネルを作成します。\n")
    print("【手順】")
    print("1. ブラウザで https://developers.line.biz/console/ を開いてください")
    print("2. 「ログイン」してLINEアカウントでログイン")
    print("3. 「新規プロバイダー作成」をクリック（初回のみ）")
    print("4. プロバイダー名を入力（例: K-Rise Video）→「作成」")
    print("5. 「Messaging APIチャネルを作成」をクリック")
    print("\n完了したら Enter キーを押してください...")
    input()

    print("\nチャネル情報を入力します。\n")
    print("【入力項目】")
    print("- チャネル名: K-Rise Video Bot（任意の名前）")
    print("- チャネル説明: 動画生成Bot（任意の説明）")
    print("- 大業種: 適切なカテゴリを選択")
    print("- 小業種: 適切なカテゴリを選択")
    print("- メールアドレス: あなたのメールアドレス")
    print("\n利用規約に同意して「作成」をクリックしてください。")
    print("完了したら Enter キーを押してください...")
    input()

    # ステップ 3: Channel Secret の取得
    print_step(3, "Channel Secret の取得")
    
    print("【手順】")
    print("1. 作成したチャネルをクリック")
    print("2. 「チャネル基本設定」タブを開く")
    print("3. 「Channel Secret」の右側にある「表示」ボタンをクリック")
    print("4. 表示された値をコピー")
    print()
    
    line_channel_secret = get_input("Channel Secret を貼り付けてください: ")

    # ステップ 4: Channel Access Token の取得
    print_step(4, "Channel Access Token の取得")
    
    print("【手順】")
    print("1. 「Messaging API設定」タブをクリック")
    print("2. 下にスクロールして「チャネルアクセストークン（長期）」セクションを探す")
    print("3. 「発行」ボタンをクリック")
    print("4. 表示されたトークンをコピー")
    print("   ⚠️  このトークンは一度しか表示されません！")
    print()
    
    line_channel_access_token = get_input("Channel Access Token を貼り付けてください: ")

    # ステップ 5: .env ファイルの作成
    print_step(5, ".env ファイルの作成")
    
    print(".env ファイルを作成しています...\n")

    env_content = f"""# Cloudflare R2 Configuration
R2_ACCOUNT_ID={r2_account_id}
R2_ACCESS_KEY_ID={r2_access_key_id}
R2_SECRET_ACCESS_KEY={r2_secret_access_key}
R2_BUCKET_NAME={r2_bucket_name}
R2_PUBLIC_URL={r2_public_url}

# LINE Messaging API Configuration
LINE_CHANNEL_SECRET={line_channel_secret}
LINE_CHANNEL_ACCESS_TOKEN={line_channel_access_token}

# Optional: TikTok Configuration (後で設定可能)
# TIKTOK_CLIENT_KEY=
# TIKTOK_CLIENT_SECRET=
# TIKTOK_ACCESS_TOKEN=
# TIKTOK_REFRESH_TOKEN=
"""

    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)

    print("✅ .env ファイルが作成されました！\n")

    # 完了メッセージ
    print_header("セットアップ完了！")
    
    print("次のステップ:")
    print("1. Cloudflare Workers をデプロイ")
    print("2. Webhook URL を LINE Developers に設定")
    print("3. LINE Bot を友だち追加してテスト")
    print("\n詳細は SETUP_GUIDE.md を参照してください。")
    print("\nEnter キーを押して終了...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  セットアップがキャンセルされました。")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ エラーが発生しました: {e}")
        sys.exit(1)
