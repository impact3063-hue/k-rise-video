import { Composition } from "remotion";
import { KpopAuditionPattern1 } from "./KpopAuditionPattern1";
import subtitlesPattern1 from "../public/kpop-audition-pattern1.json";

export const KpopAuditionRoot: React.FC = () => {
  // パターン1の動画の長さを計算（最後の字幕のendFrame + 余白30フレーム）
  const lastSubtitlePattern1 = subtitlesPattern1[subtitlesPattern1.length - 1];
  const durationPattern1 = lastSubtitlePattern1 ? lastSubtitlePattern1.endFrame + 30 : 480;

  return (
    <>
      {/* パターン1: 衝撃の事実訴求型 */}
      <Composition
        id="KpopAuditionPattern1"
        component={KpopAuditionPattern1}
        durationInFrames={durationPattern1}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          subtitles: subtitlesPattern1,
          audioFile: "audio.mp3",
          bgMusicFile: "bg-music.mp3",
          bgImageFile: "bg-cyber.png",
          logoFile: "logo.png",
        }}
      />
    </>
  );
};

export default KpopAuditionRoot;
