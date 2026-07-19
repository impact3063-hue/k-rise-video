# 🚀 RIIZE Dance Challenge - クイックスタートガイド

## 📋 5分で動画生成

### Step 1: データファイルの切り替え（10秒）

```bash
cd k-rise-video/public
copy video-data-master-riize.json video-data-master.json
```

### Step 2: Root.tsx にコンポジション追加（1分）

[`src/Root.tsx`](src/Root.tsx) を開き、以下を追加：

```typescript
// インポート追加
import { KRiseTikTok3Enhanced } from "./KRiseTikTok3Enhanced";

// Composition追加（既存のCompositionの下に）
<Composition
  id="KRiseTikTok3Enhanced"
  component={KRiseTikTok3Enhanced}
  durationInFrames={450}
  fps={30}
  width={1080}
  height={1920}
/>
```

### Step 3: プレビュー（30秒）

```bash
npm start
```

ブラウザで `KRiseTikTok3Enhanced` を選択してプレビュー。

### Step 4: レンダリング（2分）

```bash
npx remotion render KRiseTikTok3Enhanced output-riize.mp4
```

### Step 5: TikTok投稿（1分）

```bash
python upload_tiktok_auto.py
```

**キャプション例**:
```
RIIZEの新曲ダンスチャレンジに挑戦！🔥
未経験でもプロが直接指導💪

続きはプロフィールのLINEから👇
限定ワークショップ受付中🎵

#RIIZE #RIIZEChallenge #KRISEDanceProject
```

---

## 🎨 カスタマイズ（オプション）

### CTA メッセージ変更

[`video-data-master-riize.json`](public/video-data-master-riize.json) の `content.cta.message` を編集：

```json
{
  "content": {
    "cta": {
      "message": "あなたのメッセージ\n複数行OK"
    }
  }
}
```

### 歌詞変更

`subtitles` セクションの `text` と `characters` を編集。

詳細は [RIIZE_DANCE_CHALLENGE_SYSTEM.md](RIIZE_DANCE_CHALLENGE_SYSTEM.md) を参照。

---

## ✅ チェックリスト

- [ ] `video-data-master-riize.json` を `video-data-master.json` にコピー
- [ ] `Root.tsx` に `KRiseTikTok3Enhanced` を追加
- [ ] プレビューで確認
- [ ] レンダリング実行
- [ ] TikTok/Reels に投稿
- [ ] プロフィールに LINE URL 設置
- [ ] LINE Bot で自動応答設定

---

## 🎯 期待される成果

- **視聴回数**: RIIZE トレンドに乗って爆発的増加
- **プロフィールクリック率**: CTA の強調で 15-25%
- **LINE登録率**: 明確な動線で 5-10%
- **ワークショップ予約**: 限定感で高コンバージョン

---

**🔥 今すぐ始めて、RIIZE の熱量を K-RISE へ！**
