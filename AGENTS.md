# AGENTS.md — K-RISE 動画量産システム 開発規約

## プロジェクト概要
Remotion製TikTok縦動画(1080x1920/30fps)の自律量産ライン。
音声(TTS) → ffmpeg無音実測 → 1文字同期JSON → バリデーション → レンダリング。

## コマンド一覧（この順で使う）
```bash
npm run generate      # 台本生成→TTS→同期JSON出力 (要OPENAI_API_KEY)
                      # 手動台本: python scripts/generate-master.py --script-file X.txt [--skip-tts]
npm run validate      # バリデーションゲート。exit 1なら型崩れ（レンダリング禁止）
npm run render-batch  # generate→validate→render を一発実行 → out/auto.mp4
npm run render-tiktok3 # validate→render のみ → out/test.mp4
npm run optimize      # 戦績ログから演出パラメータ進化 (週1)
npm run lint          # eslint src && tsc
npm run build         # remotion bundle（検証用）
```

## 絶対規約
1. **防衛資産に触れる前に必ずバックアップ**: `public/video-data-master.json` を変更する処理は `.prev`/`.bak` を残す（generate-master.pyは自動で行う）
2. **validate を通らないデータでレンダリングしない**（npm scriptsに組み込み済み）
3. **カラオケ演出のコア仕様**（変更には明示承認が必要）:
   - アクティブ判定は半開区間 `frame >= start && frame < end`
   - 発音中のみ #FFD700 + スケール1.15倍、他は rgba(255,255,255,0.6)
   - CSS transition 禁止（レンダリングの純粋性を壊す）— 全アニメは useCurrentFrame() 駆動
   - 字幕は完全画面中央、fontSize は clamp(3rem, 9vw, 5.5rem) を docs/params-current.json で管理
4. **Hookは早期returnより前に**（Rules of Hooks）
5. **`<img>` 禁止 → remotion の `<Img />` を使う**

## 主要ファイル
- `src/KRiseTikTok3.tsx` — 本命コンポジション（Character-Level Sync）
- `public/video-data-master.json` — Single Source of Truth（音声タイミング/スタイル/文字）
- `scripts/generate-master.py` — 台本→音声→同期データの統合生成
- `scripts/validate-video-data.mjs` — 型崩れ検知ゲート（音声1対1/カバレッジ/TS整合/CTA/スキーマ）
- `scripts/optimize-params.py` — 戦績解析→docs/params-current.json 自動更新
- `docs/tiktok-analytics-log.json` — 人間が転記する戦績（進化の燃料）

## ログ出力の規約（トークン節約）
シェル実行時は `| tail -N` や `grep -E 'Encoded|Error|✅|❌'` で要点のみ抽出すること。
レンダリングの全プログレスログをコンテキストに載せない。
