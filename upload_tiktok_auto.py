#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Production Auto Upload Script
本番環境（Production）で動画を自動的にTikTokにアップロードします
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# Configuration
# ============================================================================

# TikTok API credentials from .env
TIKTOK_ACCESS_TOKEN = os.getenv('TIKTOK_ACCESS_TOKEN')
TIKTOK_OPEN_ID = os.getenv('TIKTOK_OPEN_ID')
CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY_PROD', os.getenv('TIKTOK_CLIENT_KEY', ''))

# File paths
SCRIPT_FILE = 'today_script.json'
VIDEO_FILE = 'out/MyComp.mp4'
VIDEO_CONFIG_FILE = 'video_config.json'

# TikTok API endpoints (Production)
TIKTOK_API_BASE = 'https://open.tiktokapis.com/v2'
UPLOAD_INIT_URL = f'{TIKTOK_API_BASE}/post/publish/inbox/video/init/'
UPLOAD_VIDEO_URL = f'{TIKTOK_API_BASE}/post/publish/video/init/'

# Upload settings
MAX_VIDEO_SIZE_MB = 500  # TikTok max video size
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB chunks for upload

# ============================================================================
# Logging Functions
# ============================================================================

def log_info(message):
    """Print info message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[INFO] {timestamp} - {message}")

def log_error(message):
    """Print error message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[ERROR] {timestamp} - {message}", file=sys.stderr)

def log_success(message):
    """Print success message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[SUCCESS] {timestamp} - {message}")

# ============================================================================
# Validation Functions
# ============================================================================

def validate_environment():
    """Validate that all required environment variables are set"""
    log_info("環境変数を検証中...")
    
    issues = []
    
    # Client Key check
    if CLIENT_KEY:
        if CLIENT_KEY.startswith("sbaw"):
            log_error("⚠️  Sandbox用のClient Keyが検出されました")
            log_error("   本番環境では 'aw' で始まるClient Keyを使用してください")
            issues.append("Sandbox用のClient Key")
        else:
            log_info(f"✓ Production Client Key: {CLIENT_KEY}")
    
    if not TIKTOK_ACCESS_TOKEN:
        log_error("TIKTOK_ACCESS_TOKEN が .env ファイルに設定されていません")
        log_error("python get_token.py を実行してトークンを取得してください")
        issues.append("TIKTOK_ACCESS_TOKEN が未設定")
    else:
        log_info(f"✓ Access Token: {TIKTOK_ACCESS_TOKEN[:30]}...")
    
    if not TIKTOK_OPEN_ID:
        log_error("⚠️  TIKTOK_OPEN_ID が .env ファイルに設定されていません")
        log_error("   一部のAPIで必要になる場合があります")
        # OPEN_IDはオプションなので致命的エラーにはしない
    else:
        log_info(f"✓ Open ID: {TIKTOK_OPEN_ID}")
    
    log_info(f"📡 API エンドポイント: {TIKTOK_API_BASE} (Production)")
    
    if issues:
        log_error(f"環境変数の検証に失敗しました: {len(issues)} 件の問題")
        return False
    
    log_success("環境変数の検証が完了しました")
    return True

def validate_files():
    """Validate that all required files exist"""
    log_info("必要なファイルを確認中...")
    
    # Check script file
    if not os.path.exists(SCRIPT_FILE):
        log_error(f"スクリプトファイルが見つかりません: {SCRIPT_FILE}")
        log_error("先に make_script_auto.py を実行してください")
        return False
    
    # Check video file
    if not os.path.exists(VIDEO_FILE):
        log_error(f"動画ファイルが見つかりません: {VIDEO_FILE}")
        log_error("先に動画を生成してください (npx remotion render)")
        return False
    
    # Check video size
    video_size_mb = os.path.getsize(VIDEO_FILE) / (1024 * 1024)
    if video_size_mb > MAX_VIDEO_SIZE_MB:
        log_error(f"動画ファイルが大きすぎます: {video_size_mb:.2f}MB (最大: {MAX_VIDEO_SIZE_MB}MB)")
        return False
    
    log_success(f"ファイルの確認が完了しました (動画サイズ: {video_size_mb:.2f}MB)")
    return True

# ============================================================================
# File Reading Functions
# ============================================================================

def load_script_data():
    """Load script data from today_script.json"""
    log_info(f"スクリプトデータを読み込み中: {SCRIPT_FILE}")
    
    try:
        with open(SCRIPT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        log_success("スクリプトデータの読み込みが完了しました")
        return data
    except json.JSONDecodeError as e:
        log_error(f"JSONファイルの解析に失敗しました: {e}")
        return None
    except Exception as e:
        log_error(f"スクリプトデータの読み込みに失敗しました: {e}")
        return None

def load_video_config():
    """Load video configuration from video_config.json"""
    log_info(f"動画設定を読み込み中: {VIDEO_CONFIG_FILE}")
    
    try:
        if os.path.exists(VIDEO_CONFIG_FILE):
            with open(VIDEO_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            log_success("動画設定の読み込みが完了しました")
            return config
        else:
            log_info("video_config.json が見つかりません（オプション）")
            return {}
    except Exception as e:
        log_error(f"動画設定の読み込みに失敗しました: {e}")
        return {}

# ============================================================================
# TikTok API Functions
# ============================================================================

def generate_video_title(script_data, config_data):
    """Generate video title from script and config data"""
    log_info("動画タイトルを生成中...")
    
    # Try to use theme from config
    if config_data and 'theme' in config_data:
        title = config_data['theme'][:100]  # TikTok title limit
    # Fallback to first part of narration
    elif script_data and 'narration_body' in script_data:
        narration = script_data['narration_body']
        # Take first sentence or first 100 characters
        title = narration.split('。')[0][:100]
    else:
        title = "K-RISE オーディション動画"
    
    log_success(f"タイトル: {title}")
    return title

def generate_video_description(script_data, config_data):
    """Generate video description from script and config data"""
    log_info("動画説明を生成中...")
    
    description_parts = []
    
    # Add narration if available
    if script_data and 'narration_body' in script_data:
        description_parts.append(script_data['narration_body'][:500])
    
    # Add CTA if available
    if config_data and 'cta_text' in config_data:
        description_parts.append(f"\n\n{config_data['cta_text']}")
    
    # Add hashtags
    hashtags = "\n\n#KPOP #オーディション #KRISE #韓国 #BTS"
    description_parts.append(hashtags)
    
    description = ''.join(description_parts)[:2200]  # TikTok description limit
    
    log_success(f"説明文を生成しました ({len(description)} 文字)")
    return description

def init_video_upload():
    """Initialize video upload and get upload URL"""
    log_info("TikTok API: 動画アップロードを初期化中...")
    
    headers = {
        'Authorization': f'Bearer {TIKTOK_ACCESS_TOKEN}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    
    # Get video file info
    video_size = os.path.getsize(VIDEO_FILE)
    
    payload = {
        'source_info': {
            'source': 'FILE_UPLOAD',
            'video_size': video_size,
            'chunk_size': CHUNK_SIZE,
            'total_chunk_count': (video_size + CHUNK_SIZE - 1) // CHUNK_SIZE
        }
    }
    
    try:
        log_info(f"リクエスト送信中: {UPLOAD_VIDEO_URL}")
        response = requests.post(
            UPLOAD_VIDEO_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        log_info(f"レスポンスステータス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            log_success("アップロード初期化が完了しました")
            return result
        else:
            log_error(f"アップロード初期化に失敗しました: {response.status_code}")
            log_error(f"レスポンス: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        log_error("リクエストがタイムアウトしました")
        return None
    except requests.exceptions.RequestException as e:
        log_error(f"リクエストエラー: {e}")
        return None
    except Exception as e:
        log_error(f"予期しないエラー: {e}")
        return None

def upload_video_chunks(upload_url):
    """Upload video file in chunks"""
    log_info("動画ファイルをアップロード中...")
    
    try:
        with open(VIDEO_FILE, 'rb') as video_file:
            chunk_number = 0
            total_size = os.path.getsize(VIDEO_FILE)
            uploaded_size = 0
            
            while True:
                chunk = video_file.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                chunk_number += 1
                uploaded_size += len(chunk)
                progress = (uploaded_size / total_size) * 100
                
                log_info(f"チャンク {chunk_number} をアップロード中... ({progress:.1f}%)")
                
                headers = {
                    'Content-Type': 'video/mp4',
                    'Content-Range': f'bytes {uploaded_size - len(chunk)}-{uploaded_size - 1}/{total_size}'
                }
                
                response = requests.put(
                    upload_url,
                    headers=headers,
                    data=chunk,
                    timeout=60
                )
                
                if response.status_code not in [200, 201, 204]:
                    log_error(f"チャンクアップロードに失敗しました: {response.status_code}")
                    log_error(f"レスポンス: {response.text}")
                    return False
            
            log_success(f"動画アップロードが完了しました ({chunk_number} チャンク)")
            return True
            
    except Exception as e:
        log_error(f"動画アップロード中にエラーが発生しました: {e}")
        return False

def publish_video(publish_id, title, description):
    """Publish the uploaded video to TikTok"""
    log_info("TikTok API: 動画を公開中...")
    
    headers = {
        'Authorization': f'Bearer {TIKTOK_ACCESS_TOKEN}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    
    payload = {
        'post_info': {
            'title': title,
            'description': description,
            'privacy_level': 'SELF_ONLY',  # Change to 'PUBLIC_TO_EVERYONE' for public
            'disable_duet': False,
            'disable_comment': False,
            'disable_stitch': False,
            'video_cover_timestamp_ms': 1000
        },
        'source_info': {
            'source': 'FILE_UPLOAD',
            'publish_id': publish_id
        }
    }
    
    publish_url = f'{TIKTOK_API_BASE}/post/publish/video/init/'
    
    try:
        log_info(f"公開リクエスト送信中: {publish_url}")
        response = requests.post(
            publish_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        log_info(f"レスポンスステータス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            log_success("動画の公開が完了しました！")
            return result
        else:
            log_error(f"動画公開に失敗しました: {response.status_code}")
            log_error(f"レスポンス: {response.text}")
            return None
            
    except Exception as e:
        log_error(f"動画公開中にエラーが発生しました: {e}")
        return None

# ============================================================================
# Alternative: Direct Upload Method
# ============================================================================

def upload_video_direct(title, description):
    """
    Alternative method: Direct video upload using TikTok Content Posting API
    This is a simplified version that may work better depending on your API access level
    """
    log_info("TikTok API: ダイレクトアップロードを試行中...")
    
    headers = {
        'Authorization': f'Bearer {TIKTOK_ACCESS_TOKEN}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    
    # Step 1: Initialize upload
    init_payload = {
        'post_info': {
            'title': title,
            'privacy_level': 'SELF_ONLY',
            'disable_duet': False,
            'disable_comment': False,
            'disable_stitch': False
        },
        'source_info': {
            'source': 'FILE_UPLOAD'
        }
    }
    
    try:
        # Initialize
        log_info("アップロードセッションを初期化中...")
        init_response = requests.post(
            f'{TIKTOK_API_BASE}/post/publish/video/init/',
            headers=headers,
            json=init_payload,
            timeout=30
        )
        
        if init_response.status_code != 200:
            log_error(f"初期化に失敗しました: {init_response.status_code}")
            log_error(f"レスポンス: {init_response.text}")
            return None
        
        init_data = init_response.json()
        log_info(f"初期化レスポンス: {json.dumps(init_data, indent=2, ensure_ascii=False)}")
        
        # Extract upload URL from response
        if 'data' in init_data and 'upload_url' in init_data['data']:
            upload_url = init_data['data']['upload_url']
            publish_id = init_data['data'].get('publish_id', '')
            
            log_info(f"アップロードURL取得成功: {upload_url[:50]}...")
            
            # Upload video file
            with open(VIDEO_FILE, 'rb') as video_file:
                video_data = video_file.read()
                
                log_info(f"動画ファイルをアップロード中... ({len(video_data)} bytes)")
                
                upload_response = requests.put(
                    upload_url,
                    data=video_data,
                    headers={'Content-Type': 'video/mp4'},
                    timeout=120
                )
                
                if upload_response.status_code in [200, 201, 204]:
                    log_success("動画アップロードが完了しました！")
                    log_success(f"Publish ID: {publish_id}")
                    return {'publish_id': publish_id, 'status': 'uploaded'}
                else:
                    log_error(f"動画アップロードに失敗しました: {upload_response.status_code}")
                    log_error(f"レスポンス: {upload_response.text}")
                    return None
        else:
            log_error("アップロードURLが取得できませんでした")
            log_error(f"レスポンス構造: {json.dumps(init_data, indent=2, ensure_ascii=False)}")
            return None
            
    except Exception as e:
        log_error(f"ダイレクトアップロード中にエラーが発生しました: {e}")
        import traceback
        log_error(traceback.format_exc())
        return None

# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main execution function"""
    print("=" * 80)
    print("🚀 TikTok Production Auto Upload Script")
    print("=" * 80)
    print()
    print("⚠️  注意: 本番環境（Production）への投稿です")
    print("   実際のTikTokアカウントに動画が投稿されます")
    print()
    
    # Step 1: Validate environment
    if not validate_environment():
        log_error("環境変数の検証に失敗しました")
        sys.exit(1)
    
    # Step 2: Validate files
    if not validate_files():
        log_error("ファイルの検証に失敗しました")
        sys.exit(1)
    
    # Step 3: Load data
    script_data = load_script_data()
    if not script_data:
        log_error("スクリプトデータの読み込みに失敗しました")
        sys.exit(1)
    
    config_data = load_video_config()
    
    # Step 4: Generate metadata
    title = generate_video_title(script_data, config_data)
    description = generate_video_description(script_data, config_data)
    
    print()
    print("-" * 80)
    print("アップロード情報:")
    print("-" * 80)
    print(f"タイトル: {title}")
    print(f"説明文: {description[:100]}...")
    print(f"動画ファイル: {VIDEO_FILE}")
    print(f"環境: Production (本番環境)")
    print(f"API Base: {TIKTOK_API_BASE}")
    print("-" * 80)
    print()
    
    # Confirmation prompt for production
    print("⚠️  本番環境への投稿を続行しますか？")
    print("   この動画は実際のTikTokアカウントに投稿されます。")
    response = input("続行する場合は 'yes' と入力してください: ").strip().lower()
    
    if response != 'yes':
        log_info("ユーザーによってキャンセルされました")
        sys.exit(0)
    
    print()
    
    # Step 5: Upload to TikTok
    log_info("TikTokへのアップロードを開始します...")
    
    # Try direct upload method
    result = upload_video_direct(title, description)
    
    if result:
        print()
        print("=" * 80)
        log_success("🎉 TikTok Production環境へのアップロードが完了しました！")
        print("=" * 80)
        print()
        print("アップロード結果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()
        log_info("TikTokアプリまたはCreator Centerで動画を確認してください")
        log_info("https://www.tiktok.com/creator-center/content")
        print()
        log_info("📱 本番環境に投稿されました")
        log_info("   実際のTikTokアカウントで動画が確認できます")
    else:
        print()
        print("=" * 80)
        log_error("TikTokへのアップロードに失敗しました")
        print("=" * 80)
        print()
        log_info("トラブルシューティング:")
        print("  1. TIKTOK_ACCESS_TOKEN が有効か確認してください")
        print("     → python test_tiktok_connection.py で接続をテスト")
        print("  2. アクセストークンに video.upload 権限があるか確認してください")
        print("     → Developer Portalの「Scopes」セクションを確認")
        print("  3. App Reviewが承認されているか確認してください")
        print("     → 本番環境では App Review の承認が必要です")
        print("  4. TikTok Developer Portalでアプリの設定を確認してください")
        print("     → https://developers.tiktok.com/apps")
        print("  5. 公式ドキュメントを参照してください")
        print("     → https://developers.tiktok.com/doc/content-posting-api-get-started")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        log_info("ユーザーによって中断されました")
        sys.exit(0)
    except Exception as e:
        print()
        log_error(f"予期しないエラーが発生しました: {e}")
        import traceback
        log_error(traceback.format_exc())
        sys.exit(1)
