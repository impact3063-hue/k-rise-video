#!/usr/bin/env node
/**
 * K-RISE Local Webhook Server
 * 
 * Receives webhook triggers from Cloudflare Workers
 * and initiates local Remotion rendering
 * 
 * Usage: node scripts/webhook-server.mjs
 * Expose via ngrok: ngrok http 3000
 */

import { createServer } from 'http';
import { spawn } from 'child_process';
import { writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PORT = process.env.PORT || 3000;
const VIDEO_DATA_PATH = resolve(__dirname, '../public/video-data-master.json');

/**
 * HTTP Server
 */
const server = createServer(async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  // Handle OPTIONS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  // Only accept POST to /webhook
  if (req.method !== 'POST' || req.url !== '/webhook') {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found' }));
    return;
  }
  
  try {
    // Parse request body
    let body = '';
    for await (const chunk of req) {
      body += chunk.toString();
    }
    
    const payload = JSON.parse(body);
    console.log('\n🔔 Webhook received:', {
      action: payload.action,
      source: payload.source,
      timestamp: payload.timestamp
    });
    
    // Validate payload
    if (payload.action !== 'render_video') {
      throw new Error(`Unknown action: ${payload.action}`);
    }
    
    if (!payload.data || !payload.data.subtitles) {
      throw new Error('Invalid video data payload');
    }
    
    // Save video data to local file
    console.log('💾 Saving video data to:', VIDEO_DATA_PATH);
    writeFileSync(VIDEO_DATA_PATH, JSON.stringify(payload.data, null, 2));
    console.log('✅ Video data saved');
    
    // Respond immediately (don't wait for rendering)
    res.writeHead(202, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'accepted',
      message: 'Rendering started',
      timestamp: new Date().toISOString()
    }));
    
    // Start rendering in background
    console.log('🎬 Starting render pipeline...\n');
    startRenderPipeline();
    
  } catch (error) {
    console.error('❌ Webhook error:', error.message);
    res.writeHead(400, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      error: error.message,
      timestamp: new Date().toISOString()
    }));
  }
});

/**
 * Start rendering pipeline in background
 */
function startRenderPipeline() {
  const renderProcess = spawn('node', ['scripts/render-and-upload.mjs'], {
    cwd: resolve(__dirname, '..'),
    stdio: 'inherit',
    shell: true
  });
  
  renderProcess.on('error', (error) => {
    console.error('❌ Render process error:', error);
  });
  
  renderProcess.on('exit', (code) => {
    if (code === 0) {
      console.log('\n✅ Render pipeline completed successfully');
    } else {
      console.error(`\n❌ Render pipeline failed with code ${code}`);
    }
  });
}

/**
 * Start server
 */
server.listen(PORT, () => {
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('🎬 K-RISE Webhook Server Started');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`📍 Listening on http://localhost:${PORT}`);
  console.log(`🔗 Webhook endpoint: http://localhost:${PORT}/webhook`);
  console.log('\n💡 Expose via ngrok:');
  console.log(`   ngrok http ${PORT}`);
  console.log('\n⏳ Waiting for webhook triggers...\n');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Shutting down webhook server...');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});
