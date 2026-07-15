# 🚀 固有名詞保護システム クイックスタートガイド

## 📌 5分で理解する固有名詞保護システム

---

## 🎯 何が解決されるのか？

### ❌ 従来の問題

```
入力: "K-RISEとは、アジアモデルフェスティバルです"

問題1: K-RISEが分割される
  → "K" "-" "R" "I" "S" "E" と1文字ずつバラバラに

問題2: 「とは」が固有名詞の一部と誤認識
  → "K-RISEとは" が一つの固有名詞として扱われる

問題3: セグメント分割が不自然
  → "K-RI" "SEとは" のように固有名詞の途中で分割
```

### ✅ v3.2の解決策

```
入力: "K-RISEとは、アジアモデルフェスティバルです"

✅ K-RISEは一塊として保護
✅ 「とは」は独立した文脈的表現として認識
✅ セグメント分割は固有名詞の境界を尊重

結果:
  セグメント1: "K-RISEとは"
  セグメント2: "アジアモデルフェスティバルです"
```

---

## 📦 必要なファイル

| ファイル | 役割 |
|---------|------|
| [`proper_nouns_dictionary.json`](proper_nouns_dictionary.json) | 固有名詞と文脈的表現の辞書 |
| [`proper_noun_parser.py`](proper_noun_parser.py) | パーサーの実装 |
| [`generate_video_data_master_v3.2.py`](generate_video_data_master_v3.2.py) | 統合スクリプト |
| [`test_proper_noun_system.py`](test_proper_noun_system.py) | テストスイート |

---

## 🏃 すぐに使う

### ステップ1: テストを実行

```bash
python test_proper_noun_system.py
```

**期待される出力:**
```
🎯 固有名詞保護システム テストスイート
============================================================

📝 テストケース1: K-RISEとは
------------------------------------------------------------
✅ 固有名詞検出: 2個
   - 'K-RISE' @ 位置 0-6
   - 'アジアモデルフェスティバル' @ 位置 10-23

✅ 文脈的表現検出: 1個
   - 'とは' @ 位置 6-8

✅ テストケース1: 成功

... (他のテスト)

📊 テスト結果サマリー
============================================================
   ✅ 成功 - K-RISEとは
   ✅ 成功 - BTSと出口氏
   ✅ 成功 - K-POPとLINE
   ✅ 成功 - セグメント境界
   ✅ 成功 - 複雑な文章
   ✅ 成功 - 文字アノテーション

合計: 6/6 テスト成功

🎉 すべてのテストが成功しました！
```

### ステップ2: 動画データを生成

```bash
python generate_video_data_master_v3.2.py
```

**処理フロー:**
```
🎬 Character-Level Audio-Driven Video Pipeline v3.2
   ✨ NEW: Proper Noun Protection System
============================================================
📝 Script: K-RISEとは、アジアモデルフェスティバル...
🎯 Project ID: kpop-audition
🎞️  FPS: 30
🔧 Janome: ✅ Available
🎯 Proper Noun Parser: ✅ Available

🎤 Step 1/5: Generating high-quality audio (TTS-1-HD)...
   ✅ Audio generated: public/audio.mp3

🔍 Step 2/5: Analyzing audio with Whisper API...
   ✅ Transcribed: K-RISEとは、アジアモデルフェスティバル...
   ✅ Duration: 5.50s
   ✅ Words detected: 8

🎯 Step 3/5: Calculating character-level timestamps...
   ✅ Generated 25 character timestamps

🎤 Step 4/5: Building proper-noun-aware karaoke subtitles...
   🎯 Protecting 2 proper nouns:
      - 'K-RISE' @ position 0-6
      - 'アジアモデルフェスティバル' @ position 10-23
   ✅ Created 2 natural segments

🔧 Step 5/5: Building integrated data structure...
   ✅ Saved to: public/video-data-master.json

✨ Character-Level Pipeline v3.2 completed successfully!
```

---

## 🔧 カスタマイズ

### 固有名詞を追加する

[`proper_nouns_dictionary.json`](proper_nouns_dictionary.json) を編集:

```json
{
  "properNouns": {
    "brands": [
      "K-RISE",
      "K-POP",
      "BTS",
      "LINE",
      "あなたのブランド名"  // ← ここに追加
    ]
  }
}
```

### 文脈的表現を追加する

```json
{
  "contextualExpressions": {
    "definitions": [
      "とは",
      "というのは",
      "って何",
      "あなたの表現"  // ← ここに追加
    ]
  }
}
```

---

## 💻 コードで使う

### 基本的な使い方

```python
from proper_noun_parser import ProperNounParser

# パーサーを初期化
parser = ProperNounParser()

# テキストを解析
text = "K-RISEとは、新しいプロジェクトです。"

# 固有名詞を検出
proper_nouns = parser.identify_proper_nouns_in_text(text)
print(proper_nouns)
# [{"noun": "K-RISE", "start": 0, "end": 6, "type": "proper_noun"}]

# 文脈的表現を検出
contextual = parser.identify_contextual_expressions(text, proper_nouns)
print(contextual)
# [{"expression": "とは", "start": 6, "end": 8, "type": "contextual_expression"}]

# トークンに分割
tokens = parser.parse_text_with_boundaries(text)
for token in tokens:
    print(f"[{token['type']}] {token['text']}")
# [proper_noun] K-RISE
# [contextual_expression] とは
# [normal] 、新しいプロジェクトです。
```

---

## 📊 出力フォーマット

### JSON構造

```json
{
  "version": "3.2",
  "metadata": {
    "syncMode": "character-level-proper-noun-aware",
    "properNounProtection": true
  },
  "subtitles": [
    {
      "id": "sub_001",
      "text": "K-RISE",
      "characters": [
        {
          "char": "K",
          "startTime": 0.0,
          "endTime": 0.167,
          "isProperNoun": true,
          "tokenType": "proper_noun"
        }
      ]
    }
  ]
}
```

---

## ❓ よくある質問

### Q1: 固有名詞が検出されない

**A:** 辞書に登録されていない可能性があります。

```bash
# 辞書を確認
cat proper_nouns_dictionary.json

# 固有名詞を追加
# proper_nouns_dictionary.json を編集して追加
```

### Q2: 「とは」が固有名詞の一部になる

**A:** v3.2スクリプトを使用していることを確認してください。

```bash
# v3.2を使用
python generate_video_data_master_v3.2.py

# 従来版（v3.1）は使用しない
# python generate_video_data_master.py  ← これは使わない
```

### Q3: セグメントが固有名詞の途中で分割される

**A:** `respect_proper_nouns=True` が設定されていることを確認。

```python
# 正しい使い方
boundaries = parser.get_segmentation_boundaries(
    text, 
    respect_proper_nouns=True  # ← これが重要
)
```

---

## 🎓 実例

### 例1: K-RISEの紹介

**入力テキスト:**
```
K-RISEとは、アジアモデルフェスティバルが主催する
新しいK-POPオーディションプロジェクトです。
```

**処理結果:**

**固有名詞:**
- K-RISE (位置: 0-6)
- アジアモデルフェスティバル (位置: 10-23)
- K-POP (位置: 32-37)

**文脈的表現:**
- とは (位置: 6-8)

**セグメント分割:**
1. "K-RISEとは"
2. "アジアモデルフェスティバルが主催する"
3. "新しいK-POPオーディション"
4. "プロジェクトです"

### 例2: BTSプロデューサー

**入力テキスト:**
```
BTSを日本に導いた伝説のプロデューサー、出口氏が審査します。
```

**処理結果:**

**固有名詞:**
- BTS (位置: 0-3)
- 出口氏 (位置: 18-21)

**セグメント分割:**
1. "BTSを日本に導いた"
2. "伝説のプロデューサー"
3. "出口氏が審査します"

---

## 🔍 デバッグ

### パーサーの動作を確認

```python
from proper_noun_parser import ProperNounParser

parser = ProperNounParser()
text = "あなたのテキスト"

# 詳細なログを出力
print("=" * 60)
print(f"入力: {text}")
print("=" * 60)

# 固有名詞
proper_nouns = parser.identify_proper_nouns_in_text(text)
print(f"\n固有名詞: {len(proper_nouns)}個")
for pn in proper_nouns:
    print(f"  - {pn}")

# 文脈的表現
contextual = parser.identify_contextual_expressions(text, proper_nouns)
print(f"\n文脈的表現: {len(contextual)}個")
for ctx in contextual:
    print(f"  - {ctx}")

# トークン
tokens = parser.parse_text_with_boundaries(text)
print(f"\nトークン: {len(tokens)}個")
for i, token in enumerate(tokens, 1):
    print(f"  {i}. [{token['type']:20s}] '{token['text']}'")
```

---

## 📚 次のステップ

1. ✅ テストを実行して動作確認
2. ✅ 辞書に固有名詞を追加
3. ✅ 動画データを生成
4. ✅ 出力JSONを確認
5. ✅ Remotionで動画をレンダリング

詳細は [`PROPER_NOUN_PROTECTION_SYSTEM.md`](PROPER_NOUN_PROTECTION_SYSTEM.md) を参照してください。

---

**作成日:** 2026-07-14  
**バージョン:** 3.2  
**所要時間:** 5分
