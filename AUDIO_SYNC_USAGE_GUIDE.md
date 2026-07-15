# 🎯 Audio-Driven Video Generation - 使用ガイド

## 📚 概要

このプロジェクトは、世界標準のRemotionベストプラクティスに基づいた、完全自動化されたデータ駆動型動画生成システムです。

### ✨ 主な特徴

1. **完全自動同期**: 音声と字幕が1フレーム単位で完全に同期
2. **データ駆動型**: 1つのJSONファイルですべてを制御
3. **スマートアニメーション**: 字幕の内容に応じて自動的にアニメーションを選択
4. **スケーラブル**: 台本を変えるだけで無限にバリエーション生成可能

---

## 🚀 クイックスタート

### 1. 台本の準備

[`today_script.txt`](today_script.txt) に動画のナレーション台本を記述します：

```
あのBTSを日本に導いた伝説のプロデューサー、出口氏が…まさかの直接審査！？
K-POPで本気で成功したいなら、このチャンスを逃したら後悔する。
何百人が夢破れた世界で、伝説の男があなたの才能を見抜く。
もう二度と巡ってこないこの瞬間、迷ってる時間はない。
次は君の番かもしれない。応募はLINEから！プロフィールのリンクをチェックしてね！
```

### 2. マスタースクリプトの実行

```bash
python generate_video_data_master.py
```

このコマンドは以下を自動実行します：

1. ✅ OpenAI TTS-1-HDで高品質音声を生成
2. ✅ Whisper APIで単語レベルの音声解析
3. ✅ スマート字幕生成（完全同期）
4. ✅ 統合データ構造の出力

**出力ファイル:**
- `public/audio.mp3` - 生成された音声
- `public/video-data-master.json` - 統合データ（新フォーマット）
- `public/sample-video.json` - レガシーフォーマット（後方互換性）

### 3. 動画のプレビュー

```bash
npm run dev
```

ブラウザで `http://localhost:3000` を開き、動画をプレビューします。

### 4. 動画のレンダリング

```bash
npx remotion render src/index.ts AudioDrivenComposition output.mp4
```

---

## 📊 データ構造の詳細

### 新フォーマット（video-data-master.json）

```json
{
  "version": "2.0",
  "metadata": {
    "projectId": "kpop-audition",
    "title": "K-POP Audition Video",
    "generatedAt": "2026-07-13T11:30:00Z",
    "fps": 30,
    "duration": 21.6,
    "totalFrames": 648
  },
  "audio": {
    "narration": {
      "file": "audio.mp3",
      "duration": 21.6,
      "volume": 4.0,
      "generationConfig": {
        "model": "tts-1-hd",
        "voice": "nova",
        "speed": 1.0
      }
    },
    "bgm": {
      "file": "bg-music.mp3",
      "volume": 0.08,
      "loop": true
    }
  },
  "subtitles": [
    {
      "id": "sub_001",
      "text": "あのBTSを日本に導いた",
      "startTime": 0.0,
      "endTime": 1.467,
      "startFrame": 0,
      "endFrame": 43,
      "duration": 1.467,
      "characterCount": 12,
      "words": [
        {
          "text": "あの",
          "start": 0.0,
          "end": 0.3,
          "startFrame": 0,
          "endFrame": 9
        }
      ],
      "style": {
        "type": "emphasis",
        "animation": "fadeInScale",
        "fontSize": 75,
        "fontWeight": "bold",
        "color": "#FFFFFF",
        "textShadow": "0px 0px 10px rgba(230,255,0,0.8)"
      },
      "metadata": {
        "isKeyPhrase": true,
        "wordCount": 4
      }
    }
  ],
  "analytics": {
    "totalWords": 45,
    "averageWordDuration": 0.48,
    "speechRate": 2.08,
    "pauseCount": 3,
    "longestPause": 0.5
  }
}
```

### 字幕スタイルの自動判定

スクリプトは字幕の内容を解析し、自動的に最適なスタイルを適用します：

| スタイルタイプ | 検出キーワード | アニメーション | 用途 |
|--------------|--------------|--------------|------|
| `emphasis` | BTS, 伝説, プロデューサー, チャンス | fadeInScale | 強調したい重要なフレーズ |
| `question` | ？ | bounce | 疑問文 |
| `cta` | 応募, チェック, LINE, 今すぐ | fadeInScale | 行動喚起 |
| `normal` | その他 | fadeIn | 通常のテキスト |

---

## 🎨 カスタマイズ

### 音声の変更

[`generate_video_data_master.py`](generate_video_data_master.py:67) の音声生成部分を編集：

```python
audio_response = client.audio.speech.create(
    model="tts-1-hd",
    voice="nova",  # alloy, echo, fable, onyx, nova, shimmer
    input=script_text
)
```

### 字幕の最大文字数を変更

```python
subtitles = build_smart_subtitles(
    words, 
    fps=30,
    max_chars=15,  # ここを変更（デフォルト: 15文字）
    max_duration=3.0  # 最大表示時間（秒）
)
```

### 音量の調整

```python
video_data = generate_complete_video_data(
    script_text=script_text,
    audio_volume=4.0,  # ナレーション音量
    bgm_volume=0.08    # BGM音量
)
```

### アニメーションのカスタマイズ

[`src/AudioDrivenComposition.tsx`](src/AudioDrivenComposition.tsx:178) でアニメーションを編集：

```typescript
case "fadeInScale":
  opacity = interpolate(progress, [0, 0.15, 0.85, 1], [0, 1, 1, 0.8]);
  scale = spring({
    frame: localFrame,
    fps,
    config: {
      damping: 12,      // 減衰（小さいほど弾む）
      stiffness: 100,   // 硬さ（大きいほど速い）
      mass: 0.5,        // 質量（大きいほど重い）
    },
  });
  break;
```

---

## 🔧 トラブルシューティング

### 音声と字幕がズレる

**原因**: Whisper APIの解析精度の問題

**解決策**:
1. [`generate_video_data_master.py`](generate_video_data_master.py:88) の `prompt` パラメータに固有名詞を追加：
   ```python
   prompt="BTS, 出口氏, LINE, プロデューサー, K-POP, オーディション, [追加の固有名詞]"
   ```

2. 字幕の区切り条件を調整：
   ```python
   should_break = (
       len(would_be_text) > max_chars or
       has_punctuation or
       current_duration > max_duration
   )
   ```

### 字幕が長すぎる

**解決策**: `max_chars` パラメータを小さくする：

```python
subtitles = build_smart_subtitles(words, fps=fps, max_chars=12)  # 15 → 12
```

### 音声が生成されない

**原因**: OpenAI APIキーが設定されていない

**解決策**:
1. [`.env`](.env) ファイルを確認
2. `OPENAI_API_KEY` が正しく設定されているか確認
3. APIキーの権限を確認（TTS + Whisper）

### TypeScriptエラーが出る

**解決策**:
```bash
npm install --save-dev @types/node
```

---

## 📈 パフォーマンス最適化

### 1. 音声生成の高速化

並列処理を使用する場合：

```python
from concurrent.futures import ThreadPoolExecutor

def generate_multiple_videos(scripts):
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(generate_complete_video_data, script)
            for script in scripts
        ]
        return [f.result() for f in futures]
```

### 2. レンダリングの高速化

```bash
# 並列レンダリング
npx remotion render src/index.ts AudioDrivenComposition output.mp4 --concurrency=4

# 品質を下げて高速化
npx remotion render src/index.ts AudioDrivenComposition output.mp4 --quality=60
```

---

## 🌍 世界標準のベストプラクティス

このプロジェクトは以下の原則に従っています：

### 1. Single Source of Truth
- すべてのデータは1つのJSONファイルに集約
- 手動調整は一切不要

### 2. Declarative Configuration
- 宣言的な設定でアニメーションを定義
- コードの可読性と保守性を向上

### 3. Frame-Perfect Sync
- 音声と字幕が1フレーム単位で完全同期
- Whisper APIの単語レベルタイムスタンプを活用

### 4. Scalable Architecture
- データ駆動型で無限にスケール可能
- APIサーバー化も容易

---

## 🎓 学習リソース

### Remotion公式ドキュメント
- [Audio-driven animations](https://www.remotion.dev/docs/audio)
- [Data-driven videos](https://www.remotion.dev/docs/data-driven)
- [Spring animations](https://www.remotion.dev/docs/spring)

### OpenAI API
- [Text-to-Speech Guide](https://platform.openai.com/docs/guides/text-to-speech)
- [Whisper API](https://platform.openai.com/docs/guides/speech-to-text)

---

## 📝 次のステップ

### Phase 1: 基本機能の習得 ✅
- [x] マスタースクリプトの実行
- [x] データ構造の理解
- [x] 基本的なカスタマイズ

### Phase 2: 高度な機能
- [ ] 複数バリエーションの自動生成
- [ ] カスタムアニメーションの作成
- [ ] 感情分析による自動スタイリング

### Phase 3: プロダクション化
- [ ] APIサーバーの構築
- [ ] バッチ処理システム
- [ ] 自動品質チェック

---

## 💡 よくある質問（FAQ）

### Q: 他の言語でも使えますか？

A: はい。[`generate_video_data_master.py`](generate_video_data_master.py:83) の `language` パラメータを変更してください：

```python
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="en",  # ja → en (英語)
    # ...
)
```

### Q: 動画の長さに制限はありますか？

A: OpenAI APIの制限により、音声は最大25MBまでです。通常、10分程度の動画まで対応可能です。

### Q: 商用利用は可能ですか？

A: OpenAI APIの利用規約に従ってください。生成された音声・動画の商用利用は可能ですが、APIの利用料金が発生します。

---

## 🤝 サポート

問題が発生した場合は、以下を確認してください：

1. [`REMOTION_AUDIO_SYNC_ARCHITECTURE.md`](REMOTION_AUDIO_SYNC_ARCHITECTURE.md) - アーキテクチャの詳細
2. [`generate_video_data_master.py`](generate_video_data_master.py) - スクリプトのソースコード
3. [`src/AudioDrivenComposition.tsx`](src/AudioDrivenComposition.tsx) - Remotionコンポーネント

---

**🎉 これで、世界標準のデータ駆動型動画生成システムを使いこなせます！**
