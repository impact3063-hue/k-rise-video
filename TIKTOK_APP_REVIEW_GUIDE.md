# TikTok アプリ審査通過ガイド

## エラー概要
「This form has 8 errors. Review」というエラーは、TikTok Developer Portalでアプリの基本情報が未入力のために発生します。

## 必須設定項目と具体的な入力例

### 1. App Icon（アプリアイコン）
**要件:**
- サイズ: 512x512 ピクセル以上
- フォーマット: PNG または JPG
- 背景: 透明または単色推奨

**設定手順:**
1. 512x512pxの画像を用意（プロジェクトロゴや会社ロゴを使用）
2. Developer Portal > App Settings > Basic Information
3. "App Icon" セクションで画像をアップロード

**ダミー画像の作成方法:**
```bash
# オンラインツールで作成する場合
# https://www.canva.com/ などで512x512pxの画像を作成
# または https://placeholder.com/512x512 を使用
```

---

### 2. App Name（アプリ名）
**入力例:**
```
K-Rise Video Creator
```

**ガイドライン:**
- 最大50文字
- プロジェクトの目的を反映した名前
- 特殊文字は避ける

---

### 3. App Description（アプリの説明）
**入力例（英語）:**
```
K-Rise Video Creator is an automated video content creation and publishing tool designed for TikTok. This application helps content creators generate engaging short-form videos with AI-powered scripts and subtitles, and automatically publish them to TikTok using the Content Posting API.

Key Features:
- Automated script generation using AI
- Automatic subtitle creation with Whisper
- Direct video posting to TikTok
- Content scheduling and management

This app is designed for internal use to streamline our content creation workflow and maintain consistent posting schedules on TikTok.
```

**入力例（日本語版も用意する場合）:**
```
K-Rise Video Creatorは、TikTok向けの自動動画コンテンツ作成・投稿ツールです。このアプリケーションは、AIを活用したスクリプト生成と字幕作成により、魅力的なショート動画の制作をサポートし、Content Posting APIを使用してTikTokへ自動投稿します。

主な機能:
- AIによる自動スクリプト生成
- Whisperを使用した自動字幕作成
- TikTokへの直接動画投稿
- コンテンツのスケジュール管理

このアプリは、コンテンツ制作ワークフローを効率化し、TikTokでの一貫した投稿スケジュールを維持するための内部使用を目的としています。
```

**ガイドライン:**
- 最小100文字、推奨200-500文字
- アプリの目的、機能、使用用途を明確に記載
- TikTok APIの使用目的を具体的に説明

---

### 4. Redirect URI（リダイレクトURI）
**入力例:**

**開発環境用:**
```
http://localhost:8000/callback
```

**本番環境用（推奨）:**
```
https://yourdomain.com/tiktok/callback
```

**複数設定する場合（改行で区切る）:**
```
http://localhost:8000/callback
http://localhost:3000/callback
https://yourdomain.com/tiktok/callback
```

**ガイドライン:**
- HTTPSを推奨（本番環境では必須）
- localhostは開発時のみ使用可能
- 実際に使用するコールバックURLと完全一致させる
- 複数のURIを登録可能

**注意:**
現在のプロジェクトでは `http://localhost:8000/callback` を使用しているため、これを必ず含める

---

### 5. Privacy Policy URL（プライバシーポリシーURL）
**入力例:**
```
https://yourdomain.com/privacy-policy
```

**ダミーURL（テスト用）:**
```
https://www.example.com/privacy-policy
```

**プライバシーポリシーのテンプレート:**

以下の内容を含むHTMLページを作成し、公開サーバーにアップロードしてください。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Privacy Policy - K-Rise Video Creator</title>
</head>
<body>
    <h1>Privacy Policy</h1>
    <p>Last updated: [日付]</p>
    
    <h2>1. Information We Collect</h2>
    <p>K-Rise Video Creator collects the following information when you use our service:</p>
    <ul>
        <li>TikTok account information (username, profile data) necessary for authentication</li>
        <li>Video content and metadata that you choose to publish</li>
        <li>Usage data to improve our service</li>
    </ul>
    
    <h2>2. How We Use Your Information</h2>
    <p>We use the collected information for:</p>
    <ul>
        <li>Authenticating your TikTok account</li>
        <li>Publishing video content on your behalf</li>
        <li>Improving our service functionality</li>
    </ul>
    
    <h2>3. Data Storage and Security</h2>
    <p>We store your access tokens securely and use them only for authorized TikTok API operations. We do not share your data with third parties.</p>
    
    <h2>4. Your Rights</h2>
    <p>You can revoke access to your TikTok account at any time through TikTok's settings.</p>
    
    <h2>5. Contact Us</h2>
    <p>If you have questions about this Privacy Policy, please contact us at: [メールアドレス]</p>
</body>
</html>
```

**簡易的な公開方法:**
- GitHub Pages（無料）: リポジトリに `privacy-policy.html` を作成してPages機能で公開
- Netlify/Vercel（無料）: 静的HTMLをデプロイ
- Google Sites（無料）: 簡単にページを作成可能

---

### 6. Terms of Service URL（利用規約URL）
**入力例:**
```
https://yourdomain.com/terms-of-service
```

**ダミーURL（テスト用）:**
```
https://www.example.com/terms-of-service
```

**利用規約のテンプレート:**

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Terms of Service - K-Rise Video Creator</title>
</head>
<body>
    <h1>Terms of Service</h1>
    <p>Last updated: [日付]</p>
    
    <h2>1. Acceptance of Terms</h2>
    <p>By using K-Rise Video Creator, you agree to these Terms of Service.</p>
    
    <h2>2. Description of Service</h2>
    <p>K-Rise Video Creator is a tool that helps you create and publish video content to TikTok automatically.</p>
    
    <h2>3. User Responsibilities</h2>
    <ul>
        <li>You are responsible for all content published through our service</li>
        <li>You must comply with TikTok's Community Guidelines and Terms of Service</li>
        <li>You must not use the service for illegal or unauthorized purposes</li>
    </ul>
    
    <h2>4. Intellectual Property</h2>
    <p>You retain all rights to the content you create and publish through our service.</p>
    
    <h2>5. Limitation of Liability</h2>
    <p>We are not liable for any damages arising from your use of the service.</p>
    
    <h2>6. Changes to Terms</h2>
    <p>We reserve the right to modify these terms at any time.</p>
    
    <h2>7. Contact Information</h2>
    <p>For questions about these Terms, contact us at: [メールアドレス]</p>
</body>
</html>
```

---

### 7. Category（カテゴリ）
**選択例:**
```
Tools & Utilities
```

または

```
Content & Publishing
```

**ガイドライン:**
- ドロップダウンから最も適切なカテゴリを選択
- 動画作成・投稿ツールの場合は「Tools & Utilities」または「Content & Publishing」が適切

---

### 8. Platform（プラットフォーム）
**選択例:**
```
☑ Web
```

**ガイドライン:**
- 現在のプロジェクトはPythonスクリプトベースなので「Web」を選択
- 必要に応じて複数選択可能

---

## 設定手順（ステップバイステップ）

### Step 1: Developer Portalにログイン
1. https://developers.tiktok.com/ にアクセス
2. 「Manage apps」をクリック
3. 対象のアプリを選択

### Step 2: Basic Information を入力
1. 左メニューから「Basic Information」を選択
2. 以下の項目を順番に入力:
   - App Name
   - App Icon（画像アップロード）
   - Category
   - Platform
   - App Description

### Step 3: Redirect URIs を設定
1. 「Redirect URIs」セクションで「Add」をクリック
2. `http://localhost:8000/callback` を入力
3. 必要に応じて追加のURIを登録

### Step 4: Privacy Policy と Terms of Service を設定
1. Privacy Policy URLを入力
2. Terms of Service URLを入力
3. ※事前にこれらのページを公開しておく必要があります

### Step 5: 保存して確認
1. ページ下部の「Save」ボタンをクリック
2. エラーがないことを確認
3. すべての必須項目に緑のチェックマークが表示されることを確認

### Step 6: Content Posting API を追加
1. 左メニューから「Add products」を選択
2. 「Content Posting API」を見つけて「Add」をクリック
3. 「Direct Post」をオンにする
4. 「Save」をクリック

---

## 審査提出前のチェックリスト

- [ ] App Icon（512x512px以上）がアップロード済み
- [ ] App Nameが入力済み
- [ ] App Description（100文字以上）が入力済み
- [ ] Categoryが選択済み
- [ ] Platformが選択済み
- [ ] Redirect URI（`http://localhost:8000/callback`）が登録済み
- [ ] Privacy Policy URLが入力済み、かつページが公開されている
- [ ] Terms of Service URLが入力済み、かつページが公開されている
- [ ] Content Posting APIが追加済み
- [ ] Direct Postがオンになっている

---

## よくある質問

### Q1: Privacy PolicyやTerms of Serviceのページがない場合は？
**A:** 以下の方法で簡易的に作成できます:
1. GitHub Pagesを使用（無料）
2. Google Sitesを使用（無料）
3. Netlify/Vercelで静的HTMLをデプロイ（無料）

### Q2: 開発中でまだ本番URLがない場合は？
**A:** 
- Redirect URIは `http://localhost:8000/callback` のみでOK
- Privacy PolicyとTerms of ServiceはGitHub Pagesなどの無料サービスで公開

### Q3: アプリアイコンがない場合は？
**A:** 
- Canvaなどで簡単なロゴを作成
- プロジェクト名の頭文字を使ったシンプルなデザインでOK
- 512x512pxのPNG形式で保存

### Q4: 審査にどのくらい時間がかかる？
**A:** 
- 通常1-3営業日
- 場合によっては1週間程度かかることもあります

### Q5: 審査が却下された場合は？
**A:** 
- TikTokからのフィードバックを確認
- 指摘された項目を修正
- 再提出が可能

---

## トラブルシューティング

### エラー: "Invalid Redirect URI"
**解決策:**
- URIが完全一致しているか確認
- プロトコル（http/https）が正しいか確認
- ポート番号が含まれているか確認

### エラー: "Privacy Policy URL is not accessible"
**解決策:**
- URLが実際にアクセス可能か確認
- HTTPSを使用しているか確認（推奨）
- ページが公開されているか確認

### エラー: "App Icon size is too small"
**解決策:**
- 512x512px以上の画像を使用
- PNG または JPG形式で保存

---

## 参考リンク

- [TikTok Developer Documentation](https://developers.tiktok.com/doc/overview)
- [Content Posting API Guide](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [App Review Guidelines](https://developers.tiktok.com/doc/app-review-guidelines)

---

## 次のステップ

1. このガイドに従って必要な情報を準備
2. Privacy PolicyとTerms of Serviceのページを作成・公開
3. Developer Portalで全項目を入力
4. Content Posting APIを追加してDirect Postをオン
5. 保存してエラーがないことを確認
6. 必要に応じて審査を提出

---

**注意:** 
- 本番環境で使用する場合は、適切なドメインとHTTPSを使用してください
- Privacy PolicyとTerms of Serviceは法的文書なので、必要に応じて法務担当者に確認してください
- TikTokのポリシーは変更される可能性があるため、最新の情報は公式ドキュメントを確認してください
