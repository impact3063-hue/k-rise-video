#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Sandbox Auto Upload Script
Sandbox環境で動画を自動アップロードするスクリプト
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

# File paths
SCRIPT_FILE = 'today_script.json'
VIDEO_FILE = 'out/MyComp.mp4'
VIDEO_CONFIG_FILE = 'video_config.json'

# TikTok Sandbox API endpoints
TIKTOK_API_BASE = 'https://sandbox-open.tiktokapis.com/v2'
UPLOAD_VIDEO_URL = f'{TIKTOK_API_BASE}/post/publish/video/init/'

# Upload settings
MAX_VIDEO_SIZE_MB = 500  # TikTok max video size
MIN_VIDEO_DURATION_SEC = 3  # Minimum video duration
MAX_VIDEO_DURATION_SEC = 600  # Maximum video duration (10 minutes)
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB chunks for upload

# Supported video formats
SUPPORTED_FORMATS = ['.mp4', '.mov', '.webm']

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

def log_warning(message):
    """Print warning message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[WARNING] {timestamp} - {message}")

# ============================================================================
# Validation Functions
# ============================================================================

def validate_environment():
    """Validate that all required environment variables are set"""
    log_info("環境変数を検証中...")
    
    if not TIKTOK_ACCESS_TOKEN:
        log_error("TIKTOK_ACCESS_TOKEN が .env ファイルに設定されていません")
        log_error("先に認証を完了してください: python get_token_sandbox.py")
        return False
    
    if not TIKTOK_OPEN_ID:
        log_warning("TIKTOK_OPEN_ID が設定されていません（オプション）")
    
    log_success("環境変数の検証が完了しました")
    return True

def validate_video_file():
    """Validate video file exists and meets requirements"""
    log_info("動画ファイルを検証中...")
    
    # Check if file exists
    if not os.path.exists(VIDEO_FILE):
        log_error(f"動画ファイルが見つかりません: {VIDEO_FILE}")
        log_error("先に動画を生成してください: npx remotion render")
        return False
    
    # Check file extension
    file_ext = Path(VIDEO_FILE).suffix.lower()
    if file_ext not in SUPPORTED_FORMATS:
        log_error(f"サポートされていない動画形式: {file_ext}")
        log_error(f"サポート形式: {', '.join(SUPPORTED_FORMATS)}")
        return False
    
    # Check video size
    video_size_bytes = os.path.getsize(VIDEO_FILE)
    video_size_mb = video_size_bytes / (1024 * 1024)
    
    if video_size_mb > MAX_VIDEO_SIZE_MB:
        log_error(f"動画ファイルが大きすぎます: {video_size_mb:.2f}MB")
        log_error(f"最大サイズ: {MAX_VIDEO_SIZE_MB}MB")
        return False
    
    if video_size_bytes == 0:
        log_error("動画ファイルが空です")
        return False
    
    log_success(f"動画ファイル検証完了:")
    log_info(f"  ファイル: {VIDEO_FILE}")
    log_info(f"  サイズ: {video_size_mb:.2f}MB ({video_size_bytes:,} bytes)")
    log_info(f"  形式: {file_ext}")
    
    return True

def validate_files():
    """Validate that all required files exist"""
    log_info("必要なファイルを確認中...")
    
    # Check script file (optional)
    if not os.path.exists(SCRIPT_FILE):
        log_warning(f"スクリプトファイルが見つかりません: {SCRIPT_FILE}")
        log_warning("デフォルトのタイトル・説明文を使用します")
    
    # Check video file (required)
    if not validate_video_file():
        return False
    
    log_success("ファイルの確認が完了しました")
    return True

# ============================================================================
# File Reading Functions
# ============================================================================

def load_script_data():
    """Load script data from today_script.json"""
    log_info(f"スクリプトデータを読み込み中: {SCRIPT_FILE}")
    
    try:
        if not os.path.exists(SCRIPT_FILE):
            log_warning("スクリプトファイルが見つかりません")
            return None
            
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
# Content Generation Functions
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
        title = "K-RISE オーディション動画 [Sandbox Test]"
    
    log_success(f"タイトル: {title}")
    return title

def generate_video_description(script_data, config_data):
    """Generate video description from script and config data"""
    log_info("動画説明を生成中...")
    
    description_parts = []
    
    # Add sandbox notice
    description_parts.append("🧪 [Sandbox Test Video]\n\n")
    
    # Add narration if available
    if script_data and 'narration_body' in script_data:
        description_parts.append(script_data['narration_body'][:500])
    
    # Add CTA if available
    if config_data and 'cta_text' in config_data:
        description_parts.append(f"\n\n{config_data['cta_text']}")
    
    # Add hashtags
    hashtags = "\n\n#KPOP #オーディション #KRISE #韓国 #BTS #SandboxTest"
    description_parts.append(hashtags)
    
    description = ''.join(description_parts)[:2200]  # TikTok description limit
    
    log_success(f"説明文を生成しました ({len(description)} 文字)")
    return description

# ============================================================================
# TikTok API Functions
# ============================================================================

def upload_video_to_tiktok(title, description, max_retries=3):
    """
    Upload video to TikTok Sandbox using Content Posting API v2
    
    Args:
        title: Video title
        description: Video description
        max_retries: Maximum number of retry attempts
    
    Returns:
        dict: Upload result or None if failed
    """
    log_info("TikTok Sandbox API: 動画アップロードを開始...")
    
    headers = {
        'Authorization': f'Bearer {TIKTOK_ACCESS_TOKEN}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    
    # Prepare upload initialization payload
    payload = {
        'post_info': {
            'title': title,
            'description': description,
            'privacy_level': 'SELF_ONLY',  # Sandbox: SELF_ONLY recommended
            'disable_duet': False,
            'disable_comment': False,
            'disable_stitch': False,
            'video_cover_timestamp_ms': 1000
        },
        'source_info': {
            'source': 'FILE_UPLOAD'
        }
    }
    
    for attempt in range(1, max_retries + 1):
        try:
            log_info(f"アップロード試行 {attempt}/{max_retries}...")
            log_info(f"エンドポイント: {UPLOAD_VIDEO_URL}")
            
            # Step 1: Initialize upload
            log_info("ステップ1: アップロードセッションを初期化中...")
            init_response = requests.post(
                UPLOAD_VIDEO_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            log_info(f"レスポンスステータス: {init_response.status_code}")
            
            if init_response.status_code != 200:
                log_error(f"初期化に失敗しました: HTTP {init_response.status_code}")
                log_error(f"レスポンス: {init_response.text}")
                
                if attempt < max_retries:
                    wait_time = attempt * 2
                    log_warning(f"{wait_time}秒後にリトライします...")
                    time.sleep(wait_time)
                    continue
                else:
                    return None
            
            init_data = init_response.json()
            log_info("初期化レスポンス:")
            print(json.dumps(init_data, indent=2, ensure_ascii=False))
            
            # Extract upload URL and publish ID
            if 'data' not in init_data:
                log_error("レスポンスに 'data' フィールドがありません")
                return None
            
            data = init_data['data']
            
            if 'upload_url' not in data:
                log_error("レスポンスに 'upload_url' がありません")
                log_error(f"利用可能なフィールド: {list(data.keys())}")
                return None
            
            upload_url = data['upload_url']
            publish_id = data.get('publish_id', '')
            
            log_success(f"アップロードURL取得成功")
            log_info(f"Publish ID: {publish_id}")
            
            # Step 2: Upload video file
            log_info("ステップ2: 動画ファイルをアップロード中...")
            
            with open(VIDEO_FILE, 'rb') as video_file:
                video_data = video_file.read()
                video_size = len(video_data)
                
                log_info(f"動画サイズ: {video_size:,} bytes ({video_size / (1024*1024):.2f} MB)")
                
                upload_headers = {
                    'Content-Type': 'video/mp4',
                    'Content-Length': str(video_size)
                }
                
                log_info("動画データを送信中...")
                upload_response = requests.put(
                    upload_url,
                    data=video_data,
                    headers=upload_headers,
                    timeout=120
                )
                
                log_info(f"アップロードレスポンス: HTTP {upload_response.status_code}")
                
                if upload_response.status_code in [200, 201, 204]:
                    log_success("動画アップロードが完了しました！")
                    
                    result = {
                        'status': 'success',
                        'publish_id': publish_id,
                        'video_size': video_size,
                        'title': title,
                        'description': description[:100] + '...' if len(description) > 100 else description
                    }
                    
                    return result
                else:
                    log_error(f"動画アップロードに失敗しました: HTTP {upload_response.status_code}")
                    log_error(f"レスポンス: {upload_response.text}")
                    
                    if attempt < max_retries:
                        wait_time = attempt * 2
                        log_warning(f"{wait_time}秒後にリトライします...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return None
                        
        except requests.exceptions.Timeout:
            log_error(f"リクエストタイムアウト (試行 {attempt}/{max_retries})")
            if attempt < max_retries:
                log_warning("リトライします...")
                time.sleep(attempt * 2)
                continue
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            log_error(f"リクエストエラー: {e}")
            if attempt < max_retries:
                log_warning("リトライします...")
                time.sleep(attempt * 2)
                continue
            else:
                return None
                
        except Exception as e:
            log_error(f"予期しないエラー: {e}")
            import traceback
            log_error(traceback.format_exc())
            return None
    
    return None

# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main execution function"""
    print("=" * 80)
    print("🧪 TikTok Sandbox Auto Upload Script")
    print("=" * 80)
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
    config_data = load_video_config()
    
    # Step 4: Generate metadata
    title = generate_video_title(script_data, config_data)
    description = generate_video_description(script_data, config_data)
    
    print()
    print("-" * 80)
    print("📋 アップロード情報:")
    print("-" * 80)
    print(f"タイトル: {title}")
    print(f"説明文: {description[:100]}...")
    print(f"動画ファイル: {VIDEO_FILE}")
    print(f"API Base: {TIKTOK_API_BASE}")
    print("-" * 80)
    print()
    
    # Confirmation
    print("⚠️  Sandbox環境にアップロードします。")
    print("   この動画は公開されず、テスト環境内でのみ確認できます。")
    print()
    response = input("続行しますか？ (y/N): ").strip().lower()
    
    if response != 'y':
        log_info("ユーザーによってキャンセルされました")
        sys.exit(0)
    
    print()
    
    # Step 5: Upload to TikTok Sandbox
    log_info("TikTok Sandboxへのアップロードを開始します...")
    
    result = upload_video_to_tiktok(title, description)
    
    if result:
        print()
        print("=" * 80)
        log_success("🎉 TikTok Sandboxへのアップロードが完了しました！")
        print("=" * 80)
        print()
        print("📊 アップロード結果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()
        log_info("次のステップ:")
        print("  1. TikTok Developer Portal でアップロード状況を確認")
        print("     https://developers.tiktok.com/")
        print("  2. Sandbox環境でテスト動画を確認")
        print("  3. 問題なければ本番環境への移行を検討")
        print()
    else:
        print()
        print("=" * 80)
        log_error("❌ TikTok Sandboxへのアップロードに失敗しました")
        print("=" * 80)
        print()
        log_info("🔍 トラブルシューティング:")
        print("  1. アクセストークンが有効か確認:")
        print("     python test_tiktok_connection_sandbox.py")
        print()
        print("  2. トークンに必要な権限があるか確認:")
        print("     - video.upload")
        print("     - video.publish")
        print()
        print("  3. 動画ファイルが要件を満たしているか確認:")
        print(f"     - 形式: {', '.join(SUPPORTED_FORMATS)}")
        print(f"     - サイズ: 最大 {MAX_VIDEO_SIZE_MB}MB")
        print(f"     - 長さ: {MIN_VIDEO_DURATION_SEC}秒 〜 {MAX_VIDEO_DURATION_SEC}秒")
        print()
        print("  4. TikTok API ドキュメントを確認:")
        print("     https://developers.tiktok.com/doc/content-posting-api-get-started")
        print()
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
