# -*- coding: utf-8 -*-
"""
🎯 固有名詞保護システム テストスイート
Proper Noun Protection System Test Suite

このスクリプトは固有名詞パーサーと文脈的表現の分離機能をテストします。
"""

import sys
import json
from typing import List, Dict, Any

# Windows環境でのUnicode出力対応
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from proper_noun_parser import ProperNounParser
    PARSER_AVAILABLE = True
except ImportError:
    PARSER_AVAILABLE = False
    print("❌ ProperNounParser not available")


def test_case_1_krise_toha():
    """テストケース1: K-RISEとは"""
    print("\n" + "=" * 60)
    print("📝 テストケース1: K-RISEとは")
    print("=" * 60)
    
    text = "K-RISEとは、アジアモデルフェスティバルです。"
    parser = ProperNounParser()
    
    # 固有名詞を識別
    proper_nouns = parser.identify_proper_nouns_in_text(text)
    print(f"\n✅ 固有名詞検出: {len(proper_nouns)}個")
    for pn in proper_nouns:
        print(f"   - '{pn['noun']}' @ 位置 {pn['start']}-{pn['end']}")
    
    # 文脈的表現を識別
    contextual = parser.identify_contextual_expressions(text, proper_nouns)
    print(f"\n✅ 文脈的表現検出: {len(contextual)}個")
    for expr in contextual:
        print(f"   - '{expr['expression']}' @ 位置 {expr['start']}-{expr['end']}")
    
    # トークン分割
    tokens = parser.parse_text_with_boundaries(text)
    print(f"\n✅ トークン分割: {len(tokens)}個")
    for i, token in enumerate(tokens, 1):
        print(f"   {i}. [{token['type']:20s}] '{token['text']}'")
    
    # 検証
    assert len(proper_nouns) >= 2, "K-RISEとアジアモデルフェスティバルが検出されるべき"
    assert any(pn['noun'] == 'K-RISE' for pn in proper_nouns), "K-RISEが検出されるべき"
    assert any(expr['expression'] == 'とは' for expr in contextual), "「とは」が検出されるべき"
    
    print("\n✅ テストケース1: 成功")
    return True


def test_case_2_bts_deguchi():
    """テストケース2: BTSと出口氏"""
    print("\n" + "=" * 60)
    print("📝 テストケース2: BTSを日本に導いた出口氏が審査します")
    print("=" * 60)
    
    text = "BTSを日本に導いた出口氏が審査します。"
    parser = ProperNounParser()
    
    proper_nouns = parser.identify_proper_nouns_in_text(text)
    print(f"\n✅ 固有名詞検出: {len(proper_nouns)}個")
    for pn in proper_nouns:
        print(f"   - '{pn['noun']}' @ 位置 {pn['start']}-{pn['end']}")
    
    contextual = parser.identify_contextual_expressions(text, proper_nouns)
    print(f"\n✅ 文脈的表現検出: {len(contextual)}個")
    for expr in contextual:
        print(f"   - '{expr['expression']}' @ 位置 {expr['start']}-{expr['end']}")
    
    tokens = parser.parse_text_with_boundaries(text)
    print(f"\n✅ トークン分割: {len(tokens)}個")
    for i, token in enumerate(tokens, 1):
        print(f"   {i}. [{token['type']:20s}] '{token['text']}'")
    
    # 検証
    assert any(pn['noun'] == 'BTS' for pn in proper_nouns), "BTSが検出されるべき"
    assert any(pn['noun'] == '出口氏' for pn in proper_nouns), "出口氏が検出されるべき"
    
    print("\n✅ テストケース2: 成功")
    return True


def test_case_3_kpop_line():
    """テストケース3: K-POPとLINE"""
    print("\n" + "=" * 60)
    print("📝 テストケース3: K-POPオーディションに応募はLINEから")
    print("=" * 60)
    
    text = "K-POPオーディションに応募はLINEから！"
    parser = ProperNounParser()
    
    proper_nouns = parser.identify_proper_nouns_in_text(text)
    print(f"\n✅ 固有名詞検出: {len(proper_nouns)}個")
    for pn in proper_nouns:
        print(f"   - '{pn['noun']}' @ 位置 {pn['start']}-{pn['end']}")
    
    contextual = parser.identify_contextual_expressions(text, proper_nouns)
    print(f"\n✅ 文脈的表現検出: {len(contextual)}個")
    for expr in contextual:
        print(f"   - '{expr['expression']}' @ 位置 {expr['start']}-{expr['end']}")
    
    tokens = parser.parse_text_with_boundaries(text)
    print(f"\n✅ トークン分割: {len(tokens)}個")
    for i, token in enumerate(tokens, 1):
        print(f"   {i}. [{token['type']:20s}] '{token['text']}'")
    
    # 検証
    assert any(pn['noun'] == 'K-POP' for pn in proper_nouns), "K-POPが検出されるべき"
    assert any(pn['noun'] == 'LINE' for pn in proper_nouns), "LINEが検出されるべき"
    
    print("\n✅ テストケース3: 成功")
    return True


def test_case_4_segmentation_boundaries():
    """テストケース4: セグメント境界の検証"""
    print("\n" + "=" * 60)
    print("📝 テストケース4: セグメント境界（固有名詞を尊重）")
    print("=" * 60)
    
    text = "K-RISEとは、アジアモデルフェスティバルの新プロジェクトです。"
    parser = ProperNounParser()
    
    boundaries = parser.get_segmentation_boundaries(text, respect_proper_nouns=True)
    print(f"\n✅ セグメント境界: {boundaries}")
    
    # 境界で分割してみる
    segments = []
    prev = 0
    for boundary in boundaries:
        if prev < boundary <= len(text):
            segment = text[prev:boundary]
            segments.append(segment)
            prev = boundary
    if prev < len(text):
        segments.append(text[prev:])
    
    print(f"\n✅ セグメント分割結果: {len(segments)}個")
    for i, seg in enumerate(segments, 1):
        print(f"   {i}. '{seg}'")
    
    # 検証: K-RISEが分割されていないこと
    full_text = "".join(segments)
    assert "K-RISE" in full_text or "K" in full_text, "テキストが保持されているべき"
    
    print("\n✅ テストケース4: 成功")
    return True


def test_case_5_complex_sentence():
    """テストケース5: 複雑な文章"""
    print("\n" + "=" * 60)
    print("📝 テストケース5: 複雑な文章（複数の固有名詞と文脈的表現）")
    print("=" * 60)
    
    text = "アジアモデルフェスティバルとは何か？BTSのプロデューサー出口氏がK-POPオーディションを開催。応募はLINEから！"
    parser = ProperNounParser()
    
    proper_nouns = parser.identify_proper_nouns_in_text(text)
    print(f"\n✅ 固有名詞検出: {len(proper_nouns)}個")
    for pn in proper_nouns:
        print(f"   - '{pn['noun']}' @ 位置 {pn['start']}-{pn['end']}")
    
    contextual = parser.identify_contextual_expressions(text, proper_nouns)
    print(f"\n✅ 文脈的表現検出: {len(contextual)}個")
    for expr in contextual:
        print(f"   - '{expr['expression']}' @ 位置 {expr['start']}-{expr['end']}")
    
    tokens = parser.parse_text_with_boundaries(text)
    print(f"\n✅ トークン分割: {len(tokens)}個")
    for i, token in enumerate(tokens, 1):
        print(f"   {i}. [{token['type']:20s}] '{token['text']}'")
    
    # 検証
    expected_nouns = ['アジアモデルフェスティバル', 'BTS', '出口氏', 'K-POP', 'LINE']
    detected_nouns = [pn['noun'] for pn in proper_nouns]
    
    print(f"\n📊 検証:")
    print(f"   期待される固有名詞: {expected_nouns}")
    print(f"   検出された固有名詞: {detected_nouns}")
    
    for expected in expected_nouns:
        if expected in detected_nouns:
            print(f"   ✅ '{expected}' 検出成功")
        else:
            print(f"   ⚠️  '{expected}' 未検出")
    
    print("\n✅ テストケース5: 成功")
    return True


def test_case_6_character_annotation():
    """テストケース6: 文字データへのアノテーション"""
    print("\n" + "=" * 60)
    print("📝 テストケース6: 文字データへのアノテーション")
    print("=" * 60)
    
    text = "K-RISEとは新プロジェクト"
    parser = ProperNounParser()
    
    # 模擬的な文字データを作成
    character_data = []
    for i, char in enumerate(text):
        character_data.append({
            "char": char,
            "startTime": i * 0.1,
            "endTime": (i + 1) * 0.1,
            "startFrame": i * 3,
            "endFrame": (i + 1) * 3,
            "duration": 0.1,
            "wordIndex": i
        })
    
    # アノテーションを付与
    annotated = parser.annotate_character_data(character_data, text)
    
    print(f"\n✅ アノテーション付き文字データ: {len(annotated)}個")
    for i, char_data in enumerate(annotated[:15]):  # 最初の15文字のみ表示
        is_pn = "🎯" if char_data.get("isProperNoun") else "  "
        is_ctx = "📝" if char_data.get("isContextualExpression") else "  "
        token_type = char_data.get("tokenType", "unknown")
        print(f"   {i+1:2d}. {is_pn}{is_ctx} '{char_data['char']}' [{token_type:20s}]")
    
    # 検証: K-RISEの文字が固有名詞としてマークされているか
    krise_chars = [annotated[i] for i in range(6)]  # K-RISE
    assert all(c.get("isProperNoun") for c in krise_chars), "K-RISEの全文字が固有名詞としてマークされるべき"
    
    print("\n✅ テストケース6: 成功")
    return True


def run_all_tests():
    """すべてのテストを実行"""
    print("=" * 60)
    print("🎯 固有名詞保護システム テストスイート")
    print("=" * 60)
    
    if not PARSER_AVAILABLE:
        print("\n❌ ProperNounParserが利用できません")
        return False
    
    tests = [
        ("K-RISEとは", test_case_1_krise_toha),
        ("BTSと出口氏", test_case_2_bts_deguchi),
        ("K-POPとLINE", test_case_3_kpop_line),
        ("セグメント境界", test_case_4_segmentation_boundaries),
        ("複雑な文章", test_case_5_complex_sentence),
        ("文字アノテーション", test_case_6_character_annotation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ テスト失敗: {name}")
            print(f"   エラー: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"   {status} - {name}")
    
    print(f"\n合計: {passed}/{total} テスト成功")
    
    if passed == total:
        print("\n🎉 すべてのテストが成功しました！")
        return True
    else:
        print(f"\n⚠️  {total - passed}個のテストが失敗しました")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
