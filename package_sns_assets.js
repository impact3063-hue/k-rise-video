/**
 * SNS投稿用アセット自動パッケージングスクリプト
 * 
 * 使用方法:
 * node package_sns_assets.js [version] [caption-file] [hashtags-file]
 * 
 * 例:
 * node package_sns_assets.js v3.2 tiktok_caption_updated.md tiktok_captions_hashtags.md
 * 
 * または引数なしで実行すると、デフォルト設定で実行されます:
 * node package_sns_assets.js
 */

const fs = require('fs');
const path = require('path');

// デフォルト設定
const DEFAULT_VERSION = 'v3.2';
const DEFAULT_CAPTION_FILE = 'tiktok_caption_updated.md';
const DEFAULT_HASHTAGS_FILE = 'tiktok_captions_hashtags.md';
const SOURCE_VIDEO = 'output.mp4';
const DIST_DIR = 'dist_sns_outputs';

/**
 * 日付文字列を生成 (YYYY-MM-DD形式)
 */
function getDateString() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * キャプションテキストをMarkdownファイルから抽出
 */
function extractCaptionFromMarkdown(filePath) {
  if (!fs.existsSync(filePath)) {
    console.warn(`⚠️  キャプションファイルが見つかりません: ${filePath}`);
    return '（キャプションファイルが見つかりませんでした）';
  }
  
  const content = fs.readFileSync(filePath, 'utf-8');
  
  // Markdownから実際のキャプションテキストを抽出
  // "## キャプション" または "# キャプション" セクションを探す
  const captionMatch = content.match(/##?\s*キャプション[^\n]*\n+([\s\S]*?)(?=\n##|\n#|$)/);
  if (captionMatch) {
    return captionMatch[1].trim();
  }
  
  // セクションが見つからない場合は、コードブロックやMarkdown記号を除去
  return content
    .replace(/```[\s\S]*?```/g, '')
    .replace(/^#+\s+.*/gm, '')
    .replace(/^\*\*.*\*\*$/gm, '')
    .trim();
}

/**
 * ハッシュタグをMarkdownファイルから抽出
 */
function extractHashtagsFromMarkdown(filePath) {
  if (!fs.existsSync(filePath)) {
    console.warn(`⚠️  ハッシュタグファイルが見つかりません: ${filePath}`);
    return '（ハッシュタグファイルが見つかりませんでした）';
  }
  
  const content = fs.readFileSync(filePath, 'utf-8');
  
  // Markdownからハッシュタグセクションを抽出
  const hashtagMatch = content.match(/##?\s*ハッシュタグ[^\n]*\n+([\s\S]*?)(?=\n##|\n#|$)/);
  if (hashtagMatch) {
    return hashtagMatch[1].trim();
  }
  
  // ハッシュタグ行を探す（#で始まる行）
  const lines = content.split('\n');
  const hashtagLines = lines.filter(line => line.trim().startsWith('#') && !line.trim().startsWith('##'));
  if (hashtagLines.length > 0) {
    return hashtagLines.join(' ').trim();
  }
  
  return content.trim();
}

/**
 * メイン処理
 */
function packageSNSAssets() {
  // コマンドライン引数を取得
  const args = process.argv.slice(2);
  const version = args[0] || DEFAULT_VERSION;
  const captionFile = args[1] || DEFAULT_CAPTION_FILE;
  const hashtagsFile = args[2] || DEFAULT_HASHTAGS_FILE;
  
  console.log('📦 SNS投稿用アセットのパッケージングを開始します...\n');
  
  // 日付とバージョンでフォルダ名を生成
  const dateStr = getDateString();
  const folderName = `${dateStr}_${version}`;
  const distPath = path.join(DIST_DIR, folderName);
  
  // dist_sns_outputsフォルダが存在しない場合は作成
  if (!fs.existsSync(DIST_DIR)) {
    fs.mkdirSync(DIST_DIR, { recursive: true });
    console.log(`✅ ${DIST_DIR}/ フォルダを作成しました`);
  }
  
  // 出力先フォルダを作成
  if (!fs.existsSync(distPath)) {
    fs.mkdirSync(distPath, { recursive: true });
    console.log(`✅ ${distPath}/ フォルダを作成しました`);
  } else {
    console.log(`ℹ️  ${distPath}/ フォルダは既に存在します（上書きします）`);
  }
  
  // 1. 動画ファイルをコピー
  if (fs.existsSync(SOURCE_VIDEO)) {
    const destVideo = path.join(distPath, 'output.mp4');
    fs.copyFileSync(SOURCE_VIDEO, destVideo);
    const stats = fs.statSync(destVideo);
    const fileSizeMB = (stats.size / (1024 * 1024)).toFixed(2);
    console.log(`✅ 動画ファイルをコピーしました: ${destVideo} (${fileSizeMB} MB)`);
  } else {
    console.error(`❌ エラー: ${SOURCE_VIDEO} が見つかりません`);
    process.exit(1);
  }
  
  // 2. キャプションファイルを作成
  const captionText = extractCaptionFromMarkdown(captionFile);
  const captionPath = path.join(distPath, 'caption.txt');
  fs.writeFileSync(captionPath, captionText, 'utf-8');
  console.log(`✅ キャプションファイルを作成しました: ${captionPath}`);
  console.log(`   内容プレビュー: ${captionText.substring(0, 50)}...`);
  
  // 3. ハッシュタグファイルを作成
  const hashtagsText = extractHashtagsFromMarkdown(hashtagsFile);
  const hashtagsPath = path.join(distPath, 'hashtags.txt');
  fs.writeFileSync(hashtagsPath, hashtagsText, 'utf-8');
  console.log(`✅ ハッシュタグファイルを作成しました: ${hashtagsPath}`);
  console.log(`   内容プレビュー: ${hashtagsText.substring(0, 50)}...`);
  
  console.log('\n🎉 パッケージングが完了しました！');
  console.log(`📁 出力先: ${distPath}/`);
  console.log('\n📋 生成されたファイル:');
  console.log(`   - output.mp4`);
  console.log(`   - caption.txt`);
  console.log(`   - hashtags.txt`);
  console.log('\n💡 このフォルダをクラウド同期してスマホから投稿できます！');
}

// スクリプト実行
try {
  packageSNSAssets();
} catch (error) {
  console.error('❌ エラーが発生しました:', error.message);
  process.exit(1);
}
