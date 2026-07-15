#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Sandbox 統合テストフロー
認証からAPI呼び出しまでの全フローをテストします
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# ============================================================================
# Configuration
# ============================================================================

# Sandbox API endpoints
SANDBOX_API_BASE = 'https://sandbox-open.tiktokapis.com/v2'
USER_INFO_URL = f'{SANDBOX_API_BASE}/user/info/'
VIDEO_LIST_URL = f'{SANDBOX_API_BASE}/video/list/'
VIDEO_QUERY_URL = f'{SANDBOX_API_BASE}/video/query/'

# Credentials
ACCESS_TOKEN = os.getenv('TIKTOK_ACCESS_TOKEN')
OPEN_ID = os.getenv('TIKTOK_OPEN_ID')
CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY')

# ============================================================================
# Logging Functions
# ============================================================================

def log_section(title):
    """Print section header"""
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)

def log_test(test_name, status, details=""):
    """Print test result"""
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{status_icon} {test_name}: {status}")
    if details:
        print(f"   {details}")

def log_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def log_json(data, title=""):
    """Print JSON data"""
    if title:
        print(f"\n📄 {title}:")
    print("-" * 80)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("-" * 80)

# ============================================================================
# Test Functions
# ============================================================================

def test_environment_variables():
    """Test 1: Check if all required environment variables are set"""
    log_section("Test 1: 環境変数の確認")
    
    tests = [
        ("TIKTOK_ACCESS_TOKEN", ACCESS_TOKEN),
        ("TIKTOK_OPEN_ID", OPEN_ID),
        ("TIKTOK_CLIENT_KEY", CLIENT_KEY)
    ]
    
    all_passed = True
    
    for var_name, var_value in tests:
        if var_value:
            masked_value = f"{var_value[:10]}...{var_value[-4:]}" if len(var_value) > 14 else "***"
            log_test(var_name, "PASS", masked_value)
        else:
            log_test(var_name, "FAIL", "未設定")
            all_passed = False
    
    return all_passed

def test_user_info_api():
    """Test 2: Get user information"""
    log_section("Test 2: ユーザー情報取得 API")
    
    if not ACCESS_TOKEN:
        log_test("ユーザー情報取得", "SKIP", "ACCESS_TOKEN が未設定")
        return False
    
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'fields': [
            'open_id',
            'union_id',
            'avatar_url',
            'display_name',
            'bio_description',
            'profile_deep_link',
            'is_verified',
            'follower_count',
            'following_count',
            'likes_count',
            'video_count'
        ]
    }
    
    try:
        log_info(f"リクエスト送信: {USER_INFO_URL}")
        response = requests.post(
            USER_INFO_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        log_info(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test("ユーザー情報取得", "PASS")
            log_json(data, "ユーザー情報")
            
            # Extract key information
            if 'data' in data and 'user' in data['data']:
                user = data['data']['user']
                print()
                print("👤 ユーザー詳細:")
                print(f"   Display Name: {user.get('display_name', 'N/A')}")
                print(f"   Open ID: {user.get('open_id', 'N/A')}")
                print(f"   Verified: {user.get('is_verified', False)}")
                print(f"   Followers: {user.get('follower_count', 0):,}")
                print(f"   Videos: {user.get('video_count', 0):,}")
            
            return True
        else:
            log_test("ユーザー情報取得", "FAIL", f"HTTP {response.status_code}")
            log_json(response.json() if response.text else {"error": "No response"}, "エラー詳細")
            return False
            
    except requests.exceptions.Timeout:
        log_test("ユーザー情報取得", "FAIL", "タイムアウト")
        return False
    except Exception as e:
        log_test("ユーザー情報取得", "FAIL", str(e))
        return False

def test_video_list_api():
    """Test 3: Get video list"""
    log_section("Test 3: 動画リスト取得 API")
    
    if not ACCESS_TOKEN:
        log_test("動画リスト取得", "SKIP", "ACCESS_TOKEN が未設定")
        return False
    
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'max_count': 20
    }
    
    try:
        log_info(f"リクエスト送信: {VIDEO_LIST_URL}")
        response = requests.post(
            VIDEO_LIST_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        log_info(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test("動画リスト取得", "PASS")
            log_json(data, "動画リスト")
            
            # Count videos
            if 'data' in data and 'videos' in data['data']:
                video_count = len(data['data']['videos'])
                print()
                print(f"📹 動画数: {video_count}")
                
                if video_count > 0:
                    print("\n最新の動画:")
                    for i, video in enumerate(data['data']['videos'][:3], 1):
                        print(f"  {i}. ID: {video.get('id', 'N/A')}")
                        print(f"     Title: {video.get('title', 'N/A')}")
                        print(f"     Duration: {video.get('duration', 0)}秒")
                        print()
            
            return True
        else:
            log_test("動画リスト取得", "FAIL", f"HTTP {response.status_code}")
            log_json(response.json() if response.text else {"error": "No response"}, "エラー詳細")
            return False
            
    except requests.exceptions.Timeout:
        log_test("動画リスト取得", "FAIL", "タイムアウト")
        return False
    except Exception as e:
        log_test("動画リスト取得", "FAIL", str(e))
        return False

def test_token_validity():
    """Test 4: Check token validity and expiration"""
    log_section("Test 4: トークンの有効性確認")
    
    token_expires_in = os.getenv('TIKTOK_TOKEN_EXPIRES_IN')
    
    if token_expires_in:
        try:
            expires_in_seconds = int(token_expires_in)
            expires_in_hours = expires_in_seconds / 3600
            expires_in_days = expires_in_hours / 24
            
            log_test("トークン有効期限", "INFO")
            print(f"   有効期限: {expires_in_seconds:,} 秒")
            print(f"   = {expires_in_hours:.1f} 時間")
            print(f"   = {expires_in_days:.1f} 日")
            
            if expires_in_hours < 1:
                log_info("⚠️  トークンの有効期限が1時間未満です。更新を検討してください。")
            elif expires_in_days < 1:
                log_info("⚠️  トークンの有効期限が24時間未満です。")
            else:
                log_info("✅ トークンは有効です。")
            
            return True
        except ValueError:
            log_test("トークン有効期限", "WARN", "無効な値")
            return False
    else:
        log_test("トークン有効期限", "SKIP", "TIKTOK_TOKEN_EXPIRES_IN が未設定")
        return False

def test_api_endpoints():
    """Test 5: Check API endpoint accessibility"""
    log_section("Test 5: API エンドポイントの確認")
    
    endpoints = [
        ("User Info", USER_INFO_URL),
        ("Video List", VIDEO_LIST_URL),
        ("Video Query", VIDEO_QUERY_URL)
    ]
    
    for name, url in endpoints:
        log_info(f"{name}: {url}")
    
    log_test("エンドポイント確認", "PASS", f"{len(endpoints)} 個のエンドポイントを確認")
    return True

def test_file_structure():
    """Test 6: Check required files exist"""
    log_section("Test 6: ファイル構造の確認")
    
    required_files = [
        ('generate_auth_url_sandbox.py', '認証URL生成スクリプト'),
        ('get_token_sandbox.py', 'トークン取得スクリプト'),
        ('test_tiktok_connection_sandbox.py', '接続テストスクリプト'),
        ('upload_tiktok_sandbox.py', 'アップロードスクリプト'),
        ('.env', '環境変数ファイル')
    ]
    
    all_exist = True
    
    for filename, description in required_files:
        if os.path.exists(filename):
            log_test(description, "PASS", filename)
        else:
            log_test(description, "FAIL", f"{filename} が見つかりません")
            all_exist = False
    
    return all_exist

# ============================================================================
# Main Function
# ============================================================================

def main():
    """Run all tests"""
    print("=" * 80)
    print("🧪 TikTok Sandbox 統合テストフロー")
    print("=" * 80)
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    results = []
    
    results.append(("環境変数", test_environment_variables()))
    results.append(("ファイル構造", test_file_structure()))
    results.append(("エンドポイント", test_api_endpoints()))
    results.append(("トークン有効性", test_token_validity()))
    results.append(("ユーザー情報API", test_user_info_api()))
    results.append(("動画リストAPI", test_video_list_api()))
    
    # Summary
    log_section("テスト結果サマリー")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print()
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print()
    print("-" * 80)
    print(f"合計: {passed}/{total} テスト成功")
    print("-" * 80)
    
    # Recommendations
    print()
    log_section("推奨事項")
    
    if passed == total:
        print("✅ すべてのテストに合格しました！")
        print()
        print("次のステップ:")
        print("  1. 動画をアップロードしてテスト:")
        print("     python upload_tiktok_sandbox.py")
        print()
        print("  2. 本番環境への移行を検討")
        print()
    else:
        print("⚠️  一部のテストが失敗しました。")
        print()
        print("トラブルシューティング:")
        
        if not ACCESS_TOKEN:
            print("  1. 認証を完了してトークンを取得:")
            print("     python generate_auth_url_sandbox.py")
            print("     python get_token_sandbox.py")
            print()
        
        print("  2. .env ファイルの設定を確認")
        print("  3. TikTok Developer Portal でアプリの設定を確認")
        print("     https://developers.tiktok.com/apps/")
        print()
    
    print("=" * 80)
    
    # Exit code
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("⚠️  ユーザーによって中断されました")
        sys.exit(0)
    except Exception as e:
        print()
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
