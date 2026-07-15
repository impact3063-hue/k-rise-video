#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Sandbox設定チェックスクリプト

このスクリプトは、TikTok Sandbox認証に必要な設定が正しく行われているかを確認します。
"""

import os
import sys
from dotenv import load_dotenv

# Windows環境でのUnicode出力を有効化
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# .envファイルを読み込み
load_dotenv()

def check_env_variable(var_name, required=True):
    """環境変数をチェック"""
    value = os.getenv(var_name)
    
    if value:
        # 値の長さに応じてマスク表示
        if len(value) > 10:
            masked_value = value[:4] + "..." + value[-4:]
        else:
            masked_value = value[:2] + "..." if len(value) > 2 else "***"
        
        print(f"✅ {var_name}: {masked_value} (長さ: {len(value)})")
        return True
    else:
        status = "❌ 必須" if required else "⚠️ オプション"
        print(f"{status} {var_name}: 未設定")
        return not required

def main():
    print("=" * 70)
    print("🔍 TikTok Sandbox 設定チェック")
    print("=" * 70)
    print()
    
    # 必須項目のチェック
    print("📋 必須項目:")
    print("-" * 70)
    
    client_key_ok = check_env_variable("TIKTOK_CLIENT_KEY", required=True)
    client_secret_ok = check_env_variable("TIKTOK_CLIENT_SECRET", required=True)
    
    print()
    
    # オプション項目のチェック（トークン取得後に設定される）
    print("📋 オプション項目（認証後に自動設定）:")
    print("-" * 70)
    
    check_env_variable("TIKTOK_OPEN_ID", required=False)
    check_env_variable("TIKTOK_ACCESS_TOKEN", required=False)
    check_env_variable("TIKTOK_REFRESH_TOKEN", required=False)
    check_env_variable("TIKTOK_TOKEN_EXPIRES_IN", required=False)
    
    print()
    print("=" * 70)
    
    # 結果サマリー
    if client_key_ok and client_secret_ok:
        print("✅ 必須項目は全て設定されています！")
        print()
        print("次のステップ:")
        print("1. python generate_auth_url_sandbox.py を実行")
        print("2. 生成されたURLをシークレットウィンドウで開く")
        print("3. TikTokでログインして承認")
        print("4. リダイレクトURLをコピー")
        print("5. python get_token_sandbox.py を実行してトークン取得")
    else:
        print("❌ 必須項目が不足しています")
        print()
        print("修正が必要な項目:")
        
        if not client_key_ok:
            print()
            print("📌 TIKTOK_CLIENT_KEY:")
            print("   1. https://developers.tiktok.com/apps/ にアクセス")
            print("   2. あなたのSandboxアプリを選択")
            print("   3. Basic Information → Client Key をコピー")
            print("   4. .env ファイルに追加:")
            print("      TIKTOK_CLIENT_KEY=sbaw1046rijsqctfgx")
        
        if not client_secret_ok:
            print()
            print("📌 TIKTOK_CLIENT_SECRET:")
            print("   1. https://developers.tiktok.com/apps/ にアクセス")
            print("   2. あなたのSandboxアプリを選択")
            print("   3. Basic Information → Client Secret → [Show] をクリック")
            print("   4. 表示された値をコピー")
            print("   5. .env ファイルに追加:")
            print("      TIKTOK_CLIENT_SECRET=ここにコピーした値を貼り付け")
            print()
            print("   ⚠️ CLIENT_SECRETは秘密情報です。誰にも共有しないでください。")
    
    print("=" * 70)
    print()
    print("📚 詳細なガイド:")
    print("   - TIKTOK_SANDBOX_TEST_USER_GUIDE.md")
    print("   - TIKTOK_FIX_SUMMARY.md")
    print()

if __name__ == "__main__":
    main()
