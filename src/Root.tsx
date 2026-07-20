import { Composition } from "remotion";
import { MyComposition } from "./Composition";
import { KpopAuditionPattern1 } from "./KpopAuditionPattern1";
import { AudioDrivenComposition } from "./AudioDrivenComposition";
import { KRiseTikTok3 } from "./KRiseTikTok3";
import { KRiseTikTok3Enhanced } from "./KRiseTikTok3Enhanced";
import { KRiseTikTok4 } from "./KRiseTikTok4";
import { KRiseTikTok5 } from "./KRiseTikTok5";
import { KRiseTikTok6 } from "./KRiseTikTok6";
import subtitles from "../public/sample-video.json";
import subtitlesPattern1 from "../public/kpop-audition-pattern1.json";
import videoDataMaster from "../public/video-data-master.json";
import videoDataV2 from "../public/video-data-v2-optimized.json";
import videoDataCapCut from "../public/video-data-capcut-style.json";

export const Root: React.FC = () => {
  const lastSubtitle = subtitles[subtitles.length - 1];
  const durationInFrames = lastSubtitle ? lastSubtitle.endFrame + 30 : 720;

  // K-POPオーディション パターン1の動画の長さ（15秒 = 450フレーム）
  const durationPattern1 = 450;

  // K-RISE TikTok 3の動画の長さ（video-data-master.jsonから取得）
  const durationTikTok3 = (videoDataMaster as any).metadata?.totalFrames || 450;

  // K-RISE TikTok 4の動画の長さ（video-data-v2-optimized.jsonから取得）
  const durationTikTok4 = (videoDataV2 as any).metadata?.totalFrames || 420;

  // K-RISE TikTok 5の動画の長さ（video-data-capcut-style.jsonから取得）
  const durationTikTok5 = (videoDataCapCut as any).metadata?.totalFrames || 420;

  // K-RISE TikTok 6の動画の長さ（video-data-capcut-style.jsonから取得）
  const durationTikTok6 = (videoDataCapCut as any).metadata?.totalFrames || 450;

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

      {/* ✨ K-RISE TikTok 4: Optimized CTA Version */}
      {/* 最適化版：Ken Burnsエフェクト + 矢印アニメーション + 強化CTA */}
      <Composition
        id="KRiseTikTok4"
        component={KRiseTikTok4}
        durationInFrames={durationTikTok4}
        fps={30}
        width={1080}
        height={1920}
      />

      {/* 🎯 K-RISE TikTok 5: CapCut Style Phrase Display */}
      {/* CapCut風：音声完全連動の短いフレーズ表示 */}
      <Composition
        id="KRiseTikTok5"
        component={KRiseTikTok5}
        durationInFrames={durationTikTok5}
        fps={30}
        width={1080}
        height={1920}
      />

      {/* 🏆 K-RISE TikTok 6: Final Master Version */}
      {/* 最終完成版：テキスト重複バグ修正 + 完全音声カバレッジ */}
      <Composition
        id="KRiseTikTok6"
        component={KRiseTikTok6}
        durationInFrames={durationTikTok6}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};

export const RemotionRoot = Root;

export default Root;
