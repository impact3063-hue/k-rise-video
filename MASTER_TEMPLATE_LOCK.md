# 🔒 K-RISE マスターテンプレート ロックダウン仕様書

## 📋 概要

このドキュメントは、K-RISE初号機動画（コミット `3a60dc2`）の成功コードを**永久保護**し、自動生成スクリプトによる上書きを完全に遮断するための仕様書です。

## 🎯 ロック対象ファイル

### 1. `public/video-data-master.json` 
**ステータス**: 🔒 **完全ロック（手動編集のみ許可）**

#### 確定仕様
- **バージョン**: `8.0.0-character-sync`
- **セグメント数**: 4つ（固定）
- **総フレーム数**: 420フレーム（14秒 @ 30fps）
- **改行制御**: `\n` による明示的改行のみ（自動折り返し禁止）

#### 4つの固定セグメント
1. **seg1** (0-90フレーム): "伝説のプロデューサー\n出口氏による直接審査"
2. **seg2** (90-180フレーム): "未来のKPOPスターを発掘する\nリアルオーディション"
3. **seg3** (180-330フレーム): "残された席はあとわずか\n今すぐ公式LINEから"
4. **seg4** (330-420フレーム): "エントリーせよ"

#### 文字レベル同期仕様
- **ゴールド発光**: `#FFD700` (1文字ずつ)
- **拡大率**: `1.1倍` (アクティブ文字)
- **タイミング**: 各文字に `startFrame` / `endFrame` を個別設定

### 2. `src/KRiseTikTok3.tsx`
**ステータス**: 🔒 **完全ロック（レイアウト変更禁止）**

#### 確定仕様
- **改行制御**: `whiteSpace: "nowrap"`, `flexWrap: "nowrap"`
- **文字色**: アクティブ時 `#FFD700`, 非アクティブ時 `#FFFFFF`
- **スケール**: アクティブ時 `1.1`, 非アクティブ時 `1.0`
- **グロー効果**: 
  - アクティブ: `0px 0px 30px rgba(255,215,0,1.0)`
  - 非アクティブ: `0px 0px 20px rgba(255,215,0,0.8)`

## 🚫 自動生成スクリプトの無効化

### 無効化対象スクリプト

以下のスクリプトは `video-data-master.json` を**自動上書き**する可能性があるため、ビルドプロセスから完全に切り離されています：

#### Python スクリプト
1. **`generate_video_data_master.py`** (v3.1)
   - 機能: OpenAI TTS + Whisper による音声生成と字幕同期
   - 出力先: `public/video-data-master.json`
   - **状態**: ⚠️ 手動実行のみ（ビルドから除外）

2. **`generate_video_data_master_v3.2.py`** (v3.2)
   - 機能: 固有名詞保護システム付き字幕生成
   - 出力先: `public/video-data-master.json`
   - **状態**: ⚠️ 手動実行のみ（ビルドから除外）

3. **`scripts/generate-master.py`** (v5.0)
   - 機能: LLM台本生成 + TTS + 完全自動パイプライン
   - 出力先: `public/video-data-master.json`
   - **状態**: ⚠️ 手動実行のみ（ビルドから除外）

#### npm スクリプト（package.json）
以下のコマンドは**マスターテンプレートを上書きしない**ことを確認済み：

- ✅ `npm run dev` - 開発サーバー起動（読み取りのみ）
- ✅ `npm run build` - バンドル生成（読み取りのみ）
- ✅ `npm run validate` - データ検証（読み取りのみ）
- ⚠️ `npm run generate` - **手動実行のみ**（自動ビルドから除外）
- ⚠️ `npm run render-batch` - **手動実行のみ**（自動ビルドから除外）

### ビルドプロセスの安全性

#### 安全なコマンド（マスターテンプレート不変）
```bash
npm run dev              # ✅ 開発サーバー（読み取りのみ）
npm run build            # ✅ バンドル生成（読み取りのみ）
npm run validate         # ✅ データ検証（読み取りのみ）
npm run render-tiktok3   # ✅ レンダリング（読み取りのみ）
```

#### 危険なコマンド（マスターテンプレート上書きの可能性）
```bash
npm run generate         # ⚠️ Python スクリプト実行（上書き注意）
npm run render-batch     # ⚠️ 生成 + レンダリング（上書き注意）
python generate_video_data_master.py        # ⚠️ 直接上書き
python generate_video_data_master_v3.2.py   # ⚠️ 直接上書き
python scripts/generate-master.py           # ⚠️ 直接上書き
```

## 🛡️ 保護メカニズム

### 1. バックアップファイル
- **`public/video-data-master.json.LOCKED`** - 読み取り専用マスターコピー
- **`public/video-data-master.json.bak-*`** - タイムスタンプ付きバックアップ

### 2. ソースコード保護
[`src/KRiseTikTok3.tsx`](../k-rise-video/src/KRiseTikTok3.tsx) の冒頭に以下の警告コメントを追加：

```typescript
/**
 * 🔒 LOCKED TEMPLATE - DO NOT MODIFY
 * 
 * このファイルは K-RISE 初号機マスター動画テンプレート（コミット 3a60dc2）です。
 * 以下の仕様は変更禁止：
 * 
 * - whiteSpace: "nowrap" (自動折り返し禁止)
 * - flexWrap: "nowrap" (改行制御)
 * - 1文字ゴールド発光: #FFD700
 * - 拡大率: 1.1倍
 * 
 * 変更が必要な場合は、新しいコンポーネント（KRiseTikTok4.tsx等）を作成してください。
 */
```

### 3. データ検証
[`scripts/validate-video-data.mjs`](../k-rise-video/scripts/validate-video-data.mjs) による自動検証：
- セグメント数が4つであることを確認
- 各セグメントのフレーム範囲を検証
- 文字レベルタイミングの整合性チェック

## 📝 変更履歴

### 2026-07-20 - 初回ロックダウン
- **コミット**: `3a60dc2` の成功コードを確定
- **理由**: 修正を繰り返す中でのデータ先祖返りを防止
- **対象**: `video-data-master.json` + `KRiseTikTok3.tsx`
- **実施者**: システム管理者

## 🔧 復元手順

万が一、マスターテンプレートが上書きされた場合の復元方法：

```bash
# 1. ロックファイルから復元
cd k-rise-video
copy public\video-data-master.json.LOCKED public\video-data-master.json

# 2. Gitから復元（コミット 3a60dc2）
git checkout 3a60dc2 -- public/video-data-master.json
git checkout 3a60dc2 -- src/KRiseTikTok3.tsx

# 3. 検証
npm run validate
```

## ⚠️ 重要な注意事項

1. **新しい動画を作成する場合**
   - `video-data-master.json` を直接編集しない
   - 新しいJSONファイル（例: `video-data-v2.json`）を作成
   - 新しいコンポーネント（例: `KRiseTikTok4.tsx`）を作成

2. **自動生成スクリプトの使用**
   - 必ず出力先を変更してから実行
   - `video-data-master.json` への直接出力を禁止

3. **ビルド前の確認**
   - `npm run validate` で整合性を確認
   - バックアップファイルの存在を確認

## 📞 サポート

問題が発生した場合は、このドキュメントを参照し、必要に応じて復元手順を実行してください。

---

**最終更新**: 2026-07-20  
**ステータス**: 🔒 LOCKED  
**バージョン**: 1.0.0
