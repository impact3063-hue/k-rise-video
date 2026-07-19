/**
 * 🎬 Remotion動画レンダリング ＆ R2アップロード統合スクリプト
 * RIIZE Character-Level Sync動画を生成してR2にアップロード
 */

import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { createRequire } from "module";
import path from "path";
import {
  uploadVideoToR2,
  getR2ConfigFromEnv,
  logR2UploadResult,
} from "../src/utils/r2Upload";

const require = createRequire(import.meta.url);

async function renderAndUpload() {
  console.log("🎬 RIIZE Character-Level Sync 動画レンダリング開始...\n");

  try {
    // 1. Remotionプロジェクトをバンドル
    console.log("📦 Step 1: Remotionプロジェクトをバンドル中...");
    const bundleLocation = await bundle({
      entryPoint: path.resolve("./src/index.ts"),
      webpackOverride: (config) => config,
    });
    console.log("✅ バンドル完了\n");

    // 2. コンポジション情報を取得
    console.log("🎯 Step 2: コンポジション情報を取得中...");
    const composition = await selectComposition({
      serveUrl: bundleLocation,
      id: "AudioDrivenVideo", // または "KpopAuditionPattern1"
      inputProps: {},
    });
    console.log(`✅ コンポジション取得完了: ${composition.id}\n`);

    // 3. 動画をレンダリング
    const outputPath = path.resolve("./output.mp4");
    console.log("🎥 Step 3: 動画レンダリング中...");
    console.log(`   出力先: ${outputPath}`);

    await renderMedia({
      composition,
      serveUrl: bundleLocation,
      codec: "h264",
      outputLocation: outputPath,
      inputProps: {},
      onProgress: ({ progress }) => {
        const percentage = (progress * 100).toFixed(1);
        process.stdout.write(`\r   進捗: ${percentage}%`);
      },
    });
    console.log("\n✅ レンダリング完了\n");

    // 4. R2にアップロード
    console.log("☁️ Step 4: Cloudflare R2にアップロード中...");
    const r2Config = getR2ConfigFromEnv();

    if (!r2Config) {
      console.error("❌ R2設定が見つかりません。.envファイルを確認してください。");
      process.exit(1);
    }

    const uploadResult = await uploadVideoToR2(outputPath, r2Config);
    logR2UploadResult(uploadResult);

    if (uploadResult.success) {
      console.log("🎉 すべての処理が完了しました！");
      console.log(`\n📺 動画URL: ${uploadResult.publicUrl}`);
      console.log("\n💡 このURLをLINE Botやその他のプラットフォームで使用できます。\n");
    } else {
      console.error("❌ R2アップロードに失敗しました。");
      process.exit(1);
    }
  } catch (error) {
    console.error("\n❌ エラーが発生しました:", error);
    process.exit(1);
  }
}

// スクリプト実行
renderAndUpload();
