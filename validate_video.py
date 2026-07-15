#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok 動画バリデーションツール
アップロード前に動画ファイルが要件を満たしているか検証します
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================================================
# Configuration
# ============================================================================

# TikTok video requirements
VIDEO_REQUIREMENTS = {
    'formats': ['.mp4', '.mov', '.webm'],
    'max_size_mb': 500,
    'min_duration_sec': 3,
    'max_duration_sec': 600,  # 10 minutes
    'min_resolution': (540, 960),  # width x height
    'max_resolution': (4096, 4096),
    'recommended_aspect_ratios': ['9:16', '1:1', '16:9'],
    'max_bitrate_mbps': 50,
    'recommended_fps': [24, 25, 30, 60],
    'audio_required': False
}

# ============================================================================
# Logging Functions
# ============================================================================

def log_section(title):
    """Print section header"""
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)

def log_check(item, status, details=""):
    """Print validation check result"""
    if status == "PASS":
        icon = "✅"
    elif status == "FAIL":
        icon = "❌"
    elif status == "WARN":
        icon = "⚠️"
    else:
        icon = "ℹ️"
    
    print(f"{icon} {item}: {status}")
    if details:
        print(f"   {details}")

def log_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

# ============================================================================
# Video Analysis Functions
# ============================================================================

def check_ffmpeg_installed():
    """Check if ffmpeg is installed"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def get_video_info(video_path):
    """Get video information using ffprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return None
            
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None

def calculate_aspect_ratio(width, height):
    """Calculate aspect ratio as string"""
    from math import gcd
    divisor = gcd(width, height)
    return f"{width // divisor}:{height // divisor}"

# ============================================================================
# Validation Functions
# ============================================================================

def validate_file_exists(video_path):
    """Validate that video file exists"""
    log_section("1. ファイル存在確認")
    
    if not os.path.exists(video_path):
        log_check("ファイル存在", "FAIL", f"{video_path} が見つかりません")
        return False
    
    log_check("ファイル存在", "PASS", video_path)
    return True

def validate_file_format(video_path):
    """Validate video file format"""
    log_section("2. ファイル形式確認")
    
    file_ext = Path(video_path).suffix.lower()
    
    if file_ext in VIDEO_REQUIREMENTS['formats']:
        log_check("ファイル形式", "PASS", file_ext)
        return True
    else:
        log_check("ファイル形式", "FAIL", 
                 f"{file_ext} はサポートされていません")
        log_info(f"サポート形式: {', '.join(VIDEO_REQUIREMENTS['formats'])}")
        return False

def validate_file_size(video_path):
    """Validate video file size"""
    log_section("3. ファイルサイズ確認")
    
    size_bytes = os.path.getsize(video_path)
    size_mb = size_bytes / (1024 * 1024)
    max_size = VIDEO_REQUIREMENTS['max_size_mb']
    
    print(f"   ファイルサイズ: {size_mb:.2f} MB ({size_bytes:,} bytes)")
    print(f"   最大サイズ: {max_size} MB")
    
    if size_bytes == 0:
        log_check("ファイルサイズ", "FAIL", "ファイルが空です")
        return False
    elif size_mb > max_size:
        log_check("ファイルサイズ", "FAIL", f"{size_mb:.2f} MB > {max_size} MB")
        return False
    else:
        log_check("ファイルサイズ", "PASS", f"{size_mb:.2f} MB")
        return True

def validate_video_properties(video_path):
    """Validate video properties using ffprobe"""
    log_section("4. 動画プロパティ確認")
    
    # Check if ffmpeg/ffprobe is installed
    if not check_ffmpeg_installed():
        log_check("ffmpeg/ffprobe", "WARN", "インストールされていません")
        log_info("詳細な動画分析をスキップします")
        log_info("ffmpegをインストールすると詳細な検証が可能になります")
        return True  # Don't fail if ffmpeg is not available
    
    log_check("ffmpeg/ffprobe", "PASS", "インストール済み")
    
    # Get video info
    video_info = get_video_info(video_path)
    
    if not video_info:
        log_check("動画情報取得", "WARN", "情報を取得できませんでした")
        return True  # Don't fail, just warn
    
    log_check("動画情報取得", "PASS")
    
    # Extract video stream
    video_stream = None
    audio_stream = None
    
    for stream in video_info.get('streams', []):
        if stream.get('codec_type') == 'video' and not video_stream:
            video_stream = stream
        elif stream.get('codec_type') == 'audio' and not audio_stream:
            audio_stream = stream
    
    if not video_stream:
        log_check("動画ストリーム", "FAIL", "動画ストリームが見つかりません")
        return False
    
    all_passed = True
    
    # Check duration
    duration = float(video_info.get('format', {}).get('duration', 0))
    min_duration = VIDEO_REQUIREMENTS['min_duration_sec']
    max_duration = VIDEO_REQUIREMENTS['max_duration_sec']
    
    print()
    print(f"   動画長さ: {duration:.2f} 秒 ({duration / 60:.2f} 分)")
    print(f"   要件: {min_duration} 〜 {max_duration} 秒")
    
    if duration < min_duration:
        log_check("動画長さ", "FAIL", f"{duration:.2f}秒 < {min_duration}秒")
        all_passed = False
    elif duration > max_duration:
        log_check("動画長さ", "FAIL", f"{duration:.2f}秒 > {max_duration}秒")
        all_passed = False
    else:
        log_check("動画長さ", "PASS", f"{duration:.2f} 秒")
    
    # Check resolution
    width = int(video_stream.get('width', 0))
    height = int(video_stream.get('height', 0))
    min_w, min_h = VIDEO_REQUIREMENTS['min_resolution']
    max_w, max_h = VIDEO_REQUIREMENTS['max_resolution']
    
    print()
    print(f"   解像度: {width} x {height}")
    print(f"   最小: {min_w} x {min_h}")
    print(f"   最大: {max_w} x {max_h}")
    
    if width < min_w or height < min_h:
        log_check("解像度", "FAIL", f"解像度が低すぎます")
        all_passed = False
    elif width > max_w or height > max_h:
        log_check("解像度", "FAIL", f"解像度が高すぎます")
        all_passed = False
    else:
        log_check("解像度", "PASS", f"{width} x {height}")
    
    # Check aspect ratio
    aspect_ratio = calculate_aspect_ratio(width, height)
    recommended = VIDEO_REQUIREMENTS['recommended_aspect_ratios']
    
    print()
    print(f"   アスペクト比: {aspect_ratio}")
    print(f"   推奨: {', '.join(recommended)}")
    
    if aspect_ratio in recommended:
        log_check("アスペクト比", "PASS", aspect_ratio)
    else:
        log_check("アスペクト比", "WARN", 
                 f"{aspect_ratio} は推奨されていません")
        log_info("動画は投稿できますが、推奨比率の使用を検討してください")
    
    # Check frame rate
    fps_str = video_stream.get('r_frame_rate', '0/1')
    try:
        num, den = map(int, fps_str.split('/'))
        fps = num / den if den != 0 else 0
    except:
        fps = 0
    
    recommended_fps = VIDEO_REQUIREMENTS['recommended_fps']
    
    print()
    print(f"   フレームレート: {fps:.2f} fps")
    print(f"   推奨: {', '.join(map(str, recommended_fps))} fps")
    
    if fps > 0:
        if any(abs(fps - rec_fps) < 1 for rec_fps in recommended_fps):
            log_check("フレームレート", "PASS", f"{fps:.2f} fps")
        else:
            log_check("フレームレート", "WARN", 
                     f"{fps:.2f} fps は推奨されていません")
    else:
        log_check("フレームレート", "WARN", "取得できませんでした")
    
    # Check bitrate
    bitrate = int(video_info.get('format', {}).get('bit_rate', 0))
    bitrate_mbps = bitrate / 1_000_000
    max_bitrate = VIDEO_REQUIREMENTS['max_bitrate_mbps']
    
    print()
    print(f"   ビットレート: {bitrate_mbps:.2f} Mbps")
    print(f"   最大: {max_bitrate} Mbps")
    
    if bitrate > 0:
        if bitrate_mbps > max_bitrate:
            log_check("ビットレート", "WARN", 
                     f"{bitrate_mbps:.2f} Mbps > {max_bitrate} Mbps")
            log_info("ビットレートが高いですが、投稿は可能です")
        else:
            log_check("ビットレート", "PASS", f"{bitrate_mbps:.2f} Mbps")
    else:
        log_check("ビットレート", "INFO", "取得できませんでした")
    
    # Check audio
    print()
    if audio_stream:
        audio_codec = audio_stream.get('codec_name', 'unknown')
        audio_sample_rate = audio_stream.get('sample_rate', 'unknown')
        log_check("音声ストリーム", "PASS", 
                 f"{audio_codec}, {audio_sample_rate} Hz")
    else:
        if VIDEO_REQUIREMENTS['audio_required']:
            log_check("音声ストリーム", "FAIL", "音声が見つかりません")
            all_passed = False
        else:
            log_check("音声ストリーム", "WARN", "音声がありません")
            log_info("音声なしでも投稿可能ですが、音声付きを推奨します")
    
    return all_passed

# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main validation function"""
    print("=" * 80)
    print("🔍 TikTok 動画バリデーションツール")
    print("=" * 80)
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get video file path
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = input("\n動画ファイルのパスを入力してください: ").strip()
    
    if not video_path:
        print("❌ ファイルパスが指定されていません")
        sys.exit(1)
    
    print(f"\n📹 検証対象: {video_path}")
    
    # Run validations
    results = []
    
    results.append(("ファイル存在", validate_file_exists(video_path)))
    
    if results[-1][1]:  # Only continue if file exists
        results.append(("ファイル形式", validate_file_format(video_path)))
        results.append(("ファイルサイズ", validate_file_size(video_path)))
        results.append(("動画プロパティ", validate_video_properties(video_path)))
    
    # Summary
    log_section("検証結果サマリー")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print()
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {check_name}")
    
    print()
    print("-" * 80)
    print(f"合計: {passed}/{total} 検証項目合格")
    print("-" * 80)
    
    # Recommendations
    print()
    if passed == total:
        print("✅ すべての検証項目に合格しました！")
        print()
        print("この動画はTikTokにアップロード可能です。")
        print()
        print("次のステップ:")
        print("  python upload_tiktok_sandbox.py")
        print()
    else:
        print("❌ 一部の検証項目が失敗しました。")
        print()
        print("動画を修正してから再度アップロードしてください。")
        print()
        print("推奨事項:")
        print("  - 動画編集ソフトで要件を満たすように調整")
        print("  - ffmpegで動画を変換:")
        print(f"    ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium \\")
        print(f"           -c:a aac -b:a 128k output.mp4")
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
