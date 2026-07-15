import { AbsoluteFill, staticFile, useCurrentFrame, Audio, interpolate } from "remotion";

export interface SubtitleData {
  text: string;
  startFrame: number;
  endFrame: number;
  style?: "normal" | "bullet" | "cta";
}

export interface KpopAuditionPattern1Props {
  subtitles?: SubtitleData[];
  audioFile?: string;
  bgMusicFile?: string;
  bgImageFile?: string;
  logoFile?: string;
}

export const KpopAuditionPattern1: React.FC<KpopAuditionPattern1Props> = ({
  subtitles = [],
  audioFile = "audio.mp3",
  bgMusicFile = "bg-music.mp3",
  bgImageFile = "bg-cyber.png",
  logoFile = "logo.png",
}) => {
  const frame = useCurrentFrame();

  // 現在のフレームに対応する字幕を取得
  const currentSubtitle = subtitles.find(
    (sub) => frame >= sub.startFrame && frame <= sub.endFrame
  );

  // フェードイン効果のみ
  const opacity = currentSubtitle
    ? interpolate(
        frame - currentSubtitle.startFrame,
        [0, 10],
        [0, 1],
        {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }
      )
    : 0;

  const displayText = currentSubtitle ? currentSubtitle.text : "";

  // 字幕スタイル設定（画面中央やや下、フォントサイズ76px）
  const getTextStyle = () => {
    return {
      color: "#FFFACD",
      fontWeight: "bold" as const,
      textAlign: "center" as const,
      fontFamily: "'Noto Sans JP', sans-serif",
      whiteSpace: "pre-wrap" as const,
      wordWrap: "break-word" as const,
      lineHeight: 1.4,
      fontSize: 76,
      textShadow: "3px 3px 6px rgba(0,0,0,0.9), -2px -2px 4px rgba(0,0,0,0.8), 2px 2px 5px rgba(0,0,0,0.7)",
      letterSpacing: "1.5px",
      opacity,
      padding: "20px 30px",
      backgroundColor: "rgba(0,0,0,0.65)",
      borderRadius: "12px",
      maxWidth: "90%",
    };
  };

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@700;900&display=swap');`}
      </style>

      {/* 音声ファイル */}
      <Audio src={staticFile(audioFile)} volume={4.0} />

      {/* バックグラウンドBGM */}
      <Audio src={staticFile(bgMusicFile)} volume={0.08} loop />

      {/* 背景画像 */}
      <img
        src={staticFile(bgImageFile)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          position: "absolute",
        }}
        alt="background"
      />

      {/* ロゴマーク */}
      <div
        style={{
          position: "absolute",
          top: 10,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          zIndex: 10,
        }}
      >
        <img
          src={staticFile(logoFile)}
          style={{
            width: "80%",
            height: "auto",
            objectFit: "contain",
          }}
          alt="logo"
        />
      </div>

      {/* 字幕表示（画面中央やや下、top: 55%） */}
      <div
        style={{
          position: "absolute",
          top: "55%",
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: "0 20px",
          zIndex: 5,
        }}
      >
        <span style={getTextStyle()}>{displayText}</span>
      </div>
    </AbsoluteFill>
  );
};
