/**
 * 🛡️ K-RISE 動画量産パイプライン バリデーションゲート
 *
 * public/video-data-master.json と public/audio.mp3 の「1対1一致」を
 * レンダリング前に強制検証する。違反があれば exit 1 でレンダリングを停止。
 *
 * チェック項目:
 *   [1] 音声1対1一致    : audio.mp3 実長 vs metadata.duration/totalFrames（許容 ±1フレーム）
 *   [2] 字幕カバレッジ  : ナレーション再生中の字幕空白が閾値(2秒)超ならエラー
 *   [3] 文字TS整合      : characters[] と text の1文字一致・フレーム単調増加・親範囲内
 *   [4] CTA整合         : CTA表示区間と音声区間の関係検査
 *   [5] 構造スキーマ    : 必須キーの欠落検知
 *
 * 使い方: node scripts/validate-video-data.mjs
 */

import { readFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const MASTER = join(ROOT, "public", "video-data-master.json");

// ---- 設定（許容値）----
const FRAME_TOLERANCE = 1; // 音声長の許容ズレ（フレーム）
const MAX_SUBTITLE_GAP_SEC = 2.0; // ナレーション中に許容される字幕空白（秒）

const errors = [];
const warnings = [];
const err = (m) => errors.push(m);
const warn = (m) => warnings.push(m);

// ---- データ読み込み ----
const data = JSON.parse(readFileSync(MASTER, "utf-8"));
const fps = data?.metadata?.fps ?? 30;

// ---- [5] 構造スキーマ検査 ----
for (const key of ["version", "metadata", "content", "audio", "subtitles"]) {
  if (!(key in data)) err(`[構造] ルート必須キー「${key}」が欠落しています`);
}
for (const key of ["fps", "duration", "totalFrames", "syncMode"]) {
  if (data.metadata?.[key] === undefined)
    err(`[構造] metadata.${key} が欠落しています`);
}
(data.subtitles ?? []).forEach((s, i) => {
  const label = `subtitles[${i}](id=${s.id ?? "?"})`;
  for (const key of ["id", "text", "startFrame", "endFrame", "characters", "style"]) {
    if (s[key] === undefined) err(`[構造] ${label}: 必須キー「${key}」が欠落`);
  }
  if (s.startFrame >= s.endFrame)
    err(`[構造] ${label}: startFrame(${s.startFrame}) >= endFrame(${s.endFrame})`);
});

// ---- [1] 音声1対1一致 ----
const audioFile = join(ROOT, "public", data.audio?.narration?.file ?? "audio.mp3");
let audioSec = null;
if (!existsSync(audioFile)) {
  err(`[音声] ナレーションファイルが存在しません: ${audioFile}`);
} else {
  try {
    audioSec = parseFloat(
      execFileSync("ffprobe", [
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        audioFile,
      ]).toString().trim()
    );
  } catch {
    warn("[音声] ffprobe が利用できないため音声長の実測をスキップしました（チェック[1]は不完全）");
  }
}
if (audioSec !== null) {
  const audioFrames = Math.round(audioSec * fps);
  const declaredDur = data.audio?.narration?.duration;
  const metaDur = data.metadata?.duration;
  const metaFrames = data.metadata?.totalFrames;

  const durDiffFrames = Math.abs(audioSec - declaredDur) * fps;
  if (durDiffFrames > FRAME_TOLERANCE)
    err(
      `[音声1対1] audio.narration.duration(${declaredDur}s) と audio.mp3 実測(${audioSec.toFixed(3)}s) が ` +
      `${(declaredDur - audioSec).toFixed(3)}s (約${Math.round(durDiffFrames)}フレーム) 乖離 — 音声とJSONの世代が不一致です`
    );
  if (metaFrames < audioFrames - FRAME_TOLERANCE)
    err(
      `[音声1対1] metadata.totalFrames(${metaFrames}) が音声実長(${audioFrames}フレーム)より短く、音声が尻切れになります`
    );
  if (Math.abs(metaDur * fps - metaFrames) > FRAME_TOLERANCE)
    err(`[音声1対1] metadata.duration(${metaDur}s) と totalFrames(${metaFrames}) が矛盾（fps=${fps}）`);
}

// ---- [2] 字幕カバレッジ ----
const subs = [...(data.subtitles ?? [])].sort((a, b) => a.startFrame - b.startFrame);
const narrationEndFrame = audioSec !== null
  ? Math.round(audioSec * fps)
  : (data.metadata?.totalFrames ?? 0);
let cursor = 0;
const maxGapFrames = MAX_SUBTITLE_GAP_SEC * fps;
for (const s of subs) {
  const gap = s.startFrame - cursor;
  if (gap > maxGapFrames && cursor < narrationEndFrame) {
    err(
      `[カバレッジ] frame ${cursor}〜${s.startFrame} に ${(gap / fps).toFixed(1)}秒の字幕空白 — ` +
      `ナレーション再生中(〜frame ${narrationEndFrame})に字幕データが存在しません（許容: ${MAX_SUBTITLE_GAP_SEC}秒）`
    );
  }
  cursor = Math.max(cursor, s.endFrame);
}
if (narrationEndFrame - cursor > maxGapFrames)
  err(
    `[カバレッジ] frame ${cursor}〜${narrationEndFrame}（音声終了）まで ${((narrationEndFrame - cursor) / fps).toFixed(1)}秒の字幕空白があります`
  );

// ---- [3] 文字タイムスタンプ整合 ----
for (const s of subs) {
  const label = `subtitle(id=${s.id})`;
  const chars = s.characters ?? [];
  if (chars.length === 0) continue; // CTA等の非カラオケはスキップ（[4]で検査）
  const joined = chars.map((c) => c.char).join("");
  const textNorm = (s.text ?? "").replace(/\s/g, "");
  if (joined !== textNorm)
    err(`[文字TS] ${label}: characters連結「${joined}」と text「${textNorm}」が1対1一致しません`);
  let prevEnd = -Infinity;
  chars.forEach((c, i) => {
    if (c.startFrame < prevEnd)
      err(`[文字TS] ${label}: characters[${i}]「${c.char}」のstartFrame(${c.startFrame})が前の文字の終端(${prevEnd})より前です（時系列逆行）`);
    if (c.startFrame >= c.endFrame)
      err(`[文字TS] ${label}: characters[${i}]「${c.char}」startFrame >= endFrame`);
    if (c.startFrame < s.startFrame || c.endFrame > s.endFrame)
      err(`[文字TS] ${label}: characters[${i}]「${c.char}」(${c.startFrame}-${c.endFrame})が親字幕範囲(${s.startFrame}-${s.endFrame})を逸脱`);
    prevEnd = c.endFrame;
  });
}

// ---- [4] CTA整合 ----
const ctas = subs.filter((s) => s.style?.type === "cta");
for (const cta of ctas) {
  if (audioSec !== null && cta.startFrame >= narrationEndFrame) {
    warn(
      `[CTA] id=${cta.id}: CTA表示(frame ${cta.startFrame}〜)はナレーション終了(frame ${narrationEndFrame})後の無音区間です — ` +
      `音声で読み上げられないテキストが表示されます。台本との一致を確認してください`
    );
  }
  const scriptNorm = (data.content?.script?.original ?? "").replace(/\s/g, "");
  const ctaNorm = (cta.text ?? "").replace(/\s/g, "");
  if (scriptNorm && !scriptNorm.includes(ctaNorm.slice(0, 8)))
    warn(`[CTA] id=${cta.id}: CTAテキストが content.script.original に含まれていません — 音声との乖離の可能性`);
}

// ---- 台本カバレッジ（世代ズレの決定的検知）----
const scriptNorm = (data.content?.script?.original ?? "").replace(/\s/g, "");
const karaokeText = subs
  .filter((s) => s.style?.type !== "cta")
  .map((s) => (s.text ?? "").replace(/\s/g, ""))
  .join("");
if (scriptNorm && audioSec !== null) {
  const scriptSecEstimate = audioSec; // 音声=台本の読み上げ
  const karaokeSec = subs
    .filter((s) => s.style?.type !== "cta")
    .reduce((acc, s) => acc + (s.endFrame - s.startFrame) / fps, 0);
  if (karaokeSec < scriptSecEstimate * 0.5)
    err(
      `[世代整合] カラオケ字幕の総尺(${karaokeSec.toFixed(1)}s)が音声実長(${scriptSecEstimate.toFixed(1)}s)の半分未満 — ` +
      `音声(mp3)とJSONが別世代の台本である可能性が極めて高い（字幕:「${karaokeText}」）`
    );
}

// ---- 結果出力 ----
console.log("═".repeat(70));
console.log("🛡️  K-RISE バリデーションゲート — video-data-master.json × audio.mp3");
console.log("═".repeat(70));
if (warnings.length) {
  console.log(`\n⚠️  警告 ${warnings.length}件:`);
  warnings.forEach((w, i) => console.log(`  W${i + 1}. ${w}`));
}
if (errors.length) {
  console.log(`\n❌ エラー ${errors.length}件 — レンダリングを停止します:`);
  errors.forEach((e, i) => console.log(`  E${i + 1}. ${e}`));
  console.log("\n🚫 型崩れデータを検知したため exit 1。データ世代を揃えてから再実行してください。");
  process.exit(1);
}
console.log("\n✅ 全チェック通過 — レンダリングを許可します。");
process.exit(0);
