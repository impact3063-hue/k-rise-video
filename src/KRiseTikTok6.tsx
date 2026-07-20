/**
 * 🎬 K-RISE TikTok Video 6 - Final Master Version
 * CapCut風フレーズ表示：完全版（テキスト重複バグ修正済み）
 * 
 * データソース: video-data-capcut-style.json
 * 
 * 特徴:
 * - KRiseTikTok5の優れたデザインを100%継承
 * - テキスト重複バグを完全修正（1フレーズずつ確実に切り替え）
 * - 句点「。」を含まないクリーンな表示
 * - 1.1倍ポップインアニメーション
 * - フェードイン/アウト効果
 * - ゴールドグロー強調
 * - 15秒間の完全な音声カバレッジ
 */

import React, { useMemo } from "react";
import {
  AbsoluteFill,
  staticFile,
  useCurrentFrame,
  Audio,
  interpolate,
  Img,
  spring,
  useVideoConfig,
} from "remotion";

// 型定義
interface Phrase {
  text: string;
  startFrame: number;
  endFrame: number;
}

interface VisualEffects {
  background: {
    kenBurns: {
      enabled: boolean;
      zoomFrom: number;
      zoomTo: number;
      duration: number;
    };
    neonPulse: {
      enabled: boolean;
      color: string;
      intensity: number;
      speed: number;
    };
  };
  phraseAnimation: {
    popInScale: number;
    fadeInFrames: number;
    fadeOutFrames: number;
    glowColor: string;
    glowIntensity: number;
  };
}

interface CTAConfig {
  text: string;
  startFrame: number;
  endFrame: number;
  showArrow: boolean;
}

interface VideoData {
  version: string;
  metadata: {
    projectId: string;
    title: string;
    fps: number;
    duration: number;
    totalFrames: number;
    displayMode: string;
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
  phrases: Phrase[];
  visualEffects: VisualEffects;
  cta: CTAConfig;
}

// データのインポート
import videoDataCapCut from "../public/video-data-capcut-style.json";

const videoData = videoDataCapCut as VideoData;

/**
 * 🎯 下向き矢印アニメーション（CTA用）
 */
const DownArrowAnimation: React.FC<{ frame: number; startFrame: number }> = ({
  frame,
  startFrame,
}) => {
  const { fps } = useVideoConfig();
  const localFrame = frame - startFrame;

  const bounce = spring({
    frame: localFrame % 30,
    fps,
    config: {
      damping: 10,
      stiffness: 200,
    },
  });

  const translateY = interpolate(bounce, [0, 1], [0, 15]);
  const opacity = interpolate(localFrame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: "15%",
        left: "50%",
        transform: `translateX(-50%) translateY(${translateY}px)`,
        opacity,
      }}
    >
      <svg
        width="60"
        height="60"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 4L12 20M12 20L18 14M12 20L6 14"
          stroke="#FFD700"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="drop-shadow(0 0 10px rgba(255,215,0,0.8))"
        />
      </svg>
    </div>
  );
};

/**
 * 🎯 CapCut風フレーズ表示コンポーネント
 */
const PhraseDisplay: React.FC<{
  phrase: Phrase;
  frame: number;
  effects: VisualEffects["phraseAnimation"];
}> = ({ phrase, frame, effects }) => {
  const localFrame = frame - phrase.startFrame;
  const totalFrames = phrase.endFrame - phrase.startFrame;

  // フェードイン
  const fadeIn = interpolate(
    localFrame,
    [0, effects.fadeInFrames],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // フェードアウト
  const fadeOut = interpolate(
    localFrame,
    [totalFrames - effects.fadeOutFrames, totalFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const opacity = Math.min(fadeIn, fadeOut);

  // ポップインスケール
  const popInScale = interpolate(
    localFrame,
    [0, effects.fadeInFrames],
    [effects.popInScale, 1.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // グロー強度
  const glowIntensity = effects.glowIntensity;

  return (
    <div
      style={{
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: `translate(-50%, -50%) scale(${popInScale})`,
        opacity,
      }}
    >
      <div
        style={{
          fontSize: "clamp(3.5rem, 10vw, 6rem)",
          fontWeight: 900,
          fontFamily: "'Montserrat', 'Noto Sans JP', sans-serif",
          color: effects.glowColor,
          textShadow: `
            0px 0px ${40 * glowIntensity}px rgba(255,215,0,1.0),
            0px 0px ${60 * glowIntensity}px rgba(255,215,0,0.8),
            0px 0px ${80 * glowIntensity}px rgba(255,215,0,0.6),
            0px 8px 20px rgba(0,0,0,0.95)
          `,
          WebkitTextStroke: "2px rgba(255,215,0,0.6)",
          letterSpacing: "3px",
          textAlign: "center",
          whiteSpace: "nowrap",
          padding: "0 20px",
        }}
      >
        {phrase.text}
      </div>
    </div>
  );
};

/**
 * メインコンポジション
 */
export const KRiseTikTok6: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 現在表示すべきフレーズを取得（重複防止ロジック強化）
  const currentPhrase = useMemo(() => {
    // フレーズを優先度順にソート（後のフレーズが優先）
    const sortedPhrases = [...videoData.phrases].sort(
      (a, b) => a.startFrame - b.startFrame
    );

    // 現在のフレームに該当するフレーズを検索
    // 重複がある場合は最後に開始したフレーズを優先
    let matchedPhrase: Phrase | undefined;
    
    for (const phrase of sortedPhrases) {
      // 厳密な範囲チェック: startFrame <= frame < endFrame
      if (frame >= phrase.startFrame && frame < phrase.endFrame) {
        matchedPhrase = phrase;
      }
    }

    return matchedPhrase;
  }, [frame]);

  // Ken Burnsエフェクト
  const kenBurnsEnabled = videoData.visualEffects.background.kenBurns.enabled;
  const kenBurnsZoom = kenBurnsEnabled
    ? interpolate(
        frame,
        [0, durationInFrames],
        [
          videoData.visualEffects.background.kenBurns.zoomFrom,
          videoData.visualEffects.background.kenBurns.zoomTo,
        ],
        { extrapolateRight: "clamp" }
      )
    : 1.0;

  // ネオンパルスエフェクト
  const neonPulseEnabled = videoData.visualEffects.background.neonPulse.enabled;
  const neonOpacity = neonPulseEnabled
    ? videoData.visualEffects.background.neonPulse.intensity *
      (0.5 + 0.5 * Math.sin(frame * 0.1 * videoData.visualEffects.background.neonPulse.speed))
    : 0;

  // CTA表示判定
  const showCTA = frame >= videoData.cta.startFrame && frame < videoData.cta.endFrame;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Google Fonts の読み込み */}
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@900&family=Noto+Sans+JP:wght@700;900&display=swap');`}
      </style>

      {/* ナレーション音声 */}
      <Audio src={staticFile("audio.mp3")} volume={videoData.audio.narration.volume} />

      {/* BGM */}
      <Audio src={staticFile("bg-music.mp3")} volume={videoData.audio.bgm.volume} loop />

      {/* 背景画像（Ken Burnsエフェクト付き） */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          overflow: "hidden",
        }}
      >
        <Img
          src={staticFile("bg-cyber.png")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${kenBurnsZoom})`,
            transformOrigin: "center center",
          }}
          alt="Background"
        />
      </div>

      {/* ネオンパルスオーバーレイ */}
      {neonPulseEnabled && (
        <div
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            background: `radial-gradient(circle at center, ${videoData.visualEffects.background.neonPulse.color}33 0%, transparent 70%)`,
            opacity: neonOpacity,
            pointerEvents: "none",
          }}
        />
      )}

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

      {/* フレーズ表示（CapCut風） - 重複防止ロジック適用 */}
      {currentPhrase && (
        <PhraseDisplay
          phrase={currentPhrase}
          frame={frame}
          effects={videoData.visualEffects.phraseAnimation}
        />
      )}

      {/* CTAサブテキスト */}
      {showCTA && (
        <>
          <div
            style={{
              position: "absolute",
              bottom: "25%",
              left: "50%",
              transform: "translateX(-50%)",
              fontSize: "clamp(1.2rem, 3.5vw, 2rem)",
              fontWeight: 700,
              fontFamily: "'Noto Sans JP', sans-serif",
              color: "#FFFACD",
              textShadow:
                "0px 0px 15px rgba(255,215,0,0.6), 0px 4px 10px rgba(0,0,0,0.8)",
              opacity: interpolate(
                frame - videoData.cta.startFrame,
                [0, 15],
                [0, 1],
                { extrapolateRight: "clamp" }
              ),
              whiteSpace: "nowrap",
            }}
          >
            {videoData.cta.text}
          </div>

          {/* 下向き矢印 */}
          {videoData.cta.showArrow && (
            <DownArrowAnimation frame={frame} startFrame={videoData.cta.startFrame} />
          )}
        </>
      )}

      {/* デバッグ情報 */}
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
        🎯 K-RISE Final Master | Frame: {frame} | Phrase: {currentPhrase?.text || "None"}
      </div>
    </AbsoluteFill>
  );
};
