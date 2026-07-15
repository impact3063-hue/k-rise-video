# 手動字幕編集ガイド (Manual Subtitle Editing Guide)

## 📋 目次

1. [概要](#概要)
2. [問題の背景](#問題の背景)
3. [解決方法](#解決方法)
4. [手動編集ツールの使い方](#手動編集ツールの使い方)
5. [カスタム単語辞書](#カスタム単語辞書)
6. [実践例](#実践例)
7. [トラブルシューティング](#トラブルシューティング)

---

## 概要

このガイドでは、自動生成された字幕データに不自然な単語の区切りが発生した場合に、人間が手動で修正する方法を説明します。

### 主な機能

✅ **字幕セグメントの分割・結合** - 不自然な区切りを修正  
✅ **タイムスタンプの微調整** - 表示タイミングを最適化  
✅ **テキストの直接編集** - 誤字や表現を修正  
✅ **カスタム単語辞書** - 優先的に結合すべき単語を登録  
✅ **フレーム同期の自動維持** - 編集後も音声と同期を保持

---

## 問題の背景

### 発生した問題

動画を確認したところ、以下のような不自然な字幕の区切りが発生していました：

```
字幕1: プロデューサー出口氏がまさ
字幕2: さかの直接審査！？
```

**問題点:**
- 「まさか」という単語が「まさ」と「さ」に分断されている
- 視聴者にとって読みにくく、不自然な表示になる
- 日本語の単語の意味的なまとまりが失われている

### 原因

自動字幕生成システムは、以下の理由で単語を不自然に分割することがあります：

1. **文字数制限**: 1行あたりの文字数制限により、単語の途中で改行される
2. **音声認識の区切り**: Whisper APIの音声認識結果が不完全
3. **タイミング調整**: フレーム同期のために文字が分散配置される

---

## 解決方法

### 方法1: 手動編集ツールを使用（推奨）

[`manual_subtitle_editor.py`](manual_subtitle_editor.py) を使用して、対話的に字幕を編集します。

### 方法2: JSONファイルを直接編集

高度なユーザー向け。[`public/video-data-master.json`](public/video-data-master.json) を直接編集します。

### 方法3: カスタム単語辞書を事前登録

今後の生成時に問題を防ぐため、[`custom_words_dictionary.txt`](custom_words_dictionary.txt) に単語を登録します。

---

## 手動編集ツールの使い方

### インストール

必要なPythonパッケージがインストールされていることを確認してください：

```bash
# 既にrequirements.txtがある場合
pip install -r requirements.txt
```

### 対話モードの起動

```bash
python manual_subtitle_editor.py --interactive
```

### 基本コマンド

#### 1. 字幕リストを表示

```
> list
```

または、範囲を指定：

```
> list 0 5    # 0番から5件表示
```

**出力例:**
```
================================================================================
字幕リスト
================================================================================

[0]   sub_000
    テキスト: あのBTSを日本に導いた伝説の
    時間: 0.00s - 3.06s
    フレーム: 0 - 90
    文字数: 15

[1] ✎ sub_001
    テキスト: プロデューサー出口氏が
    時間: 3.06s - 4.52s
    フレーム: 91 - 135
    文字数: 11
```

**凡例:**
- `✎` = 手動編集済み

#### 2. テキストで検索

```
> search まさか
```

**出力例:**
```
検索結果: 2件
  [1] プロデューサー出口氏がまさかの (3.06s)
  [2] まさかの直接審査！？ (5.52s)
```

#### 3. 字幕を分割

単語の途中で区切られている字幕を分割します。

```
> split <字幕番号> <分割位置>
```

**例:** 字幕1を11文字目で分割（「が」の後）

```
> split 1 11
```

**結果:**
```
✓ 字幕分割完了:
  前半: プロデューサー出口氏が
  後半: まさかの
```

#### 4. 字幕を結合

複数の字幕を1つにまとめます。

```
> merge <開始番号> <終了番号>
```

**例:** 字幕1と2を結合

```
> merge 1 2
```

**結果:**
```
✓ 字幕結合完了: まさかの直接審査！？
```

#### 5. タイミングを調整

字幕の表示タイミングを微調整します。

```
> time <字幕番号> <開始時間> <終了時間>
```

**例:** 字幕2のタイミングを調整

```
> time 2 5.52 8.06
```

**結果:**
```
✓ タイミング調整完了: まさかの直接審査！？
  開始: 5.52s (フレーム 165)
  終了: 8.06s (フレーム 241)
```

#### 6. テキストを編集

字幕のテキストを直接編集します。

```
> edit <字幕番号> <新しいテキスト>
```

**例:** 字幕2のテキストを変更

```
> edit 2 まさかの直接審査！？
```

**結果:**
```
✓ テキスト編集完了:
  変更前: まさかの直接審査
  変更後: まさかの直接審査！？
```

#### 7. カスタム単語を追加

```
> word まさかの直接審査
```

**結果:**
```
✓ カスタム単語追加: まさかの直接審査
```

#### 8. 保存

変更を保存します（自動的にバックアップも作成されます）。

```
> save
```

**結果:**
```
✓ バックアップ作成: public/video-data-master.json.backup
✓ 保存完了: public/video-data-master.json
```

#### 9. 終了

```
> quit
```

---

## カスタム単語辞書

### 辞書ファイルの編集

[`custom_words_dictionary.txt`](custom_words_dictionary.txt) を編集して、優先的に結合すべき単語を登録します。

**ファイル形式:**
```txt
# コメント行は#で始める
まさか
まさかの
プロデューサー
直接審査
K-POP
```

### 辞書の読み込み

Pythonスクリプトから辞書を読み込む：

```python
from manual_subtitle_editor import SubtitleEditor

editor = SubtitleEditor('public/video-data-master.json')
editor.load_custom_dictionary('custom_words_dictionary.txt')
```

### 今後の字幕生成に反映

字幕生成スクリプト（`generate_video_data_master.py`など）を修正して、カスタム辞書を参照するようにします。

---

## 実践例

### 例1: 「まさか」の分断を修正

**問題:**
```
字幕1: プロデューサー出口氏がまさ
字幕2: さかの直接審査！？
```

**修正手順:**

1. **対話モードを起動**
   ```bash
   python manual_subtitle_editor.py --interactive
   ```

2. **問題の字幕を確認**
   ```
   > list 0 5
   ```

3. **字幕1を分割**（「が」の後で分割）
   ```
   > split 1 11
   ```

4. **新しい字幕を作成**（「まさかの直接審査！？」として結合）
   ```
   > merge 2 3
   ```

5. **タイミングを微調整**
   ```
   > time 2 5.52 8.06
   ```

6. **スタイルを強調に変更**（JSONを直接編集）
   - `"type": "emphasis"` に変更
   - `"fontSize": 80` に拡大
   - `"color": "#FFD700"` (ゴールド) に変更

7. **保存**
   ```
   > save
   ```

**結果:**
```
字幕1: プロデューサー出口氏が
字幕2: まさかの直接審査！？  ← 綺麗に1つの塊として表示
字幕3: K-POPで本気で成功したいなら
```

### 例2: プログラム的な編集

```python
from manual_subtitle_editor import SubtitleEditor

# エディタを初期化
editor = SubtitleEditor('public/video-data-master.json')

# カスタム辞書を読み込み
editor.load_custom_dictionary('custom_words_dictionary.txt')

# 「まさか」を含む字幕を検索
results = editor.find_subtitle_by_text('まさか')
print(f"見つかった字幕: {len(results)}件")

# 字幕1を11文字目で分割
editor.split_subtitle(1, 11)

# 新しく作成された字幕2と3を結合
editor.merge_subtitles(2, 3)

# タイミングを調整
editor.adjust_timing(2, new_start_time=5.52, new_end_time=8.06)

# テキストを編集
editor.edit_text(2, 'まさかの直接審査！？')

# 保存
editor.save()

print("✓ 修正完了！")
```

---

## JSONファイルの直接編集

### 構造の理解

[`public/video-data-master.json`](public/video-data-master.json) の基本構造：

```json
{
  "version": "3.0",
  "metadata": { ... },
  "content": { ... },
  "audio": { ... },
  "subtitles": [
    {
      "id": "sub_001",
      "text": "プロデューサー出口氏が",
      "startTime": 3.06,
      "endTime": 4.52,
      "startFrame": 91,
      "endFrame": 135,
      "duration": 1.46,
      "characterCount": 11,
      "characters": [
        {
          "char": "プ",
          "startTime": 3.06,
          "endTime": 3.28,
          "startFrame": 91,
          "endFrame": 98,
          "duration": 0.22,
          "wordIndex": 15
        },
        ...
      ],
      "style": { ... },
      "metadata": {
        "isKeyPhrase": true,
        "characterCount": 11,
        "manuallyEdited": true
      }
    }
  ]
}
```

### 手動編集時の注意点

#### ✅ 必ず守ること

1. **バックアップを作成**
   ```bash
   cp public/video-data-master.json public/video-data-master.json.backup
   ```

2. **JSON構文を維持**
   - カンマ、括弧、引用符を正確に
   - JSONバリデーターで確認

3. **フレーム同期を維持**
   ```
   startFrame = floor(startTime * fps)
   endFrame = floor(endTime * fps)
   ```
   FPS = 30の場合

4. **duration を再計算**
   ```
   duration = endTime - startTime
   ```

5. **characterCount を更新**
   ```
   characterCount = len(text)
   ```

6. **manuallyEdited フラグを追加**
   ```json
   "metadata": {
     "manuallyEdited": true,
     "editedAt": "2026-07-13T23:00:00Z"
   }
   ```

#### ❌ やってはいけないこと

- ❌ `characters` 配列の `wordIndex` を変更しない（連番を維持）
- ❌ 時間の逆転（`startTime > endTime`）
- ❌ フレームの逆転（`startFrame > endFrame`）
- ❌ 他の字幕との時間的重複（特別な理由がない限り）

### 直接編集の例

**修正前:**
```json
{
  "id": "sub_001",
  "text": "プロデューサー出口氏がまさかの",
  "startTime": 3.06,
  "endTime": 6.14,
  "characterCount": 15
}
```

**修正後:**
```json
{
  "id": "sub_001",
  "text": "プロデューサー出口氏が",
  "startTime": 3.06,
  "endTime": 4.52,
  "characterCount": 11,
  "metadata": {
    "manuallyEdited": true
  }
},
{
  "id": "sub_001b",
  "text": "まさかの直接審査！？",
  "startTime": 5.52,
  "endTime": 8.06,
  "characterCount": 9,
  "metadata": {
    "manuallyEdited": true,
    "highlightPhrase": "まさかの直接審査"
  }
}
```

---

## トラブルシューティング

### 問題1: 編集後に動画が再生されない

**原因:** JSON構文エラー

**解決策:**
```bash
# JSONの構文チェック
python -m json.tool public/video-data-master.json

# エラーがある場合、バックアップから復元
cp public/video-data-master.json.backup public/video-data-master.json
```

### 問題2: 字幕と音声がズレる

**原因:** タイムスタンプやフレーム番号の不整合

**解決策:**
```python
from manual_subtitle_editor import SubtitleEditor

editor = SubtitleEditor('public/video-data-master.json')

# タイミングを再調整
editor.adjust_timing(subtitle_index, new_start_time, new_end_time)
editor.save()
```

### 問題3: 文字が表示されない

**原因:** `characters` 配列が空、または `characterCount` が0

**解決策:**
```python
# テキストを編集（自動的にcharacters配列を再構築）
editor.edit_text(subtitle_index, "新しいテキスト", preserve_timing=True)
editor.save()
```

### 問題4: スタイルが反映されない

**原因:** `style` オブジェクトの設定ミス

**解決策:**

JSONで直接編集：
```json
"style": {
  "type": "emphasis",
  "animation": "fadeInScale",
  "fontSize": 80,
  "fontWeight": "bold",
  "color": "#FFD700",
  "textShadow": "0px 0px 15px rgba(255,215,0,0.9), 0px 0px 40px rgba(255,215,0,0.6)",
  "position": "center"
}
```

---

## ベストプラクティス

### 1. 編集前の準備

- ✅ 動画を視聴して問題箇所を特定
- ✅ バックアップを作成
- ✅ 修正計画を立てる

### 2. 編集中

- ✅ 小さな変更から始める
- ✅ 変更ごとに保存してテスト
- ✅ `manuallyEdited` フラグを追加

### 3. 編集後

- ✅ 動画を再生して確認
- ✅ 音声との同期を確認
- ✅ 他の字幕への影響を確認

### 4. 今後のために

- ✅ カスタム単語辞書に追加
- ✅ 修正パターンをドキュメント化
- ✅ 生成スクリプトの改善を検討

---

## 関連ファイル

- [`manual_subtitle_editor.py`](manual_subtitle_editor.py) - 手動編集ツール
- [`custom_words_dictionary.txt`](custom_words_dictionary.txt) - カスタム単語辞書
- [`public/video-data-master.json`](public/video-data-master.json) - 字幕データ
- [`CHARACTER_LEVEL_SYNC_GUIDE.md`](CHARACTER_LEVEL_SYNC_GUIDE.md) - 文字レベル同期ガイド

---

## まとめ

このガイドで説明した手動編集システムにより、以下が可能になります：

✅ **不自然な単語の区切りを修正** - 「まさか」が「まさ/さ」に分断される問題を解決  
✅ **タイミングの最適化** - 視聴者にとって読みやすいタイミングに調整  
✅ **カスタム単語辞書** - 今後の生成時に同じ問題を防止  
✅ **フレーム同期の維持** - 編集後も音声と完璧に同期

**重要:** 編集は慎重に行い、必ずバックアップを取ってから作業してください。

---

## サポート

問題が発生した場合は、以下を確認してください：

1. バックアップファイルが存在するか
2. JSON構文が正しいか
3. タイムスタンプとフレーム番号が整合しているか

それでも解決しない場合は、バックアップから復元して再度試してください。
