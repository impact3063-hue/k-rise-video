# -*- coding: utf-8 -*-
"""
🎯 固有名詞・文脈的表現パーサー v1.0
Proper Noun and Contextual Expression Parser

このモジュールは以下を実現します：
1. 固有名詞（K-RISE、BTS等）を一塊として認識
2. 文脈的表現（「とは」等）を固有名詞と分離
3. 1文字単位のタイムスタンプを維持しつつ、セグメント境界を尊重
4. Whisper APIの出力を正確に解析し、不要な分割を防止
"""

import json
import re
from typing import List, Dict, Any, Tuple, Optional


class ProperNounParser:
    """固有名詞と文脈的表現を適切に処理するパーサー"""
    
    def __init__(self, dictionary_path: str = "proper_nouns_dictionary.json"):
        """
        パーサーの初期化
        
        Args:
            dictionary_path: 固有名詞辞書のパス
        """
        self.dictionary = self._load_dictionary(dictionary_path)
        self.proper_nouns = self._build_proper_noun_list()
        self.contextual_expressions = self._build_contextual_expression_list()
        
    def _load_dictionary(self, path: str) -> Dict[str, Any]:
        """辞書ファイルを読み込む"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Warning: Dictionary file not found: {path}")
            return self._get_default_dictionary()
    
    def _get_default_dictionary(self) -> Dict[str, Any]:
        """デフォルト辞書を返す"""
        return {
            "properNouns": {
                "brands": ["K-RISE", "K-POP", "BTS", "LINE"],
                "organizations": ["アジアモデルフェスティバル"],
                "people": ["出口氏", "出口"],
                "events": ["オーディション"]
            },
            "contextualExpressions": {
                "definitions": ["とは", "というのは", "って何"],
                "particles": ["は", "が", "を", "に", "へ", "と", "から"]
            }
        }
    
    def _build_proper_noun_list(self) -> List[str]:
        """すべての固有名詞をフラットなリストに展開"""
        nouns = []
        proper_nouns_dict = self.dictionary.get("properNouns", {})
        
        for category, items in proper_nouns_dict.items():
            nouns.extend(items)
        
        # 長い順にソート（部分一致を防ぐため）
        return sorted(nouns, key=len, reverse=True)
    
    def _build_contextual_expression_list(self) -> List[str]:
        """すべての文脈的表現をフラットなリストに展開"""
        expressions = []
        contextual_dict = self.dictionary.get("contextualExpressions", {})
        
        for category, items in contextual_dict.items():
            expressions.extend(items)
        
        # 長い順にソート
        return sorted(expressions, key=len, reverse=True)
    
    def identify_proper_nouns_in_text(self, text: str) -> List[Dict[str, Any]]:
        """
        テキスト内の固有名詞を識別し、位置情報を返す
        
        Args:
            text: 解析対象のテキスト
        
        Returns:
            固有名詞の位置情報リスト [{"noun": "K-RISE", "start": 0, "end": 6}, ...]
        """
        found_nouns = []
        
        for noun in self.proper_nouns:
            # テキスト内のすべての出現位置を検索
            start = 0
            while True:
                pos = text.find(noun, start)
                if pos == -1:
                    break
                
                found_nouns.append({
                    "noun": noun,
                    "start": pos,
                    "end": pos + len(noun),
                    "type": "proper_noun"
                })
                start = pos + 1
        
        # 開始位置でソート
        found_nouns.sort(key=lambda x: x["start"])
        
        # 重複を除去（長い方を優先）
        filtered_nouns = []
        for noun in found_nouns:
            # 既存の固有名詞と重複していないかチェック
            is_overlap = False
            for existing in filtered_nouns:
                if (noun["start"] >= existing["start"] and noun["start"] < existing["end"]) or \
                   (noun["end"] > existing["start"] and noun["end"] <= existing["end"]):
                    is_overlap = True
                    break
            
            if not is_overlap:
                filtered_nouns.append(noun)
        
        return filtered_nouns
    
    def identify_contextual_expressions(self, text: str, proper_noun_positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        テキスト内の文脈的表現を識別（固有名詞の位置を考慮）
        
        Args:
            text: 解析対象のテキスト
            proper_noun_positions: 固有名詞の位置情報
        
        Returns:
            文脈的表現の位置情報リスト
        """
        found_expressions = []
        
        for expr in self.contextual_expressions:
            start = 0
            while True:
                pos = text.find(expr, start)
                if pos == -1:
                    break
                
                # 固有名詞の内部でないことを確認
                is_inside_noun = False
                for noun_pos in proper_noun_positions:
                    if pos >= noun_pos["start"] and pos < noun_pos["end"]:
                        is_inside_noun = True
                        break
                
                if not is_inside_noun:
                    found_expressions.append({
                        "expression": expr,
                        "start": pos,
                        "end": pos + len(expr),
                        "type": "contextual_expression"
                    })
                
                start = pos + 1
        
        # 開始位置でソート
        found_expressions.sort(key=lambda x: x["start"])
        
        return found_expressions
    
    def parse_text_with_boundaries(self, text: str) -> List[Dict[str, Any]]:
        """
        テキストを固有名詞と文脈的表現の境界を考慮して解析
        
        Args:
            text: 解析対象のテキスト
        
        Returns:
            境界情報を含むトークンリスト
            [
                {"text": "K-RISE", "start": 0, "end": 6, "type": "proper_noun"},
                {"text": "とは", "start": 6, "end": 8, "type": "contextual_expression"},
                ...
            ]
        """
        # Step 1: 固有名詞を識別
        proper_nouns = self.identify_proper_nouns_in_text(text)
        
        # Step 2: 文脈的表現を識別
        contextual_exprs = self.identify_contextual_expressions(text, proper_nouns)
        
        # Step 3: すべての特殊トークンをマージ
        all_tokens = proper_nouns + contextual_exprs
        all_tokens.sort(key=lambda x: x["start"])
        
        # Step 4: 特殊トークン間の通常テキストを追加
        result = []
        current_pos = 0
        
        for token in all_tokens:
            # 前のトークンとの間に通常テキストがあれば追加
            if current_pos < token["start"]:
                normal_text = text[current_pos:token["start"]]
                if normal_text.strip():  # 空白のみでない場合
                    result.append({
                        "text": normal_text,
                        "start": current_pos,
                        "end": token["start"],
                        "type": "normal"
                    })
            
            # 特殊トークンを追加
            result.append({
                "text": token.get("noun") or token.get("expression"),
                "start": token["start"],
                "end": token["end"],
                "type": token["type"]
            })
            
            current_pos = token["end"]
        
        # 最後の残りテキストを追加
        if current_pos < len(text):
            remaining_text = text[current_pos:]
            if remaining_text.strip():
                result.append({
                    "text": remaining_text,
                    "start": current_pos,
                    "end": len(text),
                    "type": "normal"
                })
        
        return result
    
    def annotate_character_data(
        self, 
        character_data: List[Dict[str, Any]], 
        text: str
    ) -> List[Dict[str, Any]]:
        """
        1文字単位のデータに固有名詞・文脈的表現の情報を付与
        
        Args:
            character_data: 1文字単位のタイムスタンプデータ
            text: 元のテキスト
        
        Returns:
            アノテーション付きの文字データ
        """
        # テキストを解析
        tokens = self.parse_text_with_boundaries(text)
        
        # 各文字にトークン情報を付与
        annotated_data = []
        char_index = 0
        
        for char_data in character_data:
            char = char_data["char"]
            
            # この文字がどのトークンに属するか判定
            token_info = None
            for token in tokens:
                if char_index >= token["start"] and char_index < token["end"]:
                    token_info = token
                    break
            
            # アノテーション情報を追加
            annotated_char = char_data.copy()
            if token_info:
                annotated_char["tokenType"] = token_info["type"]
                annotated_char["tokenText"] = token_info["text"]
                annotated_char["tokenStart"] = token_info["start"]
                annotated_char["tokenEnd"] = token_info["end"]
                annotated_char["isProperNoun"] = token_info["type"] == "proper_noun"
                annotated_char["isContextualExpression"] = token_info["type"] == "contextual_expression"
            else:
                annotated_char["tokenType"] = "normal"
                annotated_char["isProperNoun"] = False
                annotated_char["isContextualExpression"] = False
            
            annotated_data.append(annotated_char)
            char_index += len(char)
        
        return annotated_data
    
    def get_segmentation_boundaries(
        self, 
        text: str, 
        respect_proper_nouns: bool = True
    ) -> List[int]:
        """
        固有名詞を尊重したセグメント境界を取得
        
        Args:
            text: 解析対象のテキスト
            respect_proper_nouns: 固有名詞の内部で分割しない場合True
        
        Returns:
            セグメント境界のインデックスリスト
        """
        boundaries = []
        
        if not respect_proper_nouns:
            # 通常の境界検出（句読点のみ）
            for i, char in enumerate(text):
                if char in ["、", "。", "！", "？", "!", "?"]:
                    boundaries.append(i + 1)
            return boundaries
        
        # 固有名詞を識別
        proper_nouns = self.identify_proper_nouns_in_text(text)
        
        # 固有名詞の境界を追加（固有名詞の直後は分割可能）
        for noun in proper_nouns:
            boundaries.append(noun["end"])
        
        # 句読点の境界を追加（固有名詞の内部でない場合のみ）
        for i, char in enumerate(text):
            if char in ["、", "。", "！", "？", "!", "?"]:
                # 固有名詞の内部でないことを確認
                is_inside_noun = False
                for noun in proper_nouns:
                    if i >= noun["start"] and i < noun["end"]:
                        is_inside_noun = True
                        break
                
                if not is_inside_noun:
                    boundaries.append(i + 1)
        
        # 重複を削除してソート
        boundaries = sorted(list(set(boundaries)))
        
        return boundaries


def test_parser():
    """パーサーのテスト"""
    parser = ProperNounParser()
    
    # テストケース
    test_cases = [
        "K-RISEとは、アジアモデルフェスティバルです。",
        "BTSを日本に導いた出口氏が審査します。",
        "K-POPオーディションに応募はLINEから！",
        "アジアモデルフェスティバルとは何か？"
    ]
    
    print("=" * 60)
    print("🎯 固有名詞・文脈的表現パーサー テスト")
    print("=" * 60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 テストケース {i}: {text}")
        print("-" * 60)
        
        # 固有名詞を識別
        proper_nouns = parser.identify_proper_nouns_in_text(text)
        print(f"✅ 固有名詞 ({len(proper_nouns)}個):")
        for noun in proper_nouns:
            print(f"   - '{noun['noun']}' @ {noun['start']}-{noun['end']}")
        
        # 文脈的表現を識別
        contextual = parser.identify_contextual_expressions(text, proper_nouns)
        print(f"✅ 文脈的表現 ({len(contextual)}個):")
        for expr in contextual:
            print(f"   - '{expr['expression']}' @ {expr['start']}-{expr['end']}")
        
        # 境界を解析
        tokens = parser.parse_text_with_boundaries(text)
        print(f"✅ トークン分割 ({len(tokens)}個):")
        for token in tokens:
            print(f"   - [{token['type']:20s}] '{token['text']}'")
        
        # セグメント境界
        boundaries = parser.get_segmentation_boundaries(text)
        print(f"✅ セグメント境界: {boundaries}")
    
    print("\n" + "=" * 60)
    print("✨ テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    test_parser()
