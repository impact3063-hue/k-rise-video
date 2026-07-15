import { Composition } from "remotion";
import { MyComposition } from "./Composition";
import { KpopAuditionPattern1 } from "./KpopAuditionPattern1";
import { AudioDrivenComposition } from "./AudioDrivenComposition";
import subtitles from "../public/sample-video.json";
import subtitlesPattern1 from "../public/kpop-audition-pattern1.json";

export const Root: React.FC = () => {
  const lastSubtitle = subtitles[subtitles.length - 1];
  const durationInFrames = lastSubtitle ? lastSubtitle.endFrame + 30 : 720;

  // K-POPオーディション パターン1の動画の長さ（15秒 = 450フレーム）
  const durationPattern1 = 450;

  return (
    <>
      {/* 🎬 Audio-Driven Composition（推奨：世界標準のデータ駆動型） */}
      <Composition
        id="AudioDrivenComposition"
        component={AudioDrivenComposition}
        durationInFrames={durationInFrames}
        fps={30}
        width={1080}
        height={1920}
      />

      {/* オリジナルのコンポジション */}
      <Composition
        id="MyComp"
        component={MyComposition}
        durationInFrames={durationInFrames}
        fps={30}
        width={1080}
        height={1920}
      />

      {/* K-POPオーディション パターン1: BTSプロデューサー直接審査型 */}
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

export const RemotionRoot = Root;

export default Root;
