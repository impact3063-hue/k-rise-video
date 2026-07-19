#!/usr/bin/env node
/**
 * K-RISE Auto Render & Upload Script
 * 
 * This script:
 * 1. Renders video using Remotion
 * 2. Uploads to R2 storage
 * 3. Posts video URL to Discord
 * 
 * Triggered by: Cloudflare Workers webhook
 * Environment: Local machine or GitHub Actions
 */

import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables
dotenv.config({ path: resolve(__dirname, '../.env') });

// Configuration
const CONFIG = {
  compositionId: 'KRiseTikTok3',
  outputPath: resolve(__dirname, '../out/auto-render.mp4'),
  videoDataPath: resolve(__dirname, '../public/video-data-master.json'),
  
  // R2 Configuration
  r2: {
    accountId: process.env.CLOUDFLARE_ACCOUNT_ID || 'ce43db3e02cd26f119444ba2b8bbceed',
    accessKeyId: process.env.R2_ACCESS_KEY_ID,
    secretAccessKey: process.env.R2_SECRET_ACCESS_KEY,
    bucketName: process.env.R2_BUCKET_NAME || 'k-rise-video-storage',
    endpoint: process.env.R2_ENDPOINT || `https://${process.env.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com`
  },
  
  // Discord Configuration
  discord: {
    webhookUrl: process.env.DISCORD_WEBHOOK_URL
  }
};

/**
 * Main rendering pipeline
 */
async function main() {
  console.log('🎬 K-RISE Auto Render Pipeline Started');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  try {
    // Step 1: Validate video data
    console.log('\n📋 Step 1: Validating video data...');
    if (!existsSync(CONFIG.videoDataPath)) {
      throw new Error(`Video data not found: ${CONFIG.videoDataPath}`);
    }
    
    const videoData = JSON.parse(readFileSync(CONFIG.videoDataPath, 'utf-8'));
    console.log(`✅ Video data loaded: ${videoData.subtitles.length} subtitles, ${videoData.metadata.duration}s`);
    
    // Step 2: Bundle Remotion project
    console.log('\n📦 Step 2: Bundling Remotion project...');
    const bundleLocation = await bundle({
      entryPoint: resolve(__dirname, '../src/index.ts'),
      webpackOverride: (config) => config,
    });
    console.log(`✅ Bundle created: ${bundleLocation}`);
    
    // Step 3: Select composition
    console.log('\n🎯 Step 3: Selecting composition...');
    const composition = await selectComposition({
      serveUrl: bundleLocation,
      id: CONFIG.compositionId,
    });
    console.log(`✅ Composition selected: ${composition.id} (${composition.width}x${composition.height}, ${composition.fps}fps)`);
    
    // Step 4: Render video
    console.log('\n🎥 Step 4: Rendering video...');
    console.log(`   Output: ${CONFIG.outputPath}`);
    
    const startTime = Date.now();
    await renderMedia({
      composition,
      serveUrl: bundleLocation,
      codec: 'h264',
      outputLocation: CONFIG.outputPath,
      onProgress: ({ progress, renderedFrames, encodedFrames }) => {
        const percent = (progress * 100).toFixed(1);
        process.stdout.write(`\r   Progress: ${percent}% (${renderedFrames}/${composition.durationInFrames} frames)`);
      },
    });
    
    const renderTime = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`\n✅ Video rendered successfully in ${renderTime}s`);
    
    // Step 5: Upload to R2
    console.log('\n☁️  Step 5: Uploading to R2 storage...');
    const videoUrl = await uploadToR2(CONFIG.outputPath, videoData);
    console.log(`✅ Video uploaded: ${videoUrl}`);
    
    // Step 6: Post to Discord
    console.log('\n💬 Step 6: Posting to Discord...');
    await postToDiscord(videoUrl, videoData);
    console.log('✅ Discord notification sent');
    
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🎉 Pipeline completed successfully!');
    console.log(`📹 Video URL: ${videoUrl}`);
    
  } catch (error) {
    console.error('\n❌ Pipeline failed:', error.message);
    console.error(error.stack);
    
    // Send error notification to Discord
    if (CONFIG.discord.webhookUrl) {
      await fetch(CONFIG.discord.webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: `❌ **レンダリングエラー**\n\n\`\`\`\n${error.message}\n\`\`\``,
          username: 'K-RISE Render Bot'
        })
      });
    }
    
    process.exit(1);
  }
}

/**
 * Upload video to R2 storage
 */
async function uploadToR2(videoPath, videoData) {
  if (!CONFIG.r2.accessKeyId || !CONFIG.r2.secretAccessKey) {
    console.warn('⚠️  R2 credentials not configured, skipping upload');
    return 'file://' + videoPath;
  }
  
  const s3Client = new S3Client({
    region: 'auto',
    endpoint: CONFIG.r2.endpoint,
    credentials: {
      accessKeyId: CONFIG.r2.accessKeyId,
      secretAccessKey: CONFIG.r2.secretAccessKey,
    },
  });
  
  const videoBuffer = readFileSync(videoPath);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const key = `videos/auto-render-${timestamp}.mp4`;
  
  await s3Client.send(new PutObjectCommand({
    Bucket: CONFIG.r2.bucketName,
    Key: key,
    Body: videoBuffer,
    ContentType: 'video/mp4',
    Metadata: {
      'project-id': videoData.metadata.projectId,
      'duration': videoData.metadata.duration.toString(),
      'subtitle-count': videoData.subtitles.length.toString(),
      'generated-at': videoData.metadata.generatedAt,
    },
  }));
  
  // Return public URL (configure R2 custom domain if needed)
  return `https://pub-${CONFIG.r2.accountId}.r2.dev/${CONFIG.r2.bucketName}/${key}`;
}

/**
 * Post video to Discord
 */
async function postToDiscord(videoUrl, videoData) {
  if (!CONFIG.discord.webhookUrl) {
    console.warn('⚠️  Discord webhook not configured, skipping notification');
    return;
  }
  
  const message = {
    content: `🎬 **K-RISE 動画レンダリング完了**\n\n` +
             `📝 スクリプト: ${videoData.content.script.original.substring(0, 100)}...\n` +
             `🎬 字幕数: ${videoData.subtitles.length}行\n` +
             `⏱️ 動画長: ${videoData.metadata.duration.toFixed(1)}秒\n` +
             `📹 動画URL: ${videoUrl}\n\n` +
             `✨ RIIZE仕様準拠 | ゴールドグロー適用済み`,
    username: 'K-RISE Render Bot',
    avatar_url: 'https://cdn.discordapp.com/embed/avatars/5.png'
  };
  
  const response = await fetch(CONFIG.discord.webhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(message)
  });
  
  if (!response.ok) {
    throw new Error(`Discord API error: ${response.status}`);
  }
}

// Run the pipeline
main();
