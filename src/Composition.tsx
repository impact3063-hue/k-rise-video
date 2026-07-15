import { AbsoluteFill, staticFile, useCurrentFrame, Audio } from "remotion";
import subtitles from "../public/sample-video.json"; 

export const MyComposition = () => {
  const frame = useCurrentFrame();

  const currentSubtitle = subtitles.find(
    (sub) => frame >= sub.startFrame && frame <= sub.endFrame
  );

  const displayText = currentSubtitle ? currentSubtitle.text : "";

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght=700&family=Noto+Sans+JP:wght=900&display=swap');`}
      </style>

      {/* 声優さんの音声 */}
      <Audio src={staticFile("audio.mp3")} volume={4.0} />

      {/* バックグラウンドBGM */}
      <Audio src={staticFile("bg-music.mp3")} volume={0.08} loop />

      {/* 背景画像 */}
      <img 
        src={staticFile("bg-cyber.png")} 
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          position: "absolute"
        }} 
      />

      {/* ロゴマーク */}
      <div style={{
        position: "absolute",
        top: 10,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center"
      }}>
        <img 
          src={staticFile("logo.png")} 
          style={{
            width: "80%",
            height: "auto",
            objectFit: "contain"
          }} 
        />
      </div>

      {/* テロップ表示 */}
      <div style={{
        position: "absolute",
        top: "50%",
        left: 0,
        right: 0,
        transform: "translateY(-50%)",
        display: "flex",
        justifyContent: "center",
        padding: "0 40px"
      }}>
        <span style={{
          color: "#fff",
          fontSize: 75,
          fontWeight: "bold",
          textAlign: "center",
          textShadow: "0px 0px 10px rgba(230,255,0,0.8), 0px 0px 30px rgba(230,255,0,0.5), 0px 0px 5px rgba(0,0,0,1)", 
          fontFamily: "'Orbitron', 'Noto Sans JP', sans-serif",
          whiteSpace: "pre-wrap",
          letterSpacing: "4px"
        }}>
          {displayText}
        </span>
      </div>
    </AbsoluteFill>
  );
};