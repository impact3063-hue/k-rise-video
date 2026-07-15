#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手動字幕編集ツール (Manual Subtitle Editor)
===========================================

このスクリプトは、生成されたJSONデータを人間が直接編集できるようにし、
日本語の単語が不自然に分割されるのを防ぐための機能を提供します。

機能:
1. カスタム単語辞書による単語結合の優先制御
2. 字幕セグメントの手動分割・結合
3. タイムスタンプの微調整
4. フレーム同期の自動維持
"""

import json
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path


class SubtitleEditor:
    """字幕編集クラス"""
    
    def __init__(self, json_path: str, fps: int = 30):
        """
        初期化
        
        Args:
            json_path: video-data-master.jsonのパス
            fps: フレームレート (デフォルト: 30)
        """
        self.json_path = Path(json_path)
        self.fps = fps
        self.data = self._load_json()
        
        # カスタム単語辞書 (優先的に結合すべき単語)
        self.custom_words = set([
            "まさか", "まさかの", "プロデューサー", "直接審査",
            "K-POP", "チャンス", "応募", "プロフィール",
            "リンク", "チェック"
        ])
    
    def _load_json(self) -> Dict[str, Any]:
        """JSONファイルを読み込む"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_json(self, backup: bool = True):
        """JSONファイルを保存する"""
        if backup:
            backup_path = self.json_path.with_suffix('.json.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✓ バックアップ作成: {backup_path}")
        
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✓ 保存完了: {self.json_path}")
    
    def _time_to_frame(self, time: float) -> int:
        """時間をフレーム番号に変換"""
        return int(time * self.fps)
    
    def _frame_to_time(self, frame: int) -> float:
        """フレーム番号を時間に変換"""
        return round(frame / self.fps, 2)
    
    def add_custom_word(self, word: str):
        """カスタム単語辞書に単語を追加"""
        self.custom_words.add(word)
        print(f"✓ カスタム単語追加: {word}")
    
    def load_custom_dictionary(self, dict_path: str):
        """カスタム辞書ファイルを読み込む"""
        dict_file = Path(dict_path)
        if dict_file.exists():
            with open(dict_file, 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]
                self.custom_words.update(words)
            print(f"✓ カスタム辞書読み込み: {len(words)}語")
        else:
            print(f"⚠ 辞書ファイルが見つかりません: {dict_path}")
    
    def find_subtitle_by_text(self, search_text: str) -> List[Dict[str, Any]]:
        """テキストで字幕を検索"""
        results = []
        for i, sub in enumerate(self.data['subtitles']):
            if search_text in sub['text']:
                results.append({
                    'index': i,
                    'id': sub['id'],
                    'text': sub['text'],
                    'startTime': sub['startTime'],
                    'endTime': sub['endTime']
                })
        return results
    
    def split_subtitle(self, subtitle_index: int, split_char_index: int) -> bool:
        """
        字幕を指定位置で分割
        
        Args:
            subtitle_index: 字幕のインデックス
            split_char_index: 分割する文字位置 (この位置から新しい字幕になる)
        
        Returns:
            成功したかどうか
        """
        if subtitle_index >= len(self.data['subtitles']):
            print(f"✗ エラー: インデックス {subtitle_index} は範囲外です")
            return False
        
        sub = self.data['subtitles'][subtitle_index]
        
        if split_char_index >= len(sub['characters']):
            print(f"✗ エラー: 文字位置 {split_char_index} は範囲外です")
            return False
        
        # 前半部分
        first_chars = sub['characters'][:split_char_index]
        first_text = ''.join([c['char'] for c in first_chars])
        first_end_time = first_chars[-1]['endTime']
        first_end_frame = first_chars[-1]['endFrame']
        
        # 後半部分
        second_chars = sub['characters'][split_char_index:]
        second_text = ''.join([c['char'] for c in second_chars])
        second_start_time = second_chars[0]['startTime']
        second_start_frame = second_chars[0]['startFrame']
        
        # 新しい字幕ID
        new_id = f"{sub['id']}_split"
        
        # 前半を更新
        sub['text'] = first_text
        sub['endTime'] = first_end_time
        sub['endFrame'] = first_end_frame
        sub['duration'] = first_end_time - sub['startTime']
        sub['characterCount'] = len(first_chars)
        sub['characters'] = first_chars
        sub['metadata']['manuallyEdited'] = True
        
        # 後半を作成
        new_sub = {
            'id': new_id,
            'text': second_text,
            'startTime': second_start_time,
            'endTime': sub['endTime'],
            'startFrame': second_start_frame,
            'endFrame': sub['endFrame'],
            'duration': sub['endTime'] - second_start_time,
            'characterCount': len(second_chars),
            'characters': second_chars,
            'style': sub['style'].copy(),
            'metadata': {
                **sub['metadata'],
                'manuallyEdited': True,
                'splitFrom': sub['id']
            }
        }
        
        # 挿入
        self.data['subtitles'].insert(subtitle_index + 1, new_sub)
        
        print(f"✓ 字幕分割完了:")
        print(f"  前半: {first_text}")
        print(f"  後半: {second_text}")
        
        return True
    
    def merge_subtitles(self, start_index: int, end_index: int) -> bool:
        """
        複数の字幕を結合
        
        Args:
            start_index: 開始インデックス
            end_index: 終了インデックス (含む)
        
        Returns:
            成功したかどうか
        """
        if start_index >= end_index:
            print(f"✗ エラー: 開始インデックスは終了インデックスより小さい必要があります")
            return False
        
        if end_index >= len(self.data['subtitles']):
            print(f"✗ エラー: インデックス範囲が不正です")
            return False
        
        # 結合する字幕を取得
        subs_to_merge = self.data['subtitles'][start_index:end_index + 1]
        
        # 結合後のデータを作成
        merged_text = ''.join([s['text'] for s in subs_to_merge])
        merged_chars = []
        for sub in subs_to_merge:
            merged_chars.extend(sub['characters'])
        
        first_sub = subs_to_merge[0]
        last_sub = subs_to_merge[-1]
        
        merged_sub = {
            'id': f"{first_sub['id']}_merged",
            'text': merged_text,
            'startTime': first_sub['startTime'],
            'endTime': last_sub['endTime'],
            'startFrame': first_sub['startFrame'],
            'endFrame': last_sub['endFrame'],
            'duration': last_sub['endTime'] - first_sub['startTime'],
            'characterCount': len(merged_chars),
            'characters': merged_chars,
            'style': first_sub['style'].copy(),
            'metadata': {
                **first_sub['metadata'],
                'manuallyEdited': True,
                'mergedFrom': [s['id'] for s in subs_to_merge]
            }
        }
        
        # 古い字幕を削除して新しい字幕を挿入
        del self.data['subtitles'][start_index:end_index + 1]
        self.data['subtitles'].insert(start_index, merged_sub)
        
        print(f"✓ 字幕結合完了: {merged_text}")
        
        return True
    
    def adjust_timing(self, subtitle_index: int, 
                     new_start_time: float = None, 
                     new_end_time: float = None) -> bool:
        """
        字幕のタイミングを調整
        
        Args:
            subtitle_index: 字幕のインデックス
            new_start_time: 新しい開始時間 (Noneの場合は変更なし)
            new_end_time: 新しい終了時間 (Noneの場合は変更なし)
        
        Returns:
            成功したかどうか
        """
        if subtitle_index >= len(self.data['subtitles']):
            print(f"✗ エラー: インデックス {subtitle_index} は範囲外です")
            return False
        
        sub = self.data['subtitles'][subtitle_index]
        
        if new_start_time is not None:
            sub['startTime'] = new_start_time
            sub['startFrame'] = self._time_to_frame(new_start_time)
            # 最初の文字のタイミングも調整
            if sub['characters']:
                sub['characters'][0]['startTime'] = new_start_time
                sub['characters'][0]['startFrame'] = self._time_to_frame(new_start_time)
        
        if new_end_time is not None:
            sub['endTime'] = new_end_time
            sub['endFrame'] = self._time_to_frame(new_end_time)
            # 最後の文字のタイミングも調整
            if sub['characters']:
                sub['characters'][-1]['endTime'] = new_end_time
                sub['characters'][-1]['endFrame'] = self._time_to_frame(new_end_time)
        
        # durationを再計算
        sub['duration'] = sub['endTime'] - sub['startTime']
        sub['metadata']['manuallyEdited'] = True
        
        print(f"✓ タイミング調整完了: {sub['text']}")
        print(f"  開始: {sub['startTime']}s (フレーム {sub['startFrame']})")
        print(f"  終了: {sub['endTime']}s (フレーム {sub['endFrame']})")
        
        return True
    
    def edit_text(self, subtitle_index: int, new_text: str, 
                  preserve_timing: bool = True) -> bool:
        """
        字幕テキストを編集
        
        Args:
            subtitle_index: 字幕のインデックス
            new_text: 新しいテキスト
            preserve_timing: タイミングを保持するか
        
        Returns:
            成功したかどうか
        """
        if subtitle_index >= len(self.data['subtitles']):
            print(f"✗ エラー: インデックス {subtitle_index} は範囲外です")
            return False
        
        sub = self.data['subtitles'][subtitle_index]
        old_text = sub['text']
        
        sub['text'] = new_text
        sub['characterCount'] = len(new_text)
        
        if preserve_timing and sub['characters']:
            # タイミングを保持しながら文字配列を再構築
            total_duration = sub['duration']
            char_duration = total_duration / len(new_text) if len(new_text) > 0 else 0
            
            new_chars = []
            for i, char in enumerate(new_text):
                char_start = sub['startTime'] + (i * char_duration)
                char_end = char_start + char_duration
                
                new_chars.append({
                    'char': char,
                    'startTime': round(char_start, 2),
                    'endTime': round(char_end, 2),
                    'startFrame': self._time_to_frame(char_start),
                    'endFrame': self._time_to_frame(char_end),
                    'duration': round(char_duration, 2),
                    'wordIndex': sub['characters'][0]['wordIndex'] + i if sub['characters'] else i
                })
            
            sub['characters'] = new_chars
        
        sub['metadata']['manuallyEdited'] = True
        sub['metadata']['originalText'] = old_text
        
        print(f"✓ テキスト編集完了:")
        print(f"  変更前: {old_text}")
        print(f"  変更後: {new_text}")
        
        return True
    
    def list_subtitles(self, start_index: int = 0, count: int = 10):
        """字幕リストを表示"""
        print("\n" + "="*80)
        print("字幕リスト")
        print("="*80)
        
        end_index = min(start_index + count, len(self.data['subtitles']))
        
        for i in range(start_index, end_index):
            sub = self.data['subtitles'][i]
            edited = "✎" if sub['metadata'].get('manuallyEdited') else " "
            print(f"\n[{i}] {edited} {sub['id']}")
            print(f"    テキスト: {sub['text']}")
            print(f"    時間: {sub['startTime']:.2f}s - {sub['endTime']:.2f}s")
            print(f"    フレーム: {sub['startFrame']} - {sub['endFrame']}")
            print(f"    文字数: {sub['characterCount']}")
        
        print(f"\n表示: {start_index}-{end_index-1} / 全{len(self.data['subtitles'])}件")
        print("="*80 + "\n")
    
    def save(self, backup: bool = True):
        """変更を保存"""
        self._save_json(backup=backup)


def interactive_mode():
    """対話モード"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║          手動字幕編集ツール - Manual Subtitle Editor          ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    json_path = input("JSONファイルのパス [public/video-data-master.json]: ").strip()
    if not json_path:
        json_path = "public/video-data-master.json"
    
    editor = SubtitleEditor(json_path)
    
    print("\n✓ JSONファイル読み込み完了")
    print(f"  字幕数: {len(editor.data['subtitles'])}")
    print(f"  FPS: {editor.fps}")
    
    while True:
        print("\n" + "─"*60)
        print("コマンド:")
        print("  list [開始] [件数]  - 字幕リストを表示")
        print("  search <テキスト>   - テキストで検索")
        print("  split <番号> <位置> - 字幕を分割")
        print("  merge <開始> <終了> - 字幕を結合")
        print("  time <番号> <開始> <終了> - タイミング調整")
        print("  edit <番号> <テキスト> - テキスト編集")
        print("  word <単語>         - カスタム単語追加")
        print("  save                - 保存")
        print("  quit                - 終了")
        print("─"*60)
        
        cmd = input("\n> ").strip()
        
        if not cmd:
            continue
        
        parts = cmd.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        try:
            if command == "list":
                args_list = args.split() if args else []
                start = int(args_list[0]) if len(args_list) > 0 else 0
                count = int(args_list[1]) if len(args_list) > 1 else 10
                editor.list_subtitles(start, count)
            
            elif command == "search":
                results = editor.find_subtitle_by_text(args)
                print(f"\n検索結果: {len(results)}件")
                for r in results:
                    print(f"  [{r['index']}] {r['text']} ({r['startTime']:.2f}s)")
            
            elif command == "split":
                args_list = args.split()
                if len(args_list) >= 2:
                    editor.split_subtitle(int(args_list[0]), int(args_list[1]))
                else:
                    print("✗ 使用法: split <字幕番号> <分割位置>")
            
            elif command == "merge":
                args_list = args.split()
                if len(args_list) >= 2:
                    editor.merge_subtitles(int(args_list[0]), int(args_list[1]))
                else:
                    print("✗ 使用法: merge <開始番号> <終了番号>")
            
            elif command == "time":
                args_list = args.split()
                if len(args_list) >= 3:
                    editor.adjust_timing(
                        int(args_list[0]),
                        float(args_list[1]),
                        float(args_list[2])
                    )
                else:
                    print("✗ 使用法: time <字幕番号> <開始時間> <終了時間>")
            
            elif command == "edit":
                args_list = args.split(maxsplit=1)
                if len(args_list) >= 2:
                    editor.edit_text(int(args_list[0]), args_list[1])
                else:
                    print("✗ 使用法: edit <字幕番号> <新しいテキスト>")
            
            elif command == "word":
                editor.add_custom_word(args)
            
            elif command == "save":
                editor.save()
            
            elif command in ["quit", "exit", "q"]:
                confirm = input("保存せずに終了しますか？ (y/N): ")
                if confirm.lower() == 'y':
                    break
                else:
                    print("終了をキャンセルしました")
            
            else:
                print(f"✗ 不明なコマンド: {command}")
        
        except Exception as e:
            print(f"✗ エラー: {e}")
    
    print("\n終了しました")


if __name__ == "__main__":
    # 使用例
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        # プログラム的な使用例
        print("使用例:")
        print("  python manual_subtitle_editor.py --interactive")
        print("\nまたは:")
        print("""
from manual_subtitle_editor import SubtitleEditor

# エディタを初期化
editor = SubtitleEditor('public/video-data-master.json')

# 字幕を検索
results = editor.find_subtitle_by_text('まさか')

# 字幕を結合 (例: インデックス1と2を結合)
editor.merge_subtitles(1, 2)

# タイミングを調整
editor.adjust_timing(1, new_start_time=5.5, new_end_time=8.0)

# テキストを編集
editor.edit_text(1, 'まさかの直接審査！？')

# 保存
editor.save()
        """)
