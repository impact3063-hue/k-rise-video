#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Setup Verification Script
Checks if all requirements for TikTok upload are properly configured
"""

import os
import sys
from pathlib import Path

def check_mark(condition):
    """Return checkmark or X based on condition"""
    return "✓" if condition else "✗"

def main():
    print("=" * 70)
    print("TikTok Upload Setup Verification")
    print("=" * 70)
    print()
    
    all_ok = True
    
    # Check Python packages
    print("📦 Python パッケージ:")
    print("-" * 70)
    
    packages = {
        'requests': 'HTTP リクエスト用',
        'dotenv': '環境変数管理用 (python-dotenv)',
        'json': 'JSON処理用 (標準ライブラリ)',
        'pathlib': 'ファイルパス処理用 (標準ライブラリ)'
    }
    
    for package, description in packages.items():
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"  {check_mark(True)} {package:20s} - {description}")
        except ImportError:
            print(f"  {check_mark(False)} {package:20s} - {description} [未インストール]")
            all_ok = False
            if package == 'dotenv':
                print(f"      → pip install python-dotenv")
            elif package not in ['json', 'pathlib']:
                print(f"      → pip install {package}")
    
    print()
    
    # Check .env file
    print("🔐 環境変数:")
    print("-" * 70)
    
    env_exists = os.path.exists('.env')
    print(f"  {check_mark(env_exists)} .env ファイル存在")
    
    if env_exists:
        from dotenv import load_dotenv
        load_dotenv()
        
        tiktok_token = os.getenv('TIKTOK_ACCESS_TOKEN')
        tiktok_open_id = os.getenv('TIKTOK_OPEN_ID')
        
        token_set = bool(tiktok_token and tiktok_token != 'your-tiktok-access-token-here')
        open_id_set = bool(tiktok_open_id and tiktok_open_id != 'your-tiktok-open-id-here')
        
        print(f"  {check_mark(token_set)} TIKTOK_ACCESS_TOKEN 設定済み")
        if token_set:
            print(f"      → {tiktok_token[:20]}...")
        else:
            print(f"      → .env ファイルに TIKTOK_ACCESS_TOKEN を設定してください")
            all_ok = False
        
        print(f"  {check_mark(open_id_set)} TIKTOK_OPEN_ID 設定済み")
        if open_id_set:
            print(f"      → {tiktok_open_id[:20]}...")
        else:
            print(f"      → .env ファイルに TIKTOK_OPEN_ID を設定してください")
            all_ok = False
    else:
        print(f"      → .env.example をコピーして .env を作成してください")
        all_ok = False
    
    print()
    
    # Check required files
    print("📁 必要なファイル:")
    print("-" * 70)
    
    files = {
        'upload_tiktok_auto.py': 'アップロードスクリプト',
        'today_script.json': '台本データ (make_script_auto.py で生成)',
        'out/MyComp.mp4': '動画ファイル (npx remotion render で生成)',
        'video_config.json': '動画設定ファイル'
    }
    
    for file_path, description in files.items():
        exists = os.path.exists(file_path)
        print(f"  {check_mark(exists)} {file_path:30s} - {description}")
        if not exists and file_path in ['today_script.json', 'out/MyComp.mp4']:
            if file_path == 'today_script.json':
                print(f"      → python make_script_auto.py を実行してください")
            elif file_path == 'out/MyComp.mp4':
                print(f"      → npx remotion render を実行してください")
    
    print()
    
    # Check video file size if exists
    if os.path.exists('out/MyComp.mp4'):
        video_size_mb = os.path.getsize('out/MyComp.mp4') / (1024 * 1024)
        size_ok = video_size_mb <= 500
        print("📹 動画ファイル情報:")
        print("-" * 70)
        print(f"  {check_mark(size_ok)} ファイルサイズ: {video_size_mb:.2f} MB")
        if not size_ok:
            print(f"      → TikTokの最大サイズ (500MB) を超えています")
            all_ok = False
        print()
    
    # Summary
    print("=" * 70)
    if all_ok:
        print("✓ すべての確認が完了しました！")
        print()
        print("次のコマンドでTikTokにアップロードできます:")
        print("  python upload_tiktok_auto.py")
    else:
        print("✗ いくつかの問題が見つかりました")
        print()
        print("上記のメッセージを確認して、必要な設定を完了してください。")
        print("詳細は TIKTOK_SETUP_GUIDE.md を参照してください。")
    print("=" * 70)
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())
