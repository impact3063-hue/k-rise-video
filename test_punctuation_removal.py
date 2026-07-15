# -*- coding: utf-8 -*-
"""
🎯 句読点完全除去システム - テストスクリプト

このスクリプトは以下をテストします:
1. video-data-master.json内のすべてのテキストに句読点が含まれていないことを確認
2. 各文字データ（characters配列）に句読点が含まれていないことを確認
3. レガシーフォーマット（sample-video.json）も確認
"""

import json
import re
import sys
from typing import List, Dict, Any

# Windows環境でのUnicode出力対応
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 句読点検出用の正規表現（Guard Aと同じパターン）
STRICT_PUNCTUATION_REGEX = re.compile(
    r'[、，,。．.・･\u3001\u3002\uFF0C\uFF0E\u30FB\uFF65]'
)

# より広範囲の記号検出用
EXTENDED_PUNCTUATION_REGEX = re.compile(
    r'[、，,。．.・･！？!?…‥「」『』（）()【】［］\[\]〈〉《》〔〕｛｝\{\}〜～'
    r'\u3000-\u303F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]'
)


def detect_punctuation(text: str, strict: bool = True) -> List[str]:
    """テキスト内の句読点を検出"""
    if not text:
        return []
    
    regex = STRICT_PUNCTUATION_REGEX if strict else EXTENDED_PUNCTUATION_REGEX
    matches = regex.findall(text)
    return list(set(matches)) if matches else []


def test_video_data_master():
    """video-data-master.jsonのテスト"""
    print("=" * 70)
    print("🎯 Testing video-data-master.json")
    print("=" * 70)
    
    try:
        with open("public/video-data-master.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: public/video-data-master.json not found")
        print("   Please run: python generate_video_data_master.py")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format: {e}")
        return False
    
    all_passed = True
    total_subtitles = len(data.get("subtitles", []))
    total_characters = 0
    punctuation_found = []
    
    print(f"\n📊 Total subtitles: {total_subtitles}")
    
    # 各字幕をテスト
    for i, subtitle in enumerate(data.get("subtitles", [])):
        subtitle_id = subtitle.get("id", f"sub_{i}")
        text = subtitle.get("text", "")
        characters = subtitle.get("characters", [])
        
        # テキストフィールドのチェック
        punct_in_text = detect_punctuation(text, strict=True)
        if punct_in_text:
            all_passed = False
            punctuation_found.append({
                "subtitle_id": subtitle_id,
                "location": "text",
                "text": text,
                "punctuation": punct_in_text
            })
            print(f"❌ [{subtitle_id}] Punctuation found in text: {punct_in_text}")
            print(f"   Text: {text}")
        
        # 各文字データのチェック
        for j, char_data in enumerate(characters):
            char = char_data.get("char", "")
            total_characters += 1
            
            punct_in_char = detect_punctuation(char, strict=True)
            if punct_in_char:
                all_passed = False
                punctuation_found.append({
                    "subtitle_id": subtitle_id,
                    "location": f"characters[{j}]",
                    "char": char,
                    "punctuation": punct_in_char
                })
                print(f"❌ [{subtitle_id}] Punctuation found in character[{j}]: {punct_in_char}")
                print(f"   Char: '{char}'")
    
    print(f"\n📊 Total characters checked: {total_characters}")
    
    if all_passed:
        print("\n✅ PASSED: No punctuation found in video-data-master.json")
        print(f"   ✓ All {total_subtitles} subtitles are clean")
        print(f"   ✓ All {total_characters} characters are clean")
    else:
        print(f"\n❌ FAILED: Found {len(punctuation_found)} punctuation issues")
        print("\n📋 Summary of issues:")
        for issue in punctuation_found[:10]:  # 最初の10件のみ表示
            print(f"   - {issue['subtitle_id']} ({issue['location']}): {issue['punctuation']}")
        if len(punctuation_found) > 10:
            print(f"   ... and {len(punctuation_found) - 10} more issues")
    
    return all_passed


def test_sample_video_json():
    """sample-video.json（レガシーフォーマット）のテスト"""
    print("\n" + "=" * 70)
    print("🎯 Testing sample-video.json (Legacy Format)")
    print("=" * 70)
    
    try:
        with open("public/sample-video.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("⚠️  Warning: public/sample-video.json not found (optional)")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format: {e}")
        return False
    
    all_passed = True
    total_subtitles = len(data)
    punctuation_found = []
    
    print(f"\n📊 Total legacy subtitles: {total_subtitles}")
    
    for i, subtitle in enumerate(data):
        text = subtitle.get("text", "")
        
        punct_in_text = detect_punctuation(text, strict=True)
        if punct_in_text:
            all_passed = False
            punctuation_found.append({
                "index": i,
                "text": text,
                "punctuation": punct_in_text
            })
            print(f"❌ [Subtitle {i}] Punctuation found: {punct_in_text}")
            print(f"   Text: {text}")
    
    if all_passed:
        print(f"\n✅ PASSED: No punctuation found in sample-video.json")
        print(f"   ✓ All {total_subtitles} legacy subtitles are clean")
    else:
        print(f"\n❌ FAILED: Found {len(punctuation_found)} punctuation issues")
    
    return all_passed


def test_common_punctuation_patterns():
    """よくある句読点パターンのテスト"""
    print("\n" + "=" * 70)
    print("🎯 Testing Common Punctuation Patterns (Strict Mode)")
    print("=" * 70)
    
    # Strict mode: 、。・のみを検出（！？は除外）
    test_cases = [
        ("成功したいなら、", ["、"]),
        ("応募はLINEから。", ["。"]),
        ("この瞬間。", ["。"]),
        ("まさかの直接審査！？", []),  # Strict modeでは！？は検出しない
        ("BTS・出口氏", ["・"]),
        ("成功したいなら", []),  # 句読点なし
        ("応募はLINEから", []),  # 句読点なし
        ("この瞬間", []),  # 句読点なし
    ]
    
    all_passed = True
    
    for text, expected_punct in test_cases:
        detected = detect_punctuation(text, strict=True)
        
        # 期待される句読点が検出されたかチェック
        if set(detected) == set(expected_punct):
            status = "✅"
        else:
            status = "❌"
            all_passed = False
        
        print(f"{status} '{text}'")
        print(f"   Expected: {expected_punct if expected_punct else 'None'}")
        print(f"   Detected: {detected if detected else 'None'}")
    
    if all_passed:
        print("\n✅ PASSED: All pattern tests passed")
    else:
        print("\n❌ FAILED: Some pattern tests failed")
    
    return all_passed


def main():
    """メインテスト実行"""
    print("\n" + "🎬" * 35)
    print("   句読点完全除去システム - 統合テスト")
    print("🎬" * 35 + "\n")
    
    results = []
    
    # Test 1: video-data-master.json
    results.append(("video-data-master.json", test_video_data_master()))
    
    # Test 2: sample-video.json
    results.append(("sample-video.json", test_sample_video_json()))
    
    # Test 3: Common patterns
    results.append(("Common Patterns", test_common_punctuation_patterns()))
    
    # 最終結果
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("   句読点完全除去システムは正常に動作しています。")
        print("\n次のステップ:")
        print("   1. npm run dev でプレビューを確認")
        print("   2. 画面上に句読点が表示されていないことを目視確認")
        print("   3. npm run build で動画を出力")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("   以下を確認してください:")
        print("   1. python generate_video_data_master.py を再実行")
        print("   2. src/utils/textCleaner.ts の正規表現を確認")
        print("   3. src/AudioDrivenComposition.tsx のインポートを確認")
        return 1


if __name__ == "__main__":
    exit(main())
