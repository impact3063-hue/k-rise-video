/**
 * 🎬 K-RISE TikTok Video 3 Enhanced - RIIZE Dance Challenge Edition
 * 世界標準動画システム - 1文字単位の超精密同期 + LINE誘導強化版
 *
 * 特徴:
 * - Single Source of Truth: video-data-master.json から完全データ駆動
 * - 1文字単位の超精密同期（Character-level timestamp）
 * - 発音中の文字のみゴールド (#FFD700) + スケール1.2倍 + 強化グロー
 * - ラスト3秒固定のLINE CTA専用レイヤー（ミドル・バックエンド動線）
 * - パフォーマンス最適化：メモ化とフレーム単位判定
 */

import React, { useMemo } from "react";
import {
  AbsoluteFill,
  staticFile,
  useCurrentFrame,
  Audio,
  interpolate,
  Img,
  useVideoConfig,
} from "remotion";

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
  animation: string;
  type: string;
  fontFamily: string;
  fontSize: number;
  color: string;
  highlightColor: string;
  scaleFactor: number;
}

interface Subtitle {
  id: string;
  text: string;
  startFrame: number;
  endFrame: number;
  style: SubtitleStyle;
  characters: CharacterTimestamp[];
  duration: number;
  characterCount: number;
  metadata: {
    isKeyPhrase: boolean;
    characterCount: number;
    ctaType?: string;
    urgency?: string;
    emphasis?: string;
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
    syncMode: string;
    theme?: string;
    targetPlatform?: string[];
    conversionGoal?: string;
  };
  content: {
    script: {
      original: string;
      transcribed: string;
    };
    cta?: {
      message: string;
      startTime: number;
      duration: number;
      action: string;
      urgency: string;
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
  renderParams?: {
    fontMinRem: number;
    fontVw: number;
    fontMaxRem: number;
    glow: number;
    karaokeIntensity?: string;
  };
  subtitles: Subtitle[];
  analytics: {
    totalWords: number;
    averageWordDuration: number;
    speechRate: number;
    pauseCount: number;
    longestPause: number;
  };
  marketing?: {
    trend: string;
    targetAudience: string;
    conversionFunnel: string[];
    hashtags: string[];
  };
}

// データのインポート（Single Source of Truth）
import videoDataMaster from "../public/video-data-master.json";

const videoData = videoDataMaster as VideoData;

/**
 * 🎯 Enhanced Character-Level Karaoke Subtitle Component
 * 強化版：1文字単位の超精密同期 + ゴールドグロー強化
 */
const EnhancedCharacterLevelSubtitle: React.FC<{
  subtitle: Subtitle;
  frame: number;
}> = ({ subtitle, frame }) => {
  const startFrame = subtitle.startFrame;
  const endFrame = subtitle.endFrame;

  // 字幕内での進行度（0-1）
  const localFrame = frame - startFrame;
  const totalFrames = endFrame - startFrame;

  // 字幕全体のフェード（固定4フレーム — 行の長さに依存させず、発話開始と同時に即座に可視化）
  const opacity = interpolate(
    localFrame,
    [0, 4, totalFrames - 6, totalFrames],
    [0, 1, 1, 0.8],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 🎯 1文字単位のレンダリング（パフォーマンス最適化 + 強化グロー）
  const renderCharacters = useMemo(() => {
    if (!subtitle.characters || subtitle.characters.length === 0) {
      // フォールバック：通常の文字列表示
      return <span>{subtitle.text}</span>;
    }

    return subtitle.characters.map((charData, index) => {
      const charStartFrame = charData.startFrame;
      const charEndFrame = charData.endFrame;

      // 🎯 アクティブ判定：半開区間 [start, end) — 境界フレームでの2文字同時ゴールドを防止
      const isActive = frame >= charStartFrame && frame < charEndFrame;

      // 📱 文字のスケールアニメーション（発音中のみ1.2倍 — RIIZE仕様）
      const charLocalFrame = frame - charStartFrame;
      const charDur = Math.max(1, charEndFrame - charStartFrame);
      const charMid = Math.min(3, charDur / 2);
      
      // スケールファクターをデータから取得（デフォルト1.2）
      const targetScale = subtitle.style.scaleFactor || 1.2;
      
      const charScale = isActive
        ? interpolate(
            charLocalFrame,
            [0, charMid, charDur],
            [1, targetScale, targetScale],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
          )
        : 1;

      // 🎨 強化版カラオケスタイルの色分け
      let charColor: string;
      let charShadow: string;

      if (isActive) {
        // 現在発音中 → ゴールド (#FFD700) + 超強力グロー（RIIZE仕様）
        charColor = subtitle.style.highlightColor || "#FFD700";
        charShadow = `
          0px 0px 25px rgba(255,215,0,1),
          0px 0px 45px rgba(255,215,0,0.9),
          0px 0px 60px rgba(255,215,0,0.7),
          0px 4px 15px rgba(0,0,0,0.95),
          0px 0px 80px rgba(255,215,0,0.5)
        `.trim();
      } else {
        // 未発音・発音済み → 白（半透明）で常に表示
        charColor = "rgba(255, 255, 255, 0.65)";
        charShadow = "0px 0px 10px rgba(255,255,255,0.4), 0px 4px 12px rgba(0,0,0,0.8)";
      }

      return (
        <span
          key={`${subtitle.id}-char-${index}`}
          style={{
            display: "inline-block",
            whiteSpace: "pre",
            transform: `scale(${charScale})`,
            transformOrigin: "center center",
            color: charColor,
            textShadow: charShadow,
            padding: "0 2px",
            transition: "all 0.05s ease-out",
          }}
        >
          {charData.char}
        </span>
      );
    });
  }, [subtitle, frame]);

  // 字幕全体の表示判定（全Hooks実行後に判定 — Rules of Hooks遵守）
  if (frame < startFrame || frame > endFrame) {
    return null;
  }

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "0 5%",
        opacity,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "90%",
          display: "flex",
          flexDirection: "row",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "center",
          rowGap: "16px",
          textAlign: "center",
          fontSize: "clamp(3.2rem, 9.5vw, 6rem)",
          fontWeight: 900,
          fontFamily: "'Montserrat', 'Noto Sans JP', sans-serif",
          letterSpacing: "2px",
          lineHeight: 1.5,
        }}
      >
        {renderCharacters}
      </div>
    </div>
  );
};

/**
 * 🎯 Dedicated LINE CTA Component (Last 3 Seconds Fixed Layer)
 * ミドル・バックエンド動線担保：ラスト3秒固定のLINE誘導レイヤー
 */
const DedicatedLINECTA: React.FC<{
  frame: number;
  totalFrames: number;
  fps: number;
}> = ({ frame, totalFrames, fps }) => {
  // ラスト3秒（90フレーム @ 30fps）を自動計算
  const ctaDuration = 3.0; // 秒
  const ctaFrames = Math.floor(ctaDuration * fps);
  const ctaStartFrame = totalFrames - ctaFrames;

  // 表示判定
  if (frame < ctaStartFrame || frame > totalFrames) {
    return null;
  }

  // フェードイン + スケールアニメーション（強化版）
  const localFrame = frame - ctaStartFrame;
  const opacity = interpolate(localFrame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scale = interpolate(localFrame, [0, 20], [0.85, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // パルスアニメーション（注目度向上）
  const pulse = interpolate(
    localFrame % 30,
    [0, 15, 30],
    [1, 1.05, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        position: "absolute",
        top: "50%",
        left: 0,
        right: 0,
        transform: `translateY(-50%) scale(${scale * pulse})`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "0 5%",
        opacity,
        zIndex: 100,
      }}
    >
      {/* メインCTAボックス */}
      <div
        style={{
          color: "#FFFACD",
          fontSize: "clamp(2.2rem, 6.5vw, 4rem)",
          fontWeight: "bold",
          textAlign: "center",
          fontFamily: "'Noto Sans JP', sans-serif",
          whiteSpace: "pre-wrap",
          lineHeight: 1.6,
          textShadow: `
            3px 3px 8px rgba(0,0,0,0.95),
            -2px -2px 5px rgba(0,0,0,0.85),
            0px 0px 20px rgba(255,215,0,0.6),
            0px 0px 40px rgba(255,215,0,0.4)
          `.trim(),
          letterSpacing: "2px",
          padding: "25px 35px",
          backgroundColor: "rgba(0,0,0,0.75)",
          borderRadius: "16px",
          maxWidth: "90%",
          border: "3px solid rgba(255,215,0,0.8)",
          boxShadow: `
            0px 0px 30px rgba(255,215,0,0.5),
            inset 0px 0px 20px rgba(255,215,0,0.2)
          `.trim(),
        }}
      >
        続きはプロフィールURLから
        <br />
        <span
          style={{
            color: "#FFD700",
            fontSize: "1.2em",
            fontWeight: 900,
            textShadow: `
              0px 0px 15px rgba(255,215,0,1),
              0px 0px 30px rgba(255,215,0,0.8)
            `.trim(),
          }}
        >
          LINEへ登録
        </span>
        <br />
        <br />
        <span style={{ fontSize: "0.85em", color: "#FFF" }}>
          限定ダンスワークショップ
          <br />
          受付中
        </span>
      </div>

      {/* アクセント矢印（下向き） */}
      <div
        style={{
          marginTop: "15px",
          fontSize: "2.5rem",
          color: "#FFD700",
          animation: "bounce 1s infinite",
          textShadow: "0px 0px 20px rgba(255,215,0,0.8)",
        }}
      >
        ▼
      </div>
    </div>
  );
};

/**
 * 🎯 CTA (Call-to-Action) Component - Fallback
 * データ駆動型CTA（後方互換性）
 */
const CTASubtitle: React.FC<{
  subtitle: Subtitle;
  frame: number;
}> = ({ subtitle, frame }) => {
  const startFrame = subtitle.startFrame;
  const endFrame = subtitle.endFrame;

  // 表示判定
  if (frame < startFrame || frame > endFrame) {
    return null;
  }

  // フェードイン + スケールアニメーション
  const localFrame = frame - startFrame;
  const opacity = interpolate(localFrame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scale = interpolate(localFrame, [0, 15], [0.9, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top: "50%",
        left: 0,
        right: 0,
        transform: `translateY(-50%) scale(${Math.min(scale, 1.0)})`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "0 5%",
        opacity,
      }}
    >
      <div
        style={{
          color: "#FFFACD",
          fontSize: "clamp(2rem, 6vw, 3.5rem)",
          fontWeight: "bold",
          textAlign: "center",
          fontFamily: "'Noto Sans JP', sans-serif",
          whiteSpace: "pre-wrap",
          lineHeight: 1.5,
          textShadow:
            "3px 3px 6px rgba(0,0,0,0.9), -2px -2px 4px rgba(0,0,0,0.8), 2px 2px 5px rgba(0,0,0,0.7)",
          letterSpacing: "1.5px",
          padding: "20px 30px",
          backgroundColor: "rgba(0,0,0,0.65)",
          borderRadius: "12px",
          maxWidth: "90%",
        }}
      >
        {subtitle.text}
      </div>
    </div>
  );
};

/**
 * メインコンポジション - Enhanced Edition
 */
export const KRiseTikTok3Enhanced: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 現在表示すべき字幕を取得（パフォーマンス最適化：メモ化）
  const currentSubtitle = useMemo(() => {
    return videoData.subtitles.find(
      (sub: Subtitle) => frame >= sub.startFrame && frame <= sub.endFrame
    );
  }, [frame]);

  // 音声設定（Single Source of Truth）
  const narrationVolume = videoData.audio.narration.volume;
  const bgmVolume = videoData.audio.bgm.volume;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Google Fonts の読み込み */}
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@900&family=Noto+Sans+JP:wght@700;900&display=swap');
          
          @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
          }
        `}
      </style>

      {/* ナレーション音声 */}
      <Audio src={staticFile("audio.mp3")} volume={narrationVolume} />

      {/* BGM */}
      <Audio src={staticFile("bg-music.mp3")} volume={bgmVolume} loop />

      {/* 背景画像 */}
      <Img
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
        <Img
          src={staticFile("logo.png")}
          style={{
            width: "80%",
            height: "auto",
            objectFit: "contain",
          }}
          alt="Logo"
        />
      </div>

      {/* 字幕表示（1文字単位の超精密同期 - 強化版） */}
      {currentSubtitle && currentSubtitle.style.type === "cta" && (
        <CTASubtitle subtitle={currentSubtitle} frame={frame} />
      )}
      {currentSubtitle && currentSubtitle.style.type !== "cta" && (
        <EnhancedCharacterLevelSubtitle subtitle={currentSubtitle} frame={frame} />
      )}

      {/* 🎯 ラスト3秒固定のLINE CTA専用レイヤー（システム側で固定化） */}
      <DedicatedLINECTA
        frame={frame}
        totalFrames={durationInFrames}
        fps={fps}
      />

      {/* デバッグ情報（開発時のみ） */}
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
        🎯 K-RISE Enhanced | Frame: {frame} | RIIZE Challenge
      </div>
    </AbsoluteFill>
  );
};
