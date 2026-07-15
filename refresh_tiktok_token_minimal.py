#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Token Refresh Script (Minimal Scope Version)
最小限の権限でトークンを取得します
"""

import os
import sys
import json
import requests
import webbrowser
from urllib.parse import urlencode
from dotenv import load_dotenv

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

# TikTok OAuth Configuration
CLIENT_KEY = "sbawl046rijsqctfgx"
CLIENT_SECRET = "ycxooL6kRrWlFXq8epIlEvBQtk42uQex"
REDIRECT_URI = "https://google.com"

# Minimal scope - only basic user info
# これは通常すべてのアプリで利用可能です
SCOPES = [
    'user.info.basic'
]

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_step(step_num, title):
    """Print formatted step"""
    print(f"\n【ステップ {step_num}】 {title}")
    print("-" * 70)

def generate_auth_url():
    """Generate TikTok OAuth authorization URL"""
    print_step(1, "認証URLを生成")
    
    # Generate random state for CSRF protection
    import secrets
    state = secrets.token_urlsafe(16)
    
    params = {
        'client_key': CLIENT_KEY,
        'scope': ','.join(SCOPES),
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': state
    }
    
    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(params)}"
    
    print(f"\n使用する権限 (Scopes):")
    for scope in SCOPES:
        print(f"  - {scope}")
    
    print(f"\n認証URL:")
    print(auth_url)
    
    print(f"\nState (CSRF保護用): {state}")
    
    return auth_url, state

def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
    print_step(3, "認証コードをアクセストークンに交換")
    
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }
    
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    
    try:
        print("\nトークンリクエスト送信中...")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("\n✓ トークン取得成功！")
            print("\nレスポンス:")
            print(json.dumps(token_data, indent=2, ensure_ascii=False))
            
            return token_data
        else:
            print("\n✗ トークン取得失敗")
            print("\nエラーレスポンス:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(response.text)
            return None
    
    except Exception as e:
        print(f"\n✗ エラー: {e}")
        return None

def update_env_file(token_data):
    """Update .env file with new token"""
    print_step(4, ".env ファイルを更新")
    
    if not token_data or 'data' not in token_data:
        print("✗ トークンデータが無効です")
        return False
    
    data = token_data['data']
    access_token = data.get('access_token', '')
    open_id = data.get('open_id', '')
    
    if not access_token:
        print("✗ アクセストークンが見つかりません")
        return False
    
    print(f"\nアクセストークン: {access_token[:30]}...")
    print(f"Open ID: {open_id}")
    
    # Read current .env file
    env_path = '.env'
    env_lines = []
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            env_lines = f.readlines()
    
    # Update or add TikTok credentials
    token_found = False
    open_id_found = False
    
    for i, line in enumerate(env_lines):
        if line.startswith('TIKTOK_ACCESS_TOKEN='):
            env_lines[i] = f'TIKTOK_ACCESS_TOKEN={access_token}\n'
            token_found = True
        elif line.startswith('TIKTOK_OPEN_ID='):
            env_lines[i] = f'TIKTOK_OPEN_ID={open_id}\n'
            open_id_found = True
    
    # Add if not found
    if not token_found:
        env_lines.append(f'TIKTOK_ACCESS_TOKEN={access_token}\n')
    if not open_id_found:
        env_lines.append(f'TIKTOK_OPEN_ID={open_id}\n')
    
    # Write back to .env
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(env_lines)
        
        print("\n✓ .env ファイルを更新しました")
        
        # Show token expiration info
        if 'expires_in' in data:
            expires_in = data['expires_in']
            print(f"\nトークン有効期限: {expires_in} 秒 ({expires_in / 3600:.1f} 時間)")
        
        if 'refresh_token' in data:
            print(f"リフレッシュトークン: {data['refresh_token'][:30]}...")
            print("(リフレッシュトークンは将来の更新に使用できます)")
        
        return True
    
    except Exception as e:
        print(f"\n✗ .env ファイルの更新に失敗: {e}")
        return False

def interactive_mode():
    """Interactive mode to guide user through token refresh"""
    print_header("TikTok アクセストークン更新ツール (最小権限版)")
    
    print("\nこのスクリプトは、最小限の権限 (user.info.basic) でトークンを取得します。")
    print("動画アップロードには追加の権限が必要ですが、まずは接続テストができます。")
    
    # Step 1: Generate auth URL
    auth_url, state = generate_auth_url()
    
    # Step 2: User authorization
    print_step(2, "ブラウザで認証")
    
    print("\n以下の手順を実行してください:")
    print("  1. 上記のURLをブラウザで開く")
    print("  2. TikTokアカウントでログイン")
    print("  3. アプリの権限を承認")
    print("  4. リダイレクト先のURLから 'code' パラメータをコピー")
    print("\nリダイレクト先のURLは以下のような形式です:")
    print("  https://google.com/?code=XXXXX&state=XXXXX&scopes=XXXXX")
    
    # Ask if user wants to open browser
    print("\n")
    open_browser = input("ブラウザで認証URLを開きますか? (y/n): ").strip().lower()
    
    if open_browser == 'y':
        try:
            webbrowser.open(auth_url)
            print("✓ ブラウザで認証URLを開きました")
        except:
            print("✗ ブラウザを開けませんでした。手動でURLを開いてください。")
    
    # Get authorization code from user
    print("\n")
    code = input("リダイレクト先URLから取得した 'code' を入力してください: ").strip()
    
    if not code:
        print("\n✗ コードが入力されませんでした")
        return False
    
    # Exchange code for token
    token_data = exchange_code_for_token(code)
    
    if not token_data:
        print("\n✗ トークン取得に失敗しました")
        return False
    
    # Update .env file
    success = update_env_file(token_data)
    
    if success:
        print_header("完了")
        print("\n✓ トークンの更新が完了しました！")
        print("\n次のステップ:")
        print("  1. python test_tiktok_connection.py でAPI接続をテスト")
        print("\n注意: 動画アップロードには追加の権限が必要です。")
        print("TikTok Developer Portalで video.upload と video.publish の権限を申請してください。")
        return True
    else:
        return False

def main():
    """Main function"""
    success = interactive_mode()
    return 0 if success else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n中断されました (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
