/**
 * 🎬 K-RISE TikTok Video 3 - Minimal Hardcoded Segments
 * 完全固定字幕システム - 単語切れ・画面混同の100%強制修正
 *
 * 特徴:
 * - 完全静的データ駆動：4つの固定セグメントのみ
 * - \n による明示的な改行制御（単語の途中で改行しない）
 * - シンプルなフェードイン/アウトアニメーション
 * - 自動折り返し処理を完全廃止
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
interface SubtitleStyle {
  type: string;
}

interface Subtitle {
  id: string;
  text: string;
  startFrame: number;
  endFrame: number;
  style: SubtitleStyle;
}

interface VideoData {
  version: string;
  metadata: {
    projectId: string;
    title: string;
    fps: number;
    duration: number;
    totalFrames: number;
  };
  audio: {
    narration: {
      file: string;
      volume: number;
    };
    bgm: {
      file: string;
      volume: number;
      loop: boolean;
    };
  };
  subtitles: Subtitle[];
}

// データのインポート（Single Source of Truth）
import videoDataMaster from "../public/video-data-master.json";

const videoData = videoDataMaster as VideoData;

/**
 * 🎯 Simple Subtitle Component (Minimal Version)
 * 完全固定版：\n による明示的な改行のみ使用
 */
const SimpleSubtitle: React.FC<{
  subtitle: Subtitle;
  frame: number;
}> = ({ subtitle, frame }) => {
  const startFrame = subtitle.startFrame;
  const endFrame = subtitle.endFrame;

  // 字幕内での進行度
  const localFrame = frame - startFrame;
  const totalFrames = Math.max(1, endFrame - startFrame);

  // 字幕全体のフェード
  const fadeInFrames = Math.min(8, Math.floor(totalFrames * 0.2));
  const fadeOutStart = Math.max(fadeInFrames + 1, totalFrames - Math.min(8, Math.floor(totalFrames * 0.2)));
  const fadeOutEnd = Math.max(fadeOutStart + 1, totalFrames);

  const opacity = interpolate(
    localFrame,
    [0, fadeInFrames, fadeOutStart, fadeOutEnd],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // スケールアニメーション
  const scale = interpolate(
    localFrame,
    [0, fadeInFrames],
    [0.95, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 🎯 \n で行を分割（完全固定）
  const lines = useMemo(() => {
    return subtitle.text.split('\n');
  }, [subtitle.text]);

  // 字幕全体の表示判定
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
        padding: "0 5%",
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "90%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          gap: "8px",
          textAlign: "center",
        }}
      >
        {lines.map((lineText, lineIndex) => (
          <div
            key={`${subtitle.id}-line-${lineIndex}`}
            style={{
              display: "block",
              width: "100%",
              whiteSpace: "nowrap",
              fontSize: "clamp(2.4rem, 7vw, 4.5rem)",
              fontWeight: 900,
              fontFamily: "'Montserrat', 'Noto Sans JP', sans-serif",
              letterSpacing: "2px",
              color: "#FFFFFF",
              textShadow:
                "0px 0px 20px rgba(255,215,0,0.8), " +
                "0px 0px 40px rgba(255,215,0,0.6), " +
                "0px 6px 15px rgba(0,0,0,0.95), " +
                "3px 3px 8px rgba(0,0,0,0.9)",
              WebkitTextStroke: "1.5px rgba(255,215,0,0.3)",
            }}
          >
            {lineText}
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * メインコンポジション
 */
export const KRiseTikTok3: React.FC = () => {
  const frame = useCurrentFrame();

  // 現在表示すべき字幕を取得
  const currentSubtitle = useMemo(() => {
    return videoData.subtitles.find(
      (sub: Subtitle) => frame >= sub.startFrame && frame < sub.endFrame
    );
  }, [frame]);

  // 音声設定
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

      {/* 字幕表示（完全固定セグメント） */}
      {currentSubtitle && (
        <SimpleSubtitle subtitle={currentSubtitle} frame={frame} />
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
        🎯 K-RISE TikTok 3 | Frame: {frame} | Minimal Hardcoded
      </div>
    </AbsoluteFill>
  );
};
