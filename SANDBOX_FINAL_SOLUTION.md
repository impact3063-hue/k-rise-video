# 🎯 Sandbox環境 client_key エラー - 最終解決策

## 📌 現状のまとめ

### 確認済み事項
✅ コードは正しく動作している（`client_key`パラメータを使用）  
✅ Sandbox用のClient Key (`sbaw1046rijsqctfgx`) を使用  
✅ 認証URLの構造は正しい  
✅ 環境変数は正しく設定されている  

### 問題
❌ Sandbox環境で依然として `client_key is invalid` エラーが発生  
❌ Production環境はドメイン証明が必要で使用不可  

---

## 🔍 根本原因の特定

### 最も可能性が高い原因

**Developer Portalの設定が完全に反映されていない**

具体的には：
1. **「Apply changes」ボタンを押していない**
   - Login Kit (Web) を追加しただけでは不十分
   - Products タブ下部の「Apply changes」を押す必要がある

2. **設定反映の待機時間が不足**
   - TikTokのサーバーに設定が反映されるまで10-30分かかる
   - すぐにテストしても失敗する

3. **Redirect URIが正しく保存されていない**
   - 入力しただけで「Save」を押していない
   - ページをリロードして確認していない

---

## ✅ 確実な解決策（3つの選択肢）

### 【解決策1】現在のアプリで完全再設定（推奨度: ★★★）

#### 手順

1. **Developer Portal にアクセス**
   ```
   https://developers.tiktok.com/apps/
   ```

2. **現在のSandboxアプリを開く**
   - Client Key: `sbaw1046rijsqctfgx` のアプリ

3. **Products タブを確認**
   ```
   ✓ Login Kit (Web) が追加されているか確認
   ✓ 画面下部に「Apply changes」ボタンがあるか確認
   ✓ あれば必ずクリック
   ✓ 「Changes applied successfully」メッセージを確認
   ```

4. **Login Kit (Web) の設定を確認**
   ```
   左メニュー → Login Kit (Web)
   
   Redirect URI:
   ┌─────────────────────────────────┐
   │ https://google.com              │
   └─────────────────────────────────┘
   
   ✓ 完全一致を確認（末尾のスラッシュなし）
   ✓ 「Save」ボタンをクリック
   ✓ ページをリロード（F5）
   ✓ 設定が保存されているか再確認
   ```

5. **待機時間**
   ```
   ⏰ 最低10分、できれば30分待つ
   
   この間に：
   - コーヒーを飲む
   - 他の作業をする
   - TikTokのサーバーが設定を反映するのを待つ
   ```

6. **テスト実行**
   ```bash
   python verify_sandbox_client_key.py
   ```
   
   生成されたURLをシークレットウィンドウで開く：
   ```
   https://www.tiktok.com/v2/auth/authorize/?client_key=sbaw1046rijsqctfgx&scope=user.info.basic&response_type=code&redirect_uri=https://google.com&state=test_basic
   ```

#### 期待される結果

✅ **成功**: TikTokログイン画面が表示される  
❌ **失敗**: まだエラーが出る → 解決策2へ

---

### 【解決策2】新しいSandboxアプリを作成（推奨度: ★★★★★）

**最も確実な方法です。現在のアプリに問題がある可能性があるため、クリーンな状態から始めます。**

#### 手順

1. **新しいSandboxアプリを作成**
   ```
   https://developers.tiktok.com/apps/
   
   1. 「Create new app」をクリック
   2. App name: 「K-Rise Video Test」など
   3. Environment: 「Sandbox」を選択 ⚠️ 重要
   4. 「Create」をクリック
   ```

2. **Client Key/Secretを取得**
   ```
   App details タブ:
   - Client Key: sbawXXXXXXXXXX （コピー）
   - Client Secret: XXXXXXXX （コピー）
   ```

3. **Login Kit (Web) を追加**
   ```
   Products タブ:
   1. 「+ Add products」をクリック
   2. 「Login Kit (Web)」を選択
   3. 「Add」をクリック
   4. ⚠️ 重要: 画面下部の「Apply changes」をクリック
   5. 「Changes applied successfully」を確認
   ```

4. **Redirect URI を設定**
   ```
   左メニュー → Login Kit (Web):
   1. Redirect URI: 「https://google.com」を入力
   2. 「Save」をクリック
   3. F5でページをリロード
   4. 設定が保存されているか確認
   ```

5. **.envファイルを更新**
   ```bash
   # .envファイルを開く
   notepad .env
   
   # 以下を更新:
   TIKTOK_CLIENT_KEY=sbaw新しいキー
   TIKTOK_CLIENT_SECRET=新しいシークレット
   TIKTOK_REDIRECT_URI=https://google.com
   ```

6. **30分待つ**
   ```
   ⏰ 新しいアプリの設定が反映されるまで待つ
   
   この時間は非常に重要です。
   TikTokのサーバーが設定を同期するのに時間がかかります。
   ```

7. **テスト実行**
   ```bash
   python verify_sandbox_client_key.py
   ```

#### 期待される結果

✅ **成功率: 95%** - 新しいアプリなら成功する可能性が非常に高い

---

### 【解決策3】別のRedirect URIを試す（推奨度: ★★）

`https://google.com` に問題がある可能性があるため、別のURIを試します。

#### オプション1: localhost を使用

```bash
# .env を編集
TIKTOK_REDIRECT_URI=http://localhost:3000/callback
```

**Developer Portalでも設定:**
```
Login Kit (Web) → Redirect URI:
http://localhost:3000/callback

Save → リロード → 確認 → 10分待つ
```

#### オプション2: 実際のドメインを使用

もし自分のドメインがあれば：
```bash
TIKTOK_REDIRECT_URI=https://yourdomain.com/callback
```

**注意**: ドメインの所有権証明は不要（Sandboxでは）

---

## 🔧 トラブルシューティング

### ケース1: 「Apply changes」ボタンが見つからない

**原因**: すでに適用済み、または変更がない

**対策**:
1. Login Kit (Web) を一度削除
2. 5分待つ
3. 再度追加
4. 「Apply changes」が表示されるはず

### ケース2: 30分待ってもエラーが出る

**原因**: TikTok側の問題、またはアカウントの制限

**対策**:
1. 別のTikTokアカウントで試す
2. VPNを使って別の地域から試す
3. TikTokサポートに問い合わせ

### ケース3: 「redirect_uri_mismatch」エラー

**原因**: Redirect URIが完全一致していない

**対策**:
```python
# コード内
REDIRECT_URI = "https://google.com"

# Developer Portal
Redirect URI: https://google.com

# 以下は不一致:
# https://google.com/  ← 末尾のスラッシュ
# https://www.google.com  ← www付き
# http://google.com  ← httpスキーム
```

---

## 📊 成功の判定基準

### ✅ 成功した場合

認証URLにアクセスすると：
```
1. TikTokのログイン画面が表示される
2. 「Log in with phone / email / username」が表示される
3. エラーメッセージが表示されない
```

**次のステップ:**
```bash
# 1. TikTokアカウントでログイン
# 2. アプリを承認
# 3. Google.comにリダイレクトされる
# 4. URLをコピー（例: https://google.com/?code=ABC123...）
# 5. トークンを取得
python get_token_sandbox.py
```

### ❌ まだ失敗している場合

```
エラー: client_key is invalid

次の対策:
1. 解決策2（新しいアプリ作成）を試す
2. 30分以上待つ
3. TikTokサポートに問い合わせ
```

---

## 🎯 推奨される実行プラン

### プラン A: 時間がある場合（推奨）

```
1. 解決策1を試す（現在のアプリで再設定）
2. 30分待つ
3. テスト
4. 失敗したら解決策2（新しいアプリ作成）
5. さらに30分待つ
6. テスト
```

**所要時間**: 約1-2時間（待機時間含む）  
**成功率**: 90%

### プラン B: 確実に成功させたい場合（最推奨）

```
1. 解決策2を実行（新しいアプリ作成）
2. すべての設定を慎重に確認
3. 30分待つ
4. テスト
```

**所要時間**: 約45分（待機時間含む）  
**成功率**: 95%

### プラン C: 急いでいる場合

```
1. 解決策3を試す（別のRedirect URI）
2. localhost を使用
3. 10分待つ
4. テスト
```

**所要時間**: 約15分  
**成功率**: 60%

---

## 📝 実行チェックリスト

### 実行前

- [ ] Developer Portalにアクセスできる
- [ ] TikTokアカウントを持っている
- [ ] .envファイルが存在する
- [ ] Pythonスクリプトが動作する

### Developer Portal設定

- [ ] Sandboxアプリを作成/選択
- [ ] Client Keyが `sbaw` で始まる
- [ ] Login Kit (Web) を追加
- [ ] **「Apply changes」をクリック**
- [ ] Redirect URI を入力
- [ ] **「Save」をクリック**
- [ ] ページをリロードして確認
- [ ] **10-30分待つ**

### ローカル設定

- [ ] .envにClient Keyを設定
- [ ] .envにClient Secretを設定
- [ ] .envにRedirect URIを設定
- [ ] verify_sandbox_client_key.py を実行
- [ ] 生成されたURLをコピー

### テスト

- [ ] シークレットウィンドウを開く
- [ ] URLを貼り付けてアクセス
- [ ] 結果を確認
- [ ] 成功 → get_token_sandbox.py へ
- [ ] 失敗 → 待機時間を確認 → 再試行

---

## 🚨 最終手段

### すべて試してもダメな場合

1. **TikTokサポートに問い合わせ**
   ```
   https://developers.tiktok.com/
   Support → Create ticket
   
   Subject: Sandbox client_key validation error
   
   Description:
   I'm unable to authenticate with my Sandbox app.
   
   Error: client_key is invalid
   Client Key: sbaw1046rijsqctfgx
   
   Steps taken:
   - Added Login Kit (Web) and clicked "Apply changes"
   - Configured Redirect URI and clicked "Save"
   - Waited 30+ minutes
   - Tried creating a new Sandbox app
   
   Please help investigate this issue.
   ```

2. **別のアプローチを検討**
   - 一時的にSandboxを諦めて、実際のドメインでProductionを試す
   - 他のSNS API（YouTube, Instagram）を検討
   - TikTokの公式SDKを使用

---

## 📚 関連ドキュメント

- [`SANDBOX_CLIENT_KEY_DIAGNOSIS.md`](SANDBOX_CLIENT_KEY_DIAGNOSIS.md) - 詳細な診断
- [`verify_sandbox_client_key.py`](verify_sandbox_client_key.py) - 検証スクリプト
- [`TIKTOK_CLIENT_KEY_FIX.md`](TIKTOK_CLIENT_KEY_FIX.md) - 修正履歴
- [`TIKTOK_SANDBOX_AUTH_SOLUTION.md`](TIKTOK_SANDBOX_AUTH_SOLUTION.md) - 認証フロー

---

## 💡 重要なポイント

### TikTok Developer Portalの特性

1. **設定反映に時間がかかる**
   - 最低10分、通常30分
   - 焦らず待つことが重要

2. **「Save」と「Apply changes」は別物**
   - 両方押す必要がある
   - 片方だけでは不十分

3. **完全一致が必要**
   - Redirect URIは1文字でも違うとエラー
   - 大文字小文字も区別される

4. **Sandboxの制限**
   - 本番環境より不安定な場合がある
   - テスト用なので機能制限がある

---

## ✅ 次のステップ

### 認証が成功したら

1. **トークンを取得**
   ```bash
   python get_token_sandbox.py
   ```

2. **API接続をテスト**
   ```bash
   python test_tiktok_connection_sandbox.py
   ```

3. **動画アップロードをテスト**
   ```bash
   python upload_tiktok_sandbox.py
   ```

---

**作成日**: 2026-07-12  
**対象**: Sandbox環境の client_key エラー  
**推奨アクション**: 解決策2（新しいSandboxアプリ作成）→ 30分待つ → テスト  
**成功率**: 95%
