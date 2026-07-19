#!/usr/bin/env node
/**
 * Download video-data-master.json from R2 Storage
 * 
 * Used by GitHub Actions to fetch the latest video data
 * before rendering
 */

import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3';
import { writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config({ path: resolve(__dirname, '../.env') });

const CONFIG = {
  r2: {
    accountId: process.env.CLOUDFLARE_ACCOUNT_ID || 'ce43db3e02cd26f119444ba2b8bbceed',
    accessKeyId: process.env.R2_ACCESS_KEY_ID,
    secretAccessKey: process.env.R2_SECRET_ACCESS_KEY,
    bucketName: process.env.R2_BUCKET_NAME || 'k-rise-video-storage',
    endpoint: `https://${process.env.CLOUDFLARE_ACCOUNT_ID || 'ce43db3e02cd26f119444ba2b8bbceed'}.r2.cloudflarestorage.com`
  },
  outputPath: resolve(__dirname, '../public/video-data-master.json')
};

async function downloadVideoData() {
  console.log('📥 Downloading video data from R2...');
  
  if (!CONFIG.r2.accessKeyId || !CONFIG.r2.secretAccessKey) {
    throw new Error('R2 credentials not configured. Set R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY');
  }
  
  const s3Client = new S3Client({
    region: 'auto',
    endpoint: CONFIG.r2.endpoint,
    credentials: {
      accessKeyId: CONFIG.r2.accessKeyId,
      secretAccessKey: CONFIG.r2.secretAccessKey,
    },
  });
  
  try {
    const response = await s3Client.send(new GetObjectCommand({
      Bucket: CONFIG.r2.bucketName,
      Key: 'public/video-data-master.json',
    }));
    
    const bodyContents = await streamToString(response.Body);
    const videoData = JSON.parse(bodyContents);
    
    // Validate data
    if (!videoData.subtitles || !videoData.metadata) {
      throw new Error('Invalid video data structure');
    }
    
    // Save to local file
    writeFileSync(CONFIG.outputPath, JSON.stringify(videoData, null, 2));
    
    console.log('✅ Video data downloaded successfully');
    console.log(`   Subtitles: ${videoData.subtitles.length}`);
    console.log(`   Duration: ${videoData.metadata.duration}s`);
    console.log(`   Saved to: ${CONFIG.outputPath}`);
    
  } catch (error) {
    if (error.name === 'NoSuchKey') {
      console.error('❌ Video data not found in R2. Run /ai 動画更新 first.');
    } else {
      console.error('❌ Download failed:', error.message);
    }
    throw error;
  }
}

/**
 * Convert stream to string
 */
async function streamToString(stream) {
  const chunks = [];
  for await (const chunk of stream) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString('utf-8');
}

// Run download
downloadVideoData().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
