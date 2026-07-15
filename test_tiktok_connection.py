#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Production API Connection Test Script
本番環境（Production）のTikTok APIへの接続をテストします
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

# TikTok API credentials
TIKTOK_ACCESS_TOKEN = os.getenv('TIKTOK_ACCESS_TOKEN')
TIKTOK_OPEN_ID = os.getenv('TIKTOK_OPEN_ID')
CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY_PROD', os.getenv('TIKTOK_CLIENT_KEY', ''))

# TikTok API endpoints (Production)
TIKTOK_API_BASE = 'https://open.tiktokapis.com/v2'

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_section(title):
    """Print formatted section"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)

def test_environment_variables():
    """Test if environment variables are set"""
    print_section("環境変数チェック")
    
    issues = []
    
    # Client Key check
    if CLIENT_KEY:
        print(f"  ✓ TIKTOK_CLIENT_KEY: {CLIENT_KEY}")
        if CLIENT_KEY.startswith("sbaw"):
            print("    ⚠️  Sandbox用のClient Keyが検出されました")
            print("    本番環境では 'aw' で始まるClient Keyを使用してください")
            issues.append("Sandbox用のClient Keyを使用している")
        elif CLIENT_KEY.startswith("aw"):
            print("    ✓ Production用のClient Key (正常)")
    else:
        print("  ⚠️  TIKTOK_CLIENT_KEY が設定されていません")
    
    if not TIKTOK_ACCESS_TOKEN:
        print("  ✗ TIKTOK_ACCESS_TOKEN が設定されていません")
        issues.append("TIKTOK_ACCESS_TOKEN が未設定")
    else:
        print(f"  ✓ TIKTOK_ACCESS_TOKEN: {TIKTOK_ACCESS_TOKEN[:30]}...")
        print(f"    長さ: {len(TIKTOK_ACCESS_TOKEN)} 文字")
    
    if not TIKTOK_OPEN_ID:
        print("  ⚠️  TIKTOK_OPEN_ID が設定されていません（オプション）")
        print("    一部のAPIで必要になる場合があります")
    else:
        print(f"  ✓ TIKTOK_OPEN_ID: {TIKTOK_OPEN_ID}")
    
    print(f"\n  📡 API エンドポイント: {TIKTOK_API_BASE}")
    print("     (Production環境)")
    
    return len(issues) == 0, issues

def test_token_format():
    """Test if token format looks valid"""
    print_section("トークン形式チェック")
    
    if not TIKTOK_ACCESS_TOKEN:
        print("  ✗ トークンが設定されていません")
        return False, ["トークン未設定"]
    
    issues = []
    
    # Check token format (TikTok tokens typically start with 'act.')
    if TIKTOK_ACCESS_TOKEN.startswith('act.'):
        print("  ✓ トークン形式が正しいようです (act. で始まる)")
    else:
        print("  ⚠ トークン形式が通常と異なります")
        print(f"    現在のトークン: {TIKTOK_ACCESS_TOKEN[:50]}...")
        issues.append("トークン形式が通常と異なる")
    
    # Check if token contains placeholder text
    if 'your-tiktok-access-token' in TIKTOK_ACCESS_TOKEN.lower():
        print("  ✗ プレースホルダーテキストが含まれています")
        issues.append("プレースホルダーが残っている")
    
    return len(issues) == 0, issues

def test_user_info():
    """Test API connection by fetching user info"""
    print_section("ユーザー情報取得テスト")
    
    if not TIKTOK_ACCESS_TOKEN:
        print("  ✗ トークンが設定されていないためスキップ")
        return False, ["トークン未設定"]
    
    url = f"{TIKTOK_API_BASE}/user/info/"
    headers = {
        'Authorization': f'Bearer {TIKTOK_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'fields': 'open_id,union_id,avatar_url,display_name'
    }
    
    try:
        print(f"  リクエスト送信中: {url}")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"  ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("  ✓ API接続成功！")
            print("\n  レスポンス:")
            print(json.dumps(data, indent=4, ensure_ascii=False))
            return True, []
        else:
            print(f"  ✗ API接続失敗")
            print(f"\n  エラーレスポンス:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=4, ensure_ascii=False))
                
                # Parse error details
                if 'error' in error_data:
                    error_code = error_data.get('error', {}).get('code', 'unknown')
                    error_message = error_data.get('error', {}).get('message', 'unknown')
                    return False, [f"API Error: {error_code} - {error_message}"]
            except:
                print(response.text)
            
            return False, [f"HTTP {response.status_code}"]
    
    except requests.exceptions.Timeout:
        print("  ✗ リクエストタイムアウト")
        return False, ["タイムアウト"]
    except requests.exceptions.RequestException as e:
        print(f"  ✗ リクエストエラー: {e}")
        return False, [str(e)]
    except Exception as e:
        print(f"  ✗ 予期しないエラー: {e}")
        return False, [str(e)]

def test_video_upload_permissions():
    """Test if token has video upload permissions"""
    print_section("動画アップロード権限テスト")
    
    if not TIKTOK_ACCESS_TOKEN:
        print("  ✗ トークンが設定されていないためスキップ")
        return False, ["トークン未設定"]
    
    # Try to initialize a video upload (without actually uploading)
    url = f"{TIKTOK_API_BASE}/post/publish/video/init/"
    headers = {
        'Authorization': f'Bearer {TIKTOK_ACCESS_TOKEN}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    
    # Minimal payload to test permissions
    payload = {
        'post_info': {
            'title': 'Test',
            'privacy_level': 'SELF_ONLY'
        },
        'source_info': {
            'source': 'FILE_UPLOAD'
        }
    }
    
    try:
        print(f"  リクエスト送信中: {url}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"  ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✓ 動画アップロード権限あり！")
            data = response.json()
            print("\n  レスポンス:")
            print(json.dumps(data, indent=4, ensure_ascii=False))
            return True, []
        else:
            print(f"  ✗ 動画アップロード権限テスト失敗")
            print(f"\n  エラーレスポンス:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=4, ensure_ascii=False))
                
                # Check for specific permission errors
                if 'error' in error_data:
                    error_code = error_data.get('error', {}).get('code', '')
                    error_message = error_data.get('error', {}).get('message', '')
                    
                    if 'permission' in error_message.lower() or 'scope' in error_message.lower():
                        return False, ["video.upload 権限がありません"]
                    elif 'token' in error_message.lower() or 'invalid' in error_message.lower():
                        return False, ["トークンが無効または期限切れ"]
                    else:
                        return False, [f"API Error: {error_code} - {error_message}"]
            except:
                print(response.text)
            
            return False, [f"HTTP {response.status_code}"]
    
    except Exception as e:
        print(f"  ✗ エラー: {e}")
        return False, [str(e)]

def print_troubleshooting_guide(all_issues):
    """Print troubleshooting guide based on issues found"""
    print_header("トラブルシューティングガイド")
    
    if not all_issues:
        print("\n  ✓ すべてのテストに合格しました！")
        print("  TikTok APIへの接続は正常です。")
        return
    
    print("\n  以下の問題が見つかりました:\n")
    for i, issue in enumerate(all_issues, 1):
        print(f"  {i}. {issue}")
    
    print("\n" + "-" * 70)
    print("  解決方法:")
    print("-" * 70)
    
    # Provide specific solutions based on issues
    if any('トークン未設定' in issue or 'プレースホルダー' in issue for issue in all_issues):
        print("\n  📝 トークンを取得する必要があります:")
        print("     1. TikTok Developer Portal にアクセス")
        print("        https://developers.tiktok.com/")
        print("     2. アプリを作成/選択")
        print("     3. OAuth 2.0 認証フローでアクセストークンを取得")
        print("     4. .env ファイルに設定")
    
    if any('無効' in issue or '期限切れ' in issue for issue in all_issues):
        print("\n  🔄 トークンを再取得する必要があります:")
        print("     1. get_token.py を更新")
        print("     2. 新しい認証コードを取得")
        print("     3. python get_token.py を実行")
        print("     4. 取得したトークンを .env に設定")
    
    if any('権限' in issue for issue in all_issues):
        print("\n  🔐 アプリの権限を確認してください:")
        print("     1. TikTok Developer Portal でアプリを開く")
        print("     2. 'Scopes' セクションを確認")
        print("     3. 以下の権限が有効か確認:")
        print("        - video.upload")
        print("        - video.publish")
        print("        - user.info.basic")
        print("     4. 権限を追加した場合は、トークンを再取得")
    
    print("\n  📚 詳細なガイド:")
    print("     TIKTOK_SETUP_GUIDE.md を参照してください")

def main():
    """Main test function"""
    print_header("TikTok Production API 接続テスト")
    print(f"\n  実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  環境: Production (本番環境)")
    print(f"  API Base: {TIKTOK_API_BASE}")
    
    all_issues = []
    
    # Run all tests
    success, issues = test_environment_variables()
    all_issues.extend(issues)
    
    success, issues = test_token_format()
    all_issues.extend(issues)
    
    success, issues = test_user_info()
    all_issues.extend(issues)
    
    success, issues = test_video_upload_permissions()
    all_issues.extend(issues)
    
    # Print troubleshooting guide
    print_troubleshooting_guide(all_issues)
    
    # Final summary
    print("\n" + "=" * 80)
    if not all_issues:
        print("  ✓ テスト完了: すべて正常")
        print("  🚀 Production環境への接続が確認できました")
        print("=" * 80)
        print("\n  次のステップ:")
        print("    - python upload_tiktok_auto.py で動画をアップロード")
        print("    - 本番環境では実際のTikTokアカウントに投稿されます")
        return 0
    else:
        print(f"  ✗ テスト完了: {len(all_issues)} 件の問題")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
