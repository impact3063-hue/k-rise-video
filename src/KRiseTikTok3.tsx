/**
 * 🎬 K-RISE TikTok Video 3 - Hardcoded Subtitle Segments
 * 完全固定字幕システム - 単語切れ・画面混同の100%強制修正
 *
 * 特徴:
 * - 完全静的データ駆動：4つの固定セグメントのみ
 * - \n による明示的な改行制御（単語の途中で改行しない）
 * - 1文字単位の超精密同期（Character-level timestamp）
 * - 発音中の文字のみゴールド (#FFD700) + スケール1.1倍
 * - BudouX自動分割ロジックを完全廃止
 */

import React, { useMemo } from "react";
import {
  AbsoluteFill,
  staticFile,
  useCurrentFrame,
  Audio,
  interpolate,
  Img,
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

// データのインポート（Single Source of Truth）
import videoDataMaster from "../public/video-data-master.json";

const videoData = videoDataMaster as VideoData;

/**
 * 🎯 Character-Level Karaoke Subtitle Component (Hardcoded Version)
 * 完全固定版：\n による明示的な改行のみ使用
 */
const CharacterLevelSubtitle: React.FC<{
  subtitle: Subtitle;
  frame: number;
}> = ({ subtitle, frame }) => {
  const startFrame = subtitle.startFrame;
  const endFrame = subtitle.endFrame;

  // 字幕内での進行度（0-1）
  const localFrame = frame - startFrame;
  const totalFrames = Math.max(1, endFrame - startFrame);

  // 字幕全体のフェード（安全なinterpolate - 配列の重複を防止）
  const fadeInFrames = Math.min(4, Math.floor(totalFrames * 0.3));
  const fadeOutStart = Math.max(fadeInFrames + 1, totalFrames - Math.min(6, Math.floor(totalFrames * 0.3)));
  const fadeOutEnd = Math.max(fadeOutStart + 1, totalFrames);

  const opacity = interpolate(
    localFrame,
    [0, fadeInFrames, fadeOutStart, fadeOutEnd],
    [0, 1, 1, 0.8],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 🎯 \n で行を分割（完全固定）
  const lines = useMemo(() => {
    return subtitle.text.split('\n');
  }, [subtitle.text]);

  // 🎯 1文字単位のレンダリング（完全固定版）
  const renderLines = useMemo(() => {
    let charIndex = 0;

    return lines.map((lineText, lineIndex) => {
      const lineChars: React.ReactNode[] = [];
      
      for (let i = 0; i < lineText.length; i++) {
        const char = lineText[i];
        const charData = subtitle.characters[charIndex];
        
        if (!charData) {
          // キャラクターデータがない場合はスキップ
          charIndex++;
          continue;
        }

        const charStartFrame = charData.startFrame;
        const charEndFrame = charData.endFrame;

        // 🎯 アクティブ判定：半開区間 [start, end) — 境界フレームでの2文字同時ゴールドを防止
        const isActive = frame >= charStartFrame && frame < charEndFrame;

        // 🔥 マーケティング最適化：初速3秒フック率爆発仕様
        // 発音中の1文字を「ゴールド + 1.1倍拡大 + パルス発光」で視線誘導
        const charLocalFrame = frame - charStartFrame;
        const charDur = Math.max(1, charEndFrame - charStartFrame);
        const charMid = Math.min(3, charDur / 2);
        
        // 🎯 1.1倍スケール + パルスアニメーション（発音中のみ）
        const charScale = isActive
          ? interpolate(
              charLocalFrame,
              [0, charMid, charDur],
              [1, 1.1, 1.1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            )
          : 1;

        // 🎨 カラオケスタイルの色分け
        let charColor: string;
        let charShadow: string;

        if (isActive) {
          // 🔥 現在発音中 → ゴールド (#FFD700) + 1.1倍拡大 + 強烈な発光エフェクト
          charColor = "#FFD700"; // ゴールド
          charShadow =
            "0px 0px 25px rgba(255,215,0,1), " +
            "0px 0px 50px rgba(255,215,0,0.9), " +
            "0px 0px 75px rgba(255,215,0,0.7), " +
            "0px 6px 15px rgba(0,0,0,0.95), " +
            "drop-shadow(0px 0px 30px rgba(255,215,0,1))";
        } else {
          // 未発音・発音済み → 白（半透明）で常に表示
          charColor = "rgba(255, 255, 255, 0.6)"; // 白（半透明）
          charShadow = "0px 0px 8px rgba(255,255,255,0.3), 0px 4px 12px rgba(0,0,0,0.7)";
        }

        lineChars.push(
          <span
            key={`${subtitle.id}-line-${lineIndex}-char-${i}`}
            style={{
              display: "inline-block",
              whiteSpace: "pre",
              transform: `scale(${charScale})`,
              transformOrigin: "center center",
              color: charColor,
              textShadow: charShadow,
              padding: "0 2px",
            }}
          >
            {char}
          </span>
        );

        charIndex++;
      }

      return (
        <div
          key={`${subtitle.id}-line-${lineIndex}`}
          style={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "center",
            alignItems: "center",
            width: "100%",
          }}
        >
          {lineChars}
        </div>
      );
    });
  }, [subtitle, frame, lines]);

  // 字幕全体の表示判定（全Hooks実行後に判定 — Rules of Hooks遵守）
  // 🎯 厳格なセグメント境界：半開区間 [startFrame, endFrame) でオーバーラップを完全防止
  if (frame < startFrame || frame >= endFrame) {
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
        padding: "0 8%",
        opacity,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "84%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          gap: "12px",
          textAlign: "center",
          fontSize: "clamp(2.2rem, 6.5vw, 4rem)",
          fontWeight: 900,
          fontFamily: "'Montserrat', 'Noto Sans JP', sans-serif",
          letterSpacing: "1.5px",
          lineHeight: 1.4,
          wordBreak: "keep-all",
          overflowWrap: "normal",
        }}
      >
        {renderLines}
      </div>
    </div>
  );
};

/**
 * 🎯 CTA (Call-to-Action) Component
 * 最後のCTA表示用
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
 * メインコンポジション
 */
export const KRiseTikTok3: React.FC = () => {
  const frame = useCurrentFrame();

  // 現在表示すべき字幕を取得（パフォーマンス最適化：メモ化）
  // 🎯 厳格なセグメント境界：半開区間 [startFrame, endFrame) でオーバーラップを完全防止
  const currentSubtitle = useMemo(() => {
    return videoData.subtitles.find(
      (sub: Subtitle) => frame >= sub.startFrame && frame < sub.endFrame
    );
  }, [frame]);

  // 音声設定（Single Source of Truth）
  const narrationVolume = videoData.audio.narration.volume;
  const bgmVolume = videoData.audio.bgm.volume;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Google Fonts の読み込み */}
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@900&family=Noto+Sans+JP:wght@700;900&display=swap');`}
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

      {/* 字幕表示（1文字単位の超精密同期） */}
      {currentSubtitle && currentSubtitle.style.type === "cta" && (
        <CTASubtitle subtitle={currentSubtitle} frame={frame} />
      )}
      {currentSubtitle && currentSubtitle.style.type !== "cta" && (
        <CharacterLevelSubtitle subtitle={currentSubtitle} frame={frame} />
      )}

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
        🎯 K-RISE TikTok 3 | Frame: {frame} | Hardcoded Segments
      </div>
    </AbsoluteFill>
  );
};
