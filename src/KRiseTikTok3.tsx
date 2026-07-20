/**
 * 🔒 LOCKED MASTER TEMPLATE - DO NOT MODIFY WITHOUT CREATING NEW FILE
 *
 * このファイルは K-RISE 初号機マスター動画テンプレート（コミット 3a60dc2）です。
 *
 * 🚨 以下の仕様は変更禁止（IMMUTABLE）:
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * ✓ whiteSpace: "nowrap"     - 自動折り返し完全禁止
 * ✓ flexWrap: "nowrap"       - 改行制御（\n のみ許可）
 * ✓ 1文字ゴールド発光: #FFD700 - アクティブ文字の色
 * ✓ 拡大率: 1.1倍            - アクティブ文字のスケール
 * ✓ 4セグメント固定構造      - video-data-master.json と完全同期
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 *
 * 📝 変更が必要な場合の対応:
 * 1. このファイルを複製して新しいコンポーネントを作成
 *    例: KRiseTikTok4.tsx, KRiseTikTok5.tsx
 * 2. 新しいデータファイルを作成
 *    例: video-data-v2.json
 * 3. src/Root.tsx で新しいコンポーネントを登録
 *
 * ⚠️ このファイルの直接編集は、マスター動画の再現性を破壊します。
 *
 * 🎬 K-RISE TikTok Video 3 - Character-Level Gold Sync Animation
 * 完全固定字幕システム + 1文字ずつゴールドハイライト演出
 *
 * 特徴:
 * - 完全静的データ駆動：4つの固定セグメントのみ
 * - \n による明示的な改行制御（単語の途中で改行しない）
 * - 1文字ずつゴールドに光り拡大するカラオケアニメーション
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
interface CharacterTiming {
  char: string;
  startFrame: number;
  endFrame: number;
}

interface SubtitleStyle {
  type: string;
}

interface Subtitle {
  id: string;
  text: string;
  startFrame: number;
  endFrame: number;
  style: SubtitleStyle;
  characters?: CharacterTiming[];
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
 * 🎯 Character-Level Gold Sync Subtitle Component
 * 完全固定版：\n による明示的な改行 + 1文字ずつゴールドハイライト
 */
const CharacterSyncSubtitle: React.FC<{
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

  // 🎯 文字ごとのタイミング情報を取得
  const characterTimings = subtitle.characters || [];

  // 各文字が現在アクティブかどうかを判定する関数
  const isCharacterActive = (charTiming: CharacterTiming): boolean => {
    return frame >= charTiming.startFrame && frame < charTiming.endFrame;
  };

  // 字幕全体の表示判定
  if (frame < startFrame || frame >= endFrame) {
    return null;
  }

  // 文字インデックスを追跡
  let charIndex = 0;

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
              display: "flex",
              flexDirection: "row",
              flexWrap: "nowrap",
              justifyContent: "center",
              alignItems: "center",
              width: "100%",
              whiteSpace: "nowrap",
            }}
          >
            {lineText.split('').map((char, charInLineIndex) => {
              const currentCharTiming = characterTimings[charIndex];
              const isActive = currentCharTiming && isCharacterActive(currentCharTiming);
              charIndex++;

              // アクティブな文字のスタイル
              const charColor = isActive ? "#FFD700" : "#FFFFFF";
              const charScale = isActive ? 1.1 : 1.0;
              const charGlow = isActive
                ? "0px 0px 30px rgba(255,215,0,1.0), " +
                  "0px 0px 50px rgba(255,215,0,0.8), " +
                  "0px 6px 15px rgba(0,0,0,0.95)"
                : "0px 0px 20px rgba(255,215,0,0.8), " +
                  "0px 0px 40px rgba(255,215,0,0.6), " +
                  "0px 6px 15px rgba(0,0,0,0.95), " +
                  "3px 3px 8px rgba(0,0,0,0.9)";

              return (
                <span
                  key={`${subtitle.id}-line-${lineIndex}-char-${charInLineIndex}`}
                  style={{
                    display: "inline-block",
                    fontSize: "clamp(2.4rem, 7vw, 4.5rem)",
                    fontWeight: 900,
                    fontFamily: "'Montserrat', 'Noto Sans JP', sans-serif",
                    letterSpacing: "2px",
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

      {/* 字幕表示（1文字ずつゴールドハイライト） */}
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
        🎯 K-RISE TikTok 3 | Frame: {frame} | Character-Level Gold Sync
      </div>
    </AbsoluteFill>
  );
};
