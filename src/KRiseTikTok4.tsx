/**
 * 🎬 K-RISE TikTok Video 4 - Optimized CTA Version
 * 最適化版：強化されたCTA + Ken Burnsエフェクト + 矢印アニメーション
 * 
 * ベース: KRiseTikTok3.tsx (マスターテンプレート)
 * データソース: video-data-v2-optimized.json
 * 
 * 新機能:
 * - Ken Burnsエフェクト（背景のズームイン）
 * - ネオンパルスグラデーション
 * - CTAセクションの下向き矢印アニメーション
 * - サブテキスト表示（「プロフィール欄のリンクをタップ！」）
 * - 強化されたスケールアニメーション（1.15倍）
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
interface CharacterTiming {
  char: string;
  startFrame: number;
  endFrame: number;
}

interface SubtitleStyle {
  type: string;
  emphasis?: string;
  shake?: boolean;
  pulse?: boolean;
  showArrow?: boolean;
}

interface CTASubtext {
  text: string;
  startFrame: number;
  endFrame: number;
  position: string;
}

interface Subtitle {
  id: string;
  text: string;
  startFrame: number;
  endFrame: number;
  style: SubtitleStyle;
  characters?: CharacterTiming[];
  ctaSubtext?: CTASubtext;
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
  characterAnimation: {
    activeScale: number;
    activeDuration: number;
    glowIntensity: number;
  };
}

interface VideoData {
  version: string;
  metadata: {
    projectId: string;
    title: string;
    fps: number;
    duration: number;
    totalFrames: number;
    syncMode?: string;
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
  visualEffects?: VisualEffects;
}

// データのインポート
import videoDataV2 from "../public/video-data-v2-optimized.json";

const videoData = videoDataV2 as VideoData;

/**
 * 🎯 下向き矢印アニメーション（CTA用）
 */
const DownArrowAnimation: React.FC<{ frame: number; startFrame: number }> = ({
  frame,
  startFrame,
}) => {
  const { fps } = useVideoConfig();
  const localFrame = frame - startFrame;

  // バウンスアニメーション
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
 * 🎯 Character-Level Gold Sync Subtitle Component (Enhanced)
 */
const CharacterSyncSubtitle: React.FC<{
  subtitle: Subtitle;
  frame: number;
}> = ({ subtitle, frame }) => {
  const startFrame = subtitle.startFrame;
  const endFrame = subtitle.endFrame;

  const localFrame = frame - startFrame;
  const totalFrames = Math.max(1, endFrame - startFrame);

  // フェードアニメーション
  const fadeInFrames = Math.min(8, Math.floor(totalFrames * 0.2));
  const fadeOutStart = Math.max(
    fadeInFrames + 1,
    totalFrames - Math.min(8, Math.floor(totalFrames * 0.2))
  );
  const fadeOutEnd = Math.max(fadeOutStart + 1, totalFrames);

  const opacity = interpolate(
    localFrame,
    [0, fadeInFrames, fadeOutStart, fadeOutEnd],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // スケールアニメーション
  const scale = interpolate(localFrame, [0, fadeInFrames], [0.95, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // シェイクエフェクト（緊急性を強調）
  const shake =
    subtitle.style.shake && localFrame < 30
      ? Math.sin(localFrame * 0.5) * 2
      : 0;

  // パルスエフェクト（CTA用）
  const pulse = subtitle.style.pulse
    ? 1 + Math.sin(localFrame * 0.2) * 0.05
    : 1;

  // 行分割
  const lines = useMemo(() => {
    return subtitle.text.split("\n");
  }, [subtitle.text]);

  const characterTimings = subtitle.characters || [];

  const isCharacterActive = (charTiming: CharacterTiming): boolean => {
    return frame >= charTiming.startFrame && frame <= charTiming.endFrame;
  };

  if (frame < startFrame || frame >= endFrame) {
    return null;
  }

  let charIndex = 0;

  // 強化されたスケール値
  const enhancedScale =
    videoData.visualEffects?.characterAnimation.activeScale || 1.15;

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
        transform: `scale(${scale * pulse}) translateX(${shake}px)`,
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
              display: "flex",
              flexDirection: "row",
              flexWrap: "nowrap",
              justifyContent: "center",
              alignItems: "center",
              width: "100%",
              whiteSpace: "nowrap",
            }}
          >
            {lineText.split("").map((char, charInLineIndex) => {
              // 改行文字をスキップして次のタイミングデータを取得
              let currentCharTiming = characterTimings[charIndex];
              
              // 改行文字の場合、タイミングデータをスキップ
              while (currentCharTiming && currentCharTiming.char === "\n" && charIndex < characterTimings.length - 1) {
                charIndex++;
                currentCharTiming = characterTimings[charIndex];
              }
              
              const isActive =
                currentCharTiming &&
                currentCharTiming.char !== "\n" &&
                isCharacterActive(currentCharTiming);
              
              charIndex++;

              const charColor = isActive ? "#FFD700" : "#FFFFFF";
              const charScale = isActive ? enhancedScale : 1.0;
              const glowIntensity =
                videoData.visualEffects?.characterAnimation.glowIntensity || 1.2;

              const charGlow = isActive
                ? `0px 0px ${30 * glowIntensity}px rgba(255,215,0,1.0), ` +
                  `0px 0px ${50 * glowIntensity}px rgba(255,215,0,0.8), ` +
                  `0px 6px 15px rgba(0,0,0,0.95)`
                : "0px 0px 20px rgba(255,215,0,0.8), " +
                  "0px 0px 40px rgba(255,215,0,0.6), " +
                  "0px 6px 15px rgba(0,0,0,0.95), " +
                  "3px 3px 8px rgba(0,0,0,0.9)";

              // CTAセクション用のフォントサイズとレタースペーシング調整
              const isCTASection = subtitle.id === "seg4-cta";
              const fontSize = isCTASection
                ? "clamp(2.0rem, 5.5vw, 3.8rem)"
                : "clamp(2.4rem, 7vw, 4.5rem)";
              const letterSpacing = isCTASection ? "1px" : "2px";

              return (
                <span
                  key={`${subtitle.id}-line-${lineIndex}-char-${charInLineIndex}`}
                  style={{
                    display: "inline-block",
                    fontSize,
                    fontWeight: 900,
                    fontFamily: "'Montserrat', 'Noto Sans JP', sans-serif",
                    letterSpacing,
                    color: charColor,
                    textShadow: charGlow,
                    WebkitTextStroke: isActive
                      ? "1.5px rgba(255,215,0,0.6)"
                      : "1.5px rgba(255,215,0,0.3)",
                    transform: `scale(${charScale})`,
                    transition: "all 0.1s ease-out",
                  }}
                >
                  {char}
                </span>
              );
            })}
          </div>
        ))}
      </div>

      {/* CTAサブテキスト */}
      {subtitle.ctaSubtext && frame >= subtitle.ctaSubtext.startFrame && (
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
              frame - subtitle.ctaSubtext.startFrame,
              [0, 15],
              [0, 1],
              { extrapolateRight: "clamp" }
            ),
            whiteSpace: "nowrap",
          }}
        >
          {subtitle.ctaSubtext.text}
        </div>
      )}

      {/* 下向き矢印アニメーション */}
      {subtitle.style.showArrow && <DownArrowAnimation frame={frame} startFrame={startFrame} />}
    </div>
  );
};

/**
 * メインコンポジション
 */
export const KRiseTikTok4: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 現在表示すべき字幕を取得
  const currentSubtitle = useMemo(() => {
    return videoData.subtitles.find(
      (sub: Subtitle) => frame >= sub.startFrame && frame < sub.endFrame
    );
  }, [frame]);

  // Ken Burnsエフェクト
  const kenBurnsEnabled = videoData.visualEffects?.background.kenBurns.enabled;
  const kenBurnsZoom = kenBurnsEnabled
    ? interpolate(
        frame,
        [0, durationInFrames],
        [
          videoData.visualEffects!.background.kenBurns.zoomFrom,
          videoData.visualEffects!.background.kenBurns.zoomTo,
        ],
        { extrapolateRight: "clamp" }
      )
    : 1.0;

  // ネオンパルスエフェクト
  const neonPulseEnabled = videoData.visualEffects?.background.neonPulse.enabled;
  const neonOpacity = neonPulseEnabled
    ? videoData.visualEffects!.background.neonPulse.intensity *
      (0.5 + 0.5 * Math.sin(frame * 0.1 * videoData.visualEffects!.background.neonPulse.speed))
    : 0;

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
            background: `radial-gradient(circle at center, ${videoData.visualEffects!.background.neonPulse.color}33 0%, transparent 70%)`,
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

      {/* 字幕表示（強化版） */}
      {currentSubtitle && (
        <CharacterSyncSubtitle subtitle={currentSubtitle} frame={frame} />
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
        🎯 K-RISE TikTok 4 | Frame: {frame} | Optimized CTA v{videoData.version}
      </div>
    </AbsoluteFill>
  );
};
