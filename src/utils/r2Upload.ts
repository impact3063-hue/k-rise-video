/**
 * 🚀 Cloudflare R2 Upload Utility
 * R2バケットへの動画アップロード＆パブリックURL生成
 */

import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { readFileSync } from "fs";
import { basename } from "path";

interface R2UploadConfig {
  accountId: string;
  apiToken: string;
  bucketName: string;
}

interface R2UploadResult {
  success: boolean;
  publicUrl?: string;
  error?: string;
  uploadedAt?: string;
  fileSize?: number;
}

/**
 * R2クライアントの初期化
 */
function createR2Client(config: R2UploadConfig): S3Client {
  return new S3Client({
    region: "auto",
    endpoint: `https://${config.accountId}.r2.cloudflarestorage.com`,
    credentials: {
      accessKeyId: config.apiToken,
      secretAccessKey: config.apiToken,
    },
  });
}

/**
 * 動画ファイルをR2にアップロード
 * @param filePath - アップロードするファイルのパス
 * @param config - R2設定
 * @returns アップロード結果（パブリックURL含む）
 */
export async function uploadVideoToR2(
  filePath: string,
  config: R2UploadConfig
): Promise<R2UploadResult> {
  try {
    console.log(`📤 R2アップロード開始: ${filePath}`);

    // ファイル読み込み
    const fileBuffer = readFileSync(filePath);
    const fileName = basename(filePath);
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const objectKey = `videos/${timestamp}_${fileName}`;

    // R2クライアント作成
    const r2Client = createR2Client(config);

    // アップロード実行
    const uploadCommand = new PutObjectCommand({
      Bucket: config.bucketName,
      Key: objectKey,
      Body: fileBuffer,
      ContentType: "video/mp4",
      // パブリックアクセス設定（R2のカスタムドメイン経由でアクセス可能）
      Metadata: {
        uploadedAt: new Date().toISOString(),
        source: "k-rise-video-remotion",
      },
    });

    await r2Client.send(uploadCommand);

    // パブリックURL生成
    // Note: R2のパブリックURLは、カスタムドメインまたはR2.devドメインを使用
    const publicUrl = `https://${config.bucketName}.r2.dev/${objectKey}`;

    console.log(`✅ R2アップロード成功: ${publicUrl}`);

    return {
      success: true,
      publicUrl,
      uploadedAt: new Date().toISOString(),
      fileSize: fileBuffer.length,
    };
  } catch (error) {
    console.error("❌ R2アップロードエラー:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/**
 * 環境変数からR2設定を読み込み
 */
export function getR2ConfigFromEnv(): R2UploadConfig | null {
  const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
  const apiToken = process.env.CLOUDFLARE_API_TOKEN;
  const bucketName = process.env.R2_BUCKET_NAME;

  if (!accountId || !apiToken || !bucketName) {
    console.warn("⚠️ R2設定が不完全です。.envファイルを確認してください。");
    return null;
  }

  return {
    accountId,
    apiToken,
    bucketName,
  };
}

/**
 * R2アップロード結果をログ出力
 */
export function logR2UploadResult(result: R2UploadResult): void {
  console.log("\n" + "=".repeat(60));
  console.log("📊 R2アップロード結果");
  console.log("=".repeat(60));

  if (result.success) {
    console.log("✅ ステータス: 成功");
    console.log(`🔗 パブリックURL: ${result.publicUrl}`);
    console.log(`📅 アップロード日時: ${result.uploadedAt}`);
    console.log(
      `📦 ファイルサイズ: ${((result.fileSize || 0) / 1024 / 1024).toFixed(2)} MB`
    );
  } else {
    console.log("❌ ステータス: 失敗");
    console.log(`⚠️ エラー: ${result.error}`);
  }

  console.log("=".repeat(60) + "\n");
}
