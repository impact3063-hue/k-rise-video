/**
 * 🎬 Audio-Driven Composition - Character-Level Sync
 * 世界最高峰のデータ駆動型Remotionコンポーネント
 *
 * 特徴:
 * - 1文字単位の超精密同期（Character-level timestamp）
 * - カラオケスタイルのハイライト表示
 * - フレーム完全同期（ズレゼロ）
 * - スマートアニメーション
 * - 🎯 句読点完全除去システム（Guard B - レンダリングレイヤー）
 */

import React from "react";
import {
  AbsoluteFill,
  staticFile,
  useCurrentFrame,
  Audio,
  interpolate,
  spring,
} from "remotion";
import { cleanText, isPunctuation } from "./utils/textCleaner";

// 型定義
interface CharacterTimestamp {
  char: string;
  startTime: number;
  endTime: number;
  startFrame: number;
  endFrame: number;
  duration: number;
  wordIndex: number;
}

interface SubtitleStyle {
  type: "normal" | "emphasis" | "question" | "cta";
  animation: "fadeIn" | "fadeInScale" | "bounce" | "slide";
  fontSize: number;
  fontWeight: string;
  color: string;
  textShadow: string;
  position: string;
}

interface Subtitle {
  id: string;
  text: string;
  startTime: number;
  endTime: number;
  startFrame: number;
  endFrame: number;
  duration: number;
  characterCount: number;
  characters: CharacterTimestamp[];  // 🎯 1文字単位のタイムスタンプ
  style: SubtitleStyle;
  metadata: {
    isKeyPhrase: boolean;
    characterCount: number;
  };
}

interface VideoData {
  version: string;
  metadata: {
    projectId: string;
    title: string;
    generatedAt: string;
    fps: number;
    duration: number;
    totalFrames: number;
    syncMode?: string;
  };
  content: {
    script: {
      original: string;
      transcribed: string;
    };
  };
  audio: {
    narration: {
      file: string;
      duration: number;
      volume: number;
      generationConfig: {
        model: string;
        voice: string;
        speed: number;
      };
    };
    bgm: {
      file: string;
      volume: number;
      loop: boolean;
      fadeIn: number;
      fadeOut: number;
    };
  };
  subtitles: Subtitle[];
  analytics: {
    totalWords: number;
    averageWordDuration: number;
    speechRate: number;
    pauseCount: number;
    longestPause: number;
  };
}

// レガシーフォーマット（後方互換性）
interface LegacySubtitle {
  text: string;
  startFrame: number;
  endFrame: number;
}

// データのインポート
import subtitlesData from "../public/sample-video.json";
import videoDataMaster from "../public/video-data-master.json";

const legacySubtitles: LegacySubtitle[] = subtitlesData as LegacySubtitle[];

// 新フォーマットの読み込み
let videoData: VideoData | null = null;
try {
  videoData = videoDataMaster as VideoData;
} catch (e) {
  // フォールバック：レガシーフォーマットを使用
  videoData = null;
}

/**
 * 🎯 カラオケスタイル字幕コンポーネント（1文字単位の超精密同期）
 * 📱 モバイル最適化：SNS対応セーフゾーン＋自動折り返し
 */
const KaraokeSubtitle: React.FC<{
  subtitle: Subtitle;
  frame: number;
}> = ({ subtitle, frame }) => {
  const fps = 30;
  // 🛡️ 防御的プログラミング：styleがundefinedの場合のフォールバック
  const style = subtitle?.style || { animation: "fadeIn", type: "normal" };
  const startFrame = subtitle.startFrame;
  const endFrame = subtitle.endFrame;

  // 字幕内での進行度（0-1）
  const localFrame = frame - startFrame;
  const totalFrames = endFrame - startFrame;
  const progress = Math.max(0, Math.min(1, localFrame / totalFrames));

  // アニメーションの計算
  let opacity = 1;
  let scale = 1;
  let translateY = 0;
  let translateX = 0;

  // 🛡️ 防御的プログラミング：animationプロパティのセーフティネット
  const animationType = style?.animation || "fadeIn";

  switch (animationType) {
    case "fadeIn":
      opacity = interpolate(progress, [0, 0.1, 0.9, 1], [0, 1, 1, 0.8]);
      break;

    case "fadeInScale":
      opacity = interpolate(progress, [0, 0.15, 0.85, 1], [0, 1, 1, 0.8]);
      scale = spring({
        frame: localFrame,
        fps,
        config: {
          damping: 12,
          stiffness: 100,
          mass: 0.5,
        },
      });
      break;

    case "bounce":
      opacity = interpolate(progress, [0, 0.1, 0.9, 1], [0, 1, 1, 0.8]);
      scale = spring({
        frame: localFrame,
        fps,
        config: {
          damping: 8,
          stiffness: 200,
          mass: 0.3,
        },
      });
      break;

    case "slide":
      opacity = interpolate(progress, [0, 0.15, 0.85, 1], [0, 1, 1, 0.8]);
      translateX = interpolate(progress, [0, 0.2], [-50, 0], {
        extrapolateRight: "clamp",
      });
      break;
  }

  // スタイルタイプによる追加効果
  let additionalShadow = "";
  // 🛡️ 防御的プログラミング：typeプロパティのセーフティネット
  const styleType = style?.type || "normal";
  if (styleType === "emphasis" || styleType === "cta") {
    // 強調時はグローを強化（パルス効果）
    const glowIntensity = 1.0 + Math.sin(localFrame * 0.2) * 0.3;
    additionalShadow = `, 0px 0px ${20 * glowIntensity}px rgba(230,255,0,${
      0.6 * glowIntensity
    })`;
  }

  // 🎯 カラオケスタイル：全文表示＋ハイライト制御
  const renderCharacters = () => {
    if (!subtitle.characters || subtitle.characters.length === 0) {
      // フォールバック：通常の文字列表示
      // 🎯 Guard B: レンダリング直前に句読点を完全除去
      const sanitizedText = cleanText(subtitle.text, true);
      
      // 空文字の場合はレンダリングしない
      if (!sanitizedText || sanitizedText.trim() === '') {
        return null;
      }
      
      return <span>{sanitizedText}</span>;
    }

    return subtitle.characters.map((charData, index) => {
      const charStartFrame = charData.startFrame;
      const charEndFrame = charData.endFrame;
      
      // 🎯 Guard B: レンダリング直前に句読点を完全除去
      const cleanedChar = cleanText(charData.char, true);
      
      // 🎯 句読点判定：句読点単体の場合はレンダリング自体をスキップ
      if (!cleanedChar || cleanedChar.trim() === '' || isPunctuation(charData.char, true)) {
        return null;
      }
      
      // 🎯 カラオケスタイル v3.0 判定：
      // - 現在発音中の文字のみ → ゴールド (#FFD700) + スケール1.2倍
      // - それ以外の全文字 → 白（半透明）で常に表示
      const isActive = frame >= charStartFrame && frame <= charEndFrame; // 現在発音中
      
      // 📱 文字のスケールアニメーション（発音中のみ1.2倍）
      const charLocalFrame = frame - charStartFrame;
      const charScale = isActive
        ? interpolate(
            charLocalFrame,
            [0, 2, charEndFrame - charStartFrame],
            [1, 1.2, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
          )
        : 1;

      // 🎨 カラオケスタイル v3.0 の色分け
      let charColor: string;
      let charShadow: string;
      
      if (isActive) {
        // 現在発音中 → ゴールド＋強いグロー
        charColor = "#FFD700"; // ゴールド
        charShadow = "0px 0px 20px rgba(255,215,0,1), 0px 0px 40px rgba(255,215,0,0.8)";
      } else {
        // 未発音・発音済み → 白（半透明）で常に表示
        charColor = "rgba(255, 255, 255, 0.6)"; // 白（半透明）
        charShadow = "0px 0px 8px rgba(255,255,255,0.3)";
      }

      return (
        <span
          key={`${subtitle.id}-char-${index}`}
          style={{
            display: "inline-block",
            whiteSpace: "pre", // 空白文字の崩れ防止
            transform: `scale(${charScale})`,
            transformOrigin: "center center",
            color: charColor,
            textShadow: charShadow,
            transition: "color 0.05s ease-out",
            padding: "0 2px", // 文字間の微調整
          }}
        >
          {cleanedChar}
        </span>
      );
    });
  };

  return (
    <div
      style={{
        position: "absolute",
        bottom: "15%", // 📱 SNSのUI（キャプション等）と被らない位置に調整
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        padding: "0 7.5%", // 📱 左右15%のセーフゾーンを確保（両側7.5%ずつ）
        opacity,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "85%", // 📱 最大幅を制限してセーフゾーンを確保
          display: "flex",
          flexDirection: "row",
          flexWrap: "wrap", // 📱 自動折り返しを有効化
          justifyContent: "center",
          alignItems: "center",
          rowGap: "12px", // 📱 2行になった際の間隔
          textAlign: "center",
          fontSize: "4.5rem", // 📱 スマートフォンでの最適サイズ
          fontWeight: 900,
          textShadow: "0px 4px 12px rgba(0, 0, 0, 0.7)" + additionalShadow,
          fontFamily: "'Montserrat', 'Noto Sans JP', sans-serif",
          letterSpacing: "2px",
          lineHeight: 1.3,
        }}
      >
        {renderCharacters()}
      </div>
    </div>
  );
};

/**
 * レガシー字幕コンポーネント（後方互換性）
 */
const LegacySubtitle: React.FC<{
  subtitle: LegacySubtitle;
  frame: number;
}> = ({ subtitle, frame }) => {
  const fps = 30;
  const startFrame = subtitle.startFrame;
  const endFrame = subtitle.endFrame;
  
  // 🎯 Guard B: レガシーフォーマットでも句読点を除去
  const text = cleanText(subtitle.text, true);

  // 字幕内での進行度（0-1）
  const localFrame = frame - startFrame;
  const totalFrames = endFrame - startFrame;
  const progress = Math.max(0, Math.min(1, localFrame / totalFrames));

  // シンプルなフェードインアニメーション
  const opacity = interpolate(progress, [0, 0.1, 0.9, 1], [0, 1, 1, 0.8]);
  
  // 空文字の場合はレンダリングしない
  if (!text || text.trim() === '') {
    return null;
  }

  return (
    <div
      style={{
        position: "absolute",
        top: "50%",
        left: 0,
        right: 0,
        transform: "translateY(-50%)",
        display: "flex",
        justifyContent: "center",
        padding: "0 40px",
        opacity,
      }}
    >
      <span
        style={{
          color: "#FFFFFF",
          fontSize: 75,
          fontWeight: "bold",
          textAlign: "center",
          textShadow:
            "0px 0px 10px rgba(230,255,0,0.8), 0px 0px 30px rgba(230,255,0,0.5)",
          fontFamily: "'Orbitron', 'Noto Sans JP', sans-serif",
          whiteSpace: "pre-wrap",
          letterSpacing: "4px",
          lineHeight: 1.4,
        }}
      >
        {text}
      </span>
    </div>
  );
};

/**
 * メインコンポジション
 */
export const AudioDrivenComposition: React.FC = () => {
  const frame = useCurrentFrame();

  // 現在表示すべき字幕を取得
  let currentSubtitle: Subtitle | LegacySubtitle | null = null;
  let isCharacterLevel = false;

  if (videoData && videoData.subtitles && videoData.metadata.syncMode === "character-level") {
    // 🎯 新フォーマット（1文字単位同期）
    currentSubtitle =
      videoData.subtitles.find(
        (sub: Subtitle) => frame >= sub.startFrame && frame <= sub.endFrame
      ) || null;
    isCharacterLevel = true;
  } else if (legacySubtitles.length > 0) {
    // レガシーフォーマット
    currentSubtitle =
      legacySubtitles.find(
        (sub: LegacySubtitle) => frame >= sub.startFrame && frame <= sub.endFrame
      ) || null;
  }

  // 音声設定
  const narrationVolume = videoData?.audio?.narration?.volume || 4.0;
  const bgmVolume = videoData?.audio?.bgm?.volume || 0.08;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Google Fonts の読み込み */}
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@900&family=Orbitron:wght@700&family=Noto+Sans+JP:wght@900&display=swap');`}
      </style>

      {/* ナレーション音声 */}
      <Audio src={staticFile("audio.mp3")} volume={narrationVolume} />

      {/* BGM */}
      <Audio src={staticFile("bg-music.mp3")} volume={bgmVolume} loop />

      {/* 背景画像 */}
      <img
        src={staticFile("bg-cyber.png")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          position: "absolute",
        }}
        alt="Background"
      />

      {/* ロゴ */}
      <div
        style={{
          position: "absolute",
          top: 10,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
        }}
      >
        <img
          src={staticFile("logo.png")}
          style={{
            width: "80%",
            height: "auto",
            objectFit: "contain",
          }}
          alt="Logo"
        />
      </div>

      {/* 字幕表示（1文字単位の超精密同期 or レガシー） */}
      {currentSubtitle && isCharacterLevel && (
        <KaraokeSubtitle
          subtitle={currentSubtitle as Subtitle}
          frame={frame}
        />
      )}
      {currentSubtitle && !isCharacterLevel && (
        <LegacySubtitle
          subtitle={currentSubtitle as LegacySubtitle}
          frame={frame}
        />
      )}

      {/* デバッグ情報（開発時のみ） */}
      {videoData?.metadata.syncMode === "character-level" && (
        <div
          style={{
            position: "absolute",
            bottom: 10,
            right: 10,
            color: "#00FF00",
            fontSize: 12,
            fontFamily: "monospace",
            backgroundColor: "rgba(0,0,0,0.7)",
            padding: "5px 10px",
            borderRadius: 5,
          }}
        >
          🎯 Character-Level Sync | Frame: {frame}
        </div>
      )}
    </AbsoluteFill>
  );
};
