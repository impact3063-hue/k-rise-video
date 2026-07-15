# 字幕編集クイックリファレンス

## 🚀 クイックスタート

### 1. 対話モードで編集

```bash
python manual_subtitle_editor.py --interactive
```

### 2. よく使うコマンド

| コマンド | 説明 | 例 |
|---------|------|-----|
| `list` | 字幕リスト表示 | `list 0 10` |
| `search <テキスト>` | テキスト検索 | `search まさか` |
| `split <番号> <位置>` | 字幕分割 | `split 1 11` |
| `merge <開始> <終了>` | 字幕結合 | `merge 1 2` |
| `time <番号> <開始> <終了>` | タイミング調整 | `time 2 5.52 8.06` |
| `edit <番号> <テキスト>` | テキスト編集 | `edit 2 まさかの直接審査！？` |
| `word <単語>` | カスタム単語追加 | `word まさかの` |
| `save` | 保存 | `save` |
| `quit` | 終了 | `quit` |

---

## 📝 今回の修正手順

### 問題: 「まさか」が「まさ/さ」に分断

```
修正前:
  字幕1: プロデューサー出口氏がまさ
  字幕2: さかの直接審査

修正後:
  字幕1: プロデューサー出口氏が
  字幕2: まさかの直接審査！？
```

### 手順

```bash
# 1. 対話モード起動
python manual_subtitle_editor.py --interactive

# 2. 字幕確認
> list 0 5

# 3. 字幕1を分割（11文字目で）
> split 1 11

# 4. 新しい字幕2と3を結合
> merge 2 3

# 5. タイミング調整
> time 2 5.52 8.06

# 6. テキスト編集（記号追加）
> edit 2 まさかの直接審査！？

# 7. 保存
> save

# 8. 終了
> quit
```

---

## 🐍 Pythonスクリプトで編集

```python
from manual_subtitle_editor import SubtitleEditor

# 初期化
editor = SubtitleEditor('public/video-data-master.json')

# カスタム辞書読み込み
editor.load_custom_dictionary('custom_words_dictionary.txt')

# 検索
results = editor.find_subtitle_by_text('まさか')

# 分割
editor.split_subtitle(1, 11)

# 結合
editor.merge_subtitles(2, 3)

# タイミング調整
editor.adjust_timing(2, new_start_time=5.52, new_end_time=8.06)

# テキスト編集
editor.edit_text(2, 'まさかの直接審査！？')

# 保存
editor.save()
```

---

## 📚 カスタム単語辞書

### ファイル: `custom_words_dictionary.txt`

```txt
# 優先的に結合する単語を1行に1つ記述
まさか
まさかの
プロデューサー
直接審査
K-POP
```

### 使い方

```python
editor = SubtitleEditor('public/video-data-master.json')
editor.load_custom_dictionary('custom_words_dictionary.txt')
```

---

## ⚠️ 注意事項

### ✅ 必ずやること

- バックアップ作成（自動で作成されます）
- 編集後に動画で確認
- JSON構文の維持

### ❌ やってはいけないこと

- `wordIndex` の変更
- 時間の逆転（`startTime > endTime`）
- フレーム番号の手動変更（自動計算に任せる）

---

## 🔧 トラブルシューティング

### JSON構文エラー

```bash
# 構文チェック
python -m json.tool public/video-data-master.json

# バックアップから復元
cp public/video-data-master.json.backup public/video-data-master.json
```

### 音声とズレる

```python
# タイミング再調整
editor.adjust_timing(subtitle_index, correct_start, correct_end)
editor.save()
```

---

## 📖 詳細ドキュメント

完全なガイドは [`MANUAL_SUBTITLE_EDITING_GUIDE.md`](MANUAL_SUBTITLE_EDITING_GUIDE.md) を参照してください。

---

## 🎯 修正完了チェックリスト

- [ ] バックアップ作成済み
- [ ] 字幕の分割・結合完了
- [ ] タイミング調整完了
- [ ] テキスト編集完了
- [ ] 保存完了
- [ ] 動画で確認済み
- [ ] 音声との同期確認済み
- [ ] カスタム辞書に単語追加済み

---

**完成！** 🎉
