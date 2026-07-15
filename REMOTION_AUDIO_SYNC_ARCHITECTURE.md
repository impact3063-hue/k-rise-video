# 🎬 Remotion Audio-Driven Video Architecture
## 世界標準のデータ駆動型動画生成システム設計書

---

## 📊 現状分析

### 現在のプロジェクト構造
```
k-rise-video/
├── Python側（音声生成・字幕生成）
│   ├── make_subtitles_auto.py      # OpenAI TTS + Whisper API
│   └── sync_subtitles_to_audio.py  # 音声解析・同期処理
├── Remotion側（動画レンダリング）
│   ├── src/Composition.tsx         # 基本コンポジション
│   └── public/sample-video.json    # 字幕データ
└── データファイル
    ├── public/audio.mp3            # 生成された音声
    └── public/sample-video.json    # フレーム単位の字幕
```

### 🔴 現在の問題点
1. **音声と字幕のズレ**: 手動調整が必要で、完全同期が困難
2. **データ構造の不統一**: 複数のJSONフォーマットが混在
3. **スケーラビリティの欠如**: 1本ずつ手動生成、バリエーション対応不可
4. **音声解析の不完全性**: Whisperの単語タイムスタンプを活用しきれていない

---

## 🌍 世界標準のRemotionアプローチ

### 1. **完全データ駆動型アーキテクチャ（Data-Driven Video）**

#### 原則
- **Single Source of Truth**: 1つのJSONファイルがすべてを制御
- **Declarative Configuration**: 宣言的な設定で動画を定義
- **Zero Manual Adjustment**: 手動調整ゼロの完全自動化

#### 実装例（世界標準）
```json
{
  "metadata": {
    "title": "K-POP Audition Video #001",
    "duration": 21.6,
    "fps": 30,
    "totalFrames": 648,
    "generatedAt": "2026-07-13T11:30:00Z"
  },
  "audio": {
    "narration": {
      "file": "audio.mp3",
      "duration": 21.6,
      "volume": 4.0,
      "model": "tts-1-hd",
      "voice": "nova"
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
      "words": [
        {"text": "あの", "start": 0.0, "end": 0.3, "startFrame": 0, "endFrame": 9},
        {"text": "BTSを", "start": 0.3, "end": 0.8, "startFrame": 9, "endFrame": 24},
        {"text": "日本に", "start": 0.8, "end": 1.2, "startFrame": 24, "endFrame": 36},
        {"text": "導いた", "start": 1.2, "end": 1.467, "startFrame": 36, "endFrame": 44}
      ],
      "style": {
        "type": "emphasis",
        "animation": "fadeInScale",
        "color": "#FFFFFF",
        "fontSize": 75,
        "fontWeight": "bold",
        "textShadow": "0px 0px 10px rgba(230,255,0,0.8)"
      }
    }
  ],
  "scenes": [
    {
      "id": "scene_intro",
      "startFrame": 0,
      "endFrame": 147,
      "background": "bg-cyber.png",
      "logo": {
        "file": "logo.png",
        "position": "top-center",
        "width": "80%"
      }
    }
  ]
}
```

---

### 2. **音声駆動型アニメーション（Audio-Driven Animation）**

#### 🎯 核心原則
> **"音声が真実、すべては音声に従う"**

#### A. Whisper APIの完全活用

```python
# 世界標準の実装パターン
def generate_audio_driven_data(script_text: str) -> dict:
    """
    音声生成 → 音声解析 → データ統合を1つのパイプラインで実行
    """
    # Step 1: 高品質音声生成
    audio_file = generate_tts(script_text, model="tts-1-hd", voice="nova")
    
    # Step 2: 単語レベルの完全解析
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="verbose_json",
        language="ja",
        timestamp_granularities=["word", "segment"]  # 両方取得
    )
    
    # Step 3: 統合データ構造の生成
    return {
        "metadata": extract_metadata(transcription),
        "audio": {
            "file": audio_file,
            "duration": transcription.duration,
            "fullText": transcription.text
        },
        "subtitles": build_smart_subtitles(transcription.words),
        "words": transcription.words,  # 単語レベルデータを保持
        "segments": transcription.segments  # セグメントデータも保持
    }
```

#### B. スマート字幕生成アルゴリズム

```python
def build_smart_subtitles(words: list, max_chars: int = 15, fps: int = 30) -> list:
    """
    世界標準の字幕生成ロジック
    - 読みやすさ優先（1行15文字以内）
    - 音声との完全同期（1フレーム精度）
    - 自然な区切り（句読点・意味単位）
    """
    subtitles = []
    current_subtitle = {
        "text": "",
        "words": [],
        "startTime": None,
        "endTime": None
    }
    
    for word in words:
        # 追加判定
        would_be_text = current_subtitle["text"] + word["text"]
        has_punctuation = any(p in word["text"] for p in ["、", "。", "！", "？"])
        
        # 区切り条件
        should_break = (
            len(would_be_text) > max_chars or
            has_punctuation or
            (word["start"] - current_subtitle.get("startTime", 0)) > 3.0  # 最大3秒
        )
        
        if should_break and current_subtitle["text"]:
            # 現在の字幕を確定
            subtitles.append(finalize_subtitle(current_subtitle, fps))
            current_subtitle = {"text": "", "words": [], "startTime": None}
        
        # 単語を追加
        if current_subtitle["startTime"] is None:
            current_subtitle["startTime"] = word["start"]
        current_subtitle["text"] += word["text"]
        current_subtitle["words"].append(word)
        current_subtitle["endTime"] = word["end"]
    
    # 最後の字幕
    if current_subtitle["text"]:
        subtitles.append(finalize_subtitle(current_subtitle, fps))
    
    # 重なり防止処理
    return prevent_overlap(subtitles)

def finalize_subtitle(subtitle: dict, fps: int) -> dict:
    """字幕オブジェクトを確定"""
    return {
        "id": f"sub_{len(subtitles):03d}",
        "text": subtitle["text"].strip(),
        "startTime": subtitle["startTime"],
        "endTime": subtitle["endTime"],
        "startFrame": int(subtitle["startTime"] * fps),
        "endFrame": int(subtitle["endTime"] * fps) - 1,  # 1フレーム前で終了
        "words": subtitle["words"],
        "duration": subtitle["endTime"] - subtitle["startTime"]
    }

def prevent_overlap(subtitles: list) -> list:
    """重なり完全防止"""
    for i in range(len(subtitles) - 1):
        current = subtitles[i]
        next_sub = subtitles[i + 1]
        
        # 現在の字幕は次の字幕の1フレーム前で終了
        if current["endFrame"] >= next_sub["startFrame"]:
            current["endFrame"] = next_sub["startFrame"] - 1
            current["endTime"] = current["endFrame"] / 30.0
    
    return subtitles
```

---

### 3. **動的テロップの高度化（Dynamic Text Effects）**

#### 音声特性に応じたアニメーション

```typescript
// src/components/AudioDrivenSubtitle.tsx
import { useCurrentFrame, interpolate, Audio, useAudioData, visualizeAudio } from "remotion";

interface SubtitleWithAudio {
  text: string;
  startFrame: number;
  endFrame: number;
  words: Array<{
    text: string;
    startFrame: number;
    endFrame: number;
  }>;
  style: {
    type: "normal" | "emphasis" | "question" | "cta";
    animation: "fadeIn" | "fadeInScale" | "bounce" | "slide";
  };
}

export const AudioDrivenSubtitle: React.FC<{subtitle: SubtitleWithAudio}> = ({subtitle}) => {
  const frame = useCurrentFrame();
  const audioData = useAudioData(staticFile("audio.mp3"));
  
  // 現在の音声ボリュームを取得
  const volume = audioData 
    ? visualizeAudio({
        fps: 30,
        frame,
        audioData,
        numberOfSamples: 16
      }).reduce((a, b) => a + b, 0) / 16
    : 0;
  
  // ボリュームに応じてスケールを変化
  const scale = interpolate(
    volume,
    [0, 0.5, 1],
    [1, 1.1, 1.2],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  
  // フレーム内での進行度
  const progress = (frame - subtitle.startFrame) / (subtitle.endFrame - subtitle.startFrame);
  
  // アニメーション
  const opacity = interpolate(progress, [0, 0.1, 0.9, 1], [0, 1, 1, 0]);
  const translateY = interpolate(progress, [0, 0.2], [20, 0], { extrapolateRight: "clamp" });
  
  return (
    <div style={{
      opacity,
      transform: `translateY(${translateY}px) scale(${scale})`,
      transition: "transform 0.1s ease-out"
    }}>
      {subtitle.text}
    </div>
  );
};
```

---

## 🎯 推奨される新しいデータ構造

### **統合データフォーマット v2.0**

```json
{
  "version": "2.0",
  "metadata": {
    "projectId": "kpop-audition-001",
    "title": "K-POP Audition - BTS Producer",
    "generatedAt": "2026-07-13T11:30:00Z",
    "fps": 30,
    "duration": 21.6,
    "totalFrames": 648
  },
  "content": {
    "script": {
      "original": "あのBTSを日本に導いた伝説のプロデューサー、出口氏が…",
      "transcribed": "あのBTSを日本に導いた伝説のプロデューサー、出口氏が…"
    }
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
      "loop": true,
      "fadeIn": 0.5,
      "fadeOut": 0.5
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
          "endFrame": 9,
          "confidence": 0.98
        },
        {
          "text": "BTSを",
          "start": 0.3,
          "end": 0.8,
          "startFrame": 9,
          "endFrame": 24,
          "confidence": 0.99
        }
      ],
      "style": {
        "type": "emphasis",
        "animation": "fadeInScale",
        "fontSize": 75,
        "fontWeight": "bold",
        "color": "#FFFFFF",
        "textShadow": "0px 0px 10px rgba(230,255,0,0.8)",
        "position": "center"
      },
      "metadata": {
        "isKeyPhrase": true,
        "sentiment": "positive",
        "emphasis": "high"
      }
    }
  ],
  "scenes": [
    {
      "id": "scene_001",
      "name": "Introduction",
      "startFrame": 0,
      "endFrame": 147,
      "duration": 4.9,
      "background": {
        "type": "image",
        "file": "bg-cyber.png",
        "opacity": 1.0,
        "animation": "zoomIn"
      },
      "elements": [
        {
          "type": "logo",
          "file": "logo.png",
          "position": "top-center",
          "width": "80%",
          "animation": "fadeIn"
        }
      ]
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

---

## 🚀 実装ロードマップ

### Phase 1: データ統合（1-2日）
- [ ] 新しいJSON構造の定義
- [ ] Python側の生成スクリプト統合
- [ ] 単一パイプラインの構築

### Phase 2: Remotionコンポーネント刷新（2-3日）
- [ ] AudioDrivenSubtitle コンポーネント作成
- [ ] データ駆動型レンダリングエンジン
- [ ] 音声同期の完全自動化

### Phase 3: 高度化（3-5日）
- [ ] 音声ボリューム連動アニメーション
- [ ] 感情分析による自動スタイリング
- [ ] バリエーション自動生成システム

---

## 💡 即座に適用できる改善策

### 1. **統合生成スクリプトの作成**

```python
# generate_video_data_master.py
"""
世界標準のデータ駆動型動画生成マスタースクリプト
"""
import os
import json
from datetime import datetime
from openai import OpenAI

def generate_complete_video_data(
    script_text: str,
    project_id: str = "kpop-audition",
    fps: int = 30
) -> dict:
    """
    音声生成から字幕同期まで完全自動化
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # 1. 音声生成
    print("🎤 Generating audio...")
    audio_response = client.audio.speech.create(
        model="tts-1-hd",
        voice="nova",
        input=script_text
    )
    audio_path = f"public/audio.mp3"
    audio_response.stream_to_file(audio_path)
    
    # 2. 音声解析（単語レベル）
    print("🔍 Analyzing audio with Whisper...")
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            language="ja",
            timestamp_granularities=["word", "segment"]
        )
    
    # 3. スマート字幕生成
    print("📝 Building smart subtitles...")
    subtitles = build_smart_subtitles(transcription.words, fps=fps)
    
    # 4. 統合データ構造
    video_data = {
        "version": "2.0",
        "metadata": {
            "projectId": project_id,
            "generatedAt": datetime.utcnow().isoformat() + "Z",
            "fps": fps,
            "duration": transcription.duration,
            "totalFrames": int(transcription.duration * fps)
        },
        "content": {
            "script": {
                "original": script_text,
                "transcribed": transcription.text
            }
        },
        "audio": {
            "narration": {
                "file": "audio.mp3",
                "duration": transcription.duration,
                "volume": 4.0
            },
            "bgm": {
                "file": "bg-music.mp3",
                "volume": 0.08,
                "loop": True
            }
        },
        "subtitles": subtitles
    }
    
    # 5. 保存
    output_path = "public/video-data-master.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Complete! Generated {len(subtitles)} subtitles")
    print(f"📁 Saved to: {output_path}")
    
    return video_data
```

### 2. **Remotion側の統合コンポーネント**

```typescript
// src/AudioDrivenComposition.tsx
import { AbsoluteFill, staticFile, useCurrentFrame, Audio } from "remotion";
import videoData from "../public/video-data-master.json";

export const AudioDrivenComposition = () => {
  const frame = useCurrentFrame();
  
  // 現在表示すべき字幕を取得
  const currentSubtitle = videoData.subtitles.find(
    (sub) => frame >= sub.startFrame && frame <= sub.endFrame
  );
  
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* 音声 */}
      <Audio 
        src={staticFile(videoData.audio.narration.file)} 
        volume={videoData.audio.narration.volume} 
      />
      <Audio 
        src={staticFile(videoData.audio.bgm.file)} 
        volume={videoData.audio.bgm.volume} 
        loop={videoData.audio.bgm.loop}
      />
      
      {/* 背景 */}
      <img src={staticFile("bg-cyber.png")} style={{...}} />
      
      {/* 字幕 */}
      {currentSubtitle && (
        <div style={{
          position: "absolute",
          top: "50%",
          left: 0,
          right: 0,
          transform: "translateY(-50%)",
          textAlign: "center",
          color: currentSubtitle.style.color,
          fontSize: currentSubtitle.style.fontSize,
          fontWeight: currentSubtitle.style.fontWeight,
          textShadow: currentSubtitle.style.textShadow
        }}>
          {currentSubtitle.text}
        </div>
      )}
    </AbsoluteFill>
  );
};
```

---

## 📚 参考：世界のRemotionベストプラクティス

### 推奨リソース
1. **Remotion公式ドキュメント**: Audio-driven animations
2. **GitHub Examples**: remotion-dev/template-audiogram
3. **Community Showcases**: Data-driven video generation

### キーコンセプト
- **Declarative over Imperative**: 宣言的な設定を優先
- **Data as Source of Truth**: データが唯一の真実
- **Frame-Perfect Sync**: フレーム完全同期
- **Scalable Architecture**: スケーラブルな設計

---

## ✅ まとめ：次のステップ

### 今すぐ実装すべきこと
1. ✅ **統合データ構造の採用**: `video-data-master.json`
2. ✅ **単一パイプラインの構築**: `generate_video_data_master.py`
3. ✅ **Remotionコンポーネントの刷新**: データ駆動型に移行

### 中期的な目標
- 音声ボリューム連動アニメーション
- 複数バリエーション自動生成
- APIサーバー化（REST/GraphQL）

### 長期的なビジョン
- 完全自動化されたビデオファクトリー
- AIによる自動最適化
- リアルタイムプレビュー機能

---

**このアーキテクチャに基づいて、今後のコード生成を行います。**
