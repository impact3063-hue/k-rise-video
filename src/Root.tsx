import { Composition } from "remotion";
import { MyComposition } from "./Composition";
import { KpopAuditionPattern1 } from "./KpopAuditionPattern1";
import { AudioDrivenComposition } from "./AudioDrivenComposition";
import { KRiseTikTok3 } from "./KRiseTikTok3";
import { KRiseTikTok3Enhanced } from "./KRiseTikTok3Enhanced";
import subtitles from "../public/sample-video.json";
import subtitlesPattern1 from "../public/kpop-audition-pattern1.json";
import videoDataMaster from "../public/video-data-master.json";

export const Root: React.FC = () => {
  const lastSubtitle = subtitles[subtitles.length - 1];
  const durationInFrames = lastSubtitle ? lastSubtitle.endFrame + 30 : 720;

  // K-POPオーディション パターン1の動画の長さ（15秒 = 450フレーム）
  const durationPattern1 = 450;

  // K-RISE TikTok 3の動画の長さ（video-data-master.jsonから取得）
  const durationTikTok3 = (videoDataMaster as any).metadata?.totalFrames || 450;

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

      {/* 🎯 K-RISE TikTok 3: 1文字単位の超精密同期（Character-Level Sync） */}
      <Composition
        id="KRiseTikTok3"
        component={KRiseTikTok3}
        durationInFrames={durationTikTok3}
        fps={30}
        width={1080}
        height={1920}
      />

      {/* 🔥 K-RISE TikTok 3 Enhanced: RIIZE Dance Challenge Edition */}
      {/* 強化版：ゴールドグロー5層 + ラスト3秒固定LINE CTA */}
      <Composition
        id="KRiseTikTok3Enhanced"
        component={KRiseTikTok3Enhanced}
        durationInFrames={450}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};

export const RemotionRoot = Root;

export default Root;
