# -*- coding: utf-8 -*-
"""
字幕セグメント品質チェックスクリプト
v3.1の文節考慮アルゴリズムの効果を検証
"""

import json
import sys
import io

# Windows環境でのUnicode出力対応
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_segmentation_quality(json_path):
    """セグメント品質を分析"""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    subtitles = data.get('subtitles', [])
    
    print("=" * 70)
    print("📊 字幕セグメント品質レポート (v3.1 文節考慮版)")
    print("=" * 70)
    print(f"\n総セグメント数: {len(subtitles)}")
    print(f"バージョン: {data.get('version', 'N/A')}")
    print(f"セグメンテーションエンジン: {data['metadata'].get('segmentationEngine', 'N/A')}")
    print(f"同期モード: {data['metadata'].get('syncMode', 'N/A')}")
    
    # 文字数分布
    char_counts = [len(s['text']) for s in subtitles]
    avg_chars = sum(char_counts) / len(char_counts) if char_counts else 0
    max_chars = max(char_counts) if char_counts else 0
    min_chars = min(char_counts) if char_counts else 0
    
    print(f"\n📏 文字数統計:")
    print(f"   平均: {avg_chars:.1f}文字")
    print(f"   最大: {max_chars}文字")
    print(f"   最小: {min_chars}文字")
    print(f"   推奨範囲(12-15文字)内: {sum(1 for c in char_counts if 12 <= c <= 15)}/{len(char_counts)} ({sum(1 for c in char_counts if 12 <= c <= 15)/len(char_counts)*100:.1f}%)")
    
    # 全セグメント表示
    print(f"\n📝 全セグメント一覧:")
    print("-" * 70)
    
    for i, sub in enumerate(subtitles, 1):
        text = sub['text']
        char_count = len(text)
        start_time = sub['startTime']
        end_time = sub['endTime']
        duration = sub['duration']
        
        # 品質インジケーター
        quality = "✅" if 12 <= char_count <= 15 else "⚠️" if char_count > 15 else "ℹ️"
        
        print(f"{i:2d}. {quality} [{char_count:2d}文字] [{start_time:5.2f}s-{end_time:5.2f}s] {text}")
    
    print("-" * 70)
    
    # 不自然な分割の検出
    print(f"\n🔍 分割品質チェック:")
    
    unnatural_breaks = []
    for i, sub in enumerate(subtitles):
        text = sub['text']
        
        # 単語の途中で切れているパターンを検出
        # 例: 「プロ」で終わる（「プロデューサー」の途中）
        if text.endswith(('プロ', 'デュ', 'サ', '伝', '説の', 'の男', 'あな')):
            unnatural_breaks.append((i+1, text, "単語途中の可能性"))
        
        # 助詞で始まるパターン（不自然な分割）
        if text.startswith(('が', 'を', 'に', 'は', 'の', 'と', 'で')):
            unnatural_breaks.append((i+1, text, "助詞で開始"))
    
    if unnatural_breaks:
        print(f"   ⚠️  不自然な分割の可能性: {len(unnatural_breaks)}件")
        for idx, text, reason in unnatural_breaks[:5]:
            print(f"      - セグメント{idx}: 「{text}」 ({reason})")
    else:
        print(f"   ✅ 不自然な分割は検出されませんでした")
    
    # 句読点での分割チェック
    punctuation_breaks = sum(1 for s in subtitles if s['text'].endswith(('、', '。', '！', '？')))
    print(f"\n✂️  句読点での分割: {punctuation_breaks}/{len(subtitles)} ({punctuation_breaks/len(subtitles)*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("✨ 分析完了")
    print("=" * 70)

if __name__ == "__main__":
    analyze_segmentation_quality("public/video-data-master.json")
