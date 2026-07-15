# 🔍 Sandbox環境 client_key エラーの根本原因と解決策

## 📊 現状分析

### 確認済み事項
✅ コードは正しく `client_key` パラメータを使用している  
✅ Sandbox用のClient Key (`sbaw1046rijsqctfgx`) を使用している  
✅ URLエンコードは使用していない  
✅ 認証URLは正しい (`https://www.tiktok.com/v2/auth/authorize/`)  

### 問題の本質
**Sandbox環境でも依然として `client_key is invalid` エラーが出る**

---

## 🎯 根本原因の特定

### 原因1: Developer Portal側の設定不備（最も可能性が高い）

Sandbox環境のDeveloper Portalで以下のいずれかが不完全な可能性：

1. **Login Kit (Web) が正しく有効化されていない**
   - 追加しただけで「Apply changes」を押していない
   - 設定が反映されるまでの待機時間が不足（5-10分必要）

2. **Redirect URIが正しく保存されていない**
   - 入力したが「Save」を押していない
   - 保存後にページをリロードして確認していない
   - 完全一致していない（末尾のスラッシュなど）

3. **Sandbox環境の制限**
   - Sandboxアプリの状態が「Draft」のまま
   - 必要なProductsが追加されていない
   - アプリの承認待ち状態

### 原因2: Client Keyの状態

1. **Client Keyが無効化されている**
   - Developer Portalで再生成された
   - アプリが削除・再作成された

2. **Client Keyの環境不一致**
   - `.env`のClient Keyとポータルのものが異なる

### 原因3: TikTok側のSandbox環境の問題

1. **Sandbox環境の一時的な不具合**
   - TikTok側のサーバー問題
   - メンテナンス中

2. **地域制限**
   - 日本からのSandboxアクセスに制限がある可能性

---

## ✅ 具体的な解決策

### 解決策1: Developer Portalの完全再設定（推奨）

#### ステップ1: 現在の設定を完全確認

```bash
python check_sandbox_setup.py
```

このスクリプトを実行して、以下を確認：
- Client Keyが正しいか
- .envファイルの設定が正しいか

#### ステップ2: Developer Portalで設定を再確認

1. **https://developers.tiktok.com/apps/** にアクセス
2. Sandboxアプリを選択
3. **App details** タブ:
   - Client Key: `sbaw1046rijsqctfgx` であることを確認
   - もし異なる場合は、`.env`を更新

4. **Products** タブ:
   - `Login Kit (Web)` が追加されているか確認
   - なければ「+ Add products」から追加
   - **重要**: 追加後、必ず「Apply changes」をクリック

5. **Login Kit (Web)** の設定:
   - 左メニューから「Login Kit (Web)」を選択
   - **Redirect URI**: `https://google.com` を入力
   - **重要**: 「Save」をクリック
   - ページをリロードして保存されたか確認

6. **待機時間**:
   - 設定変更後、**最低10分待つ**
   - TikTokのサーバーに設定が反映されるまで時間がかかる

#### ステップ3: 設定反映後にテスト

```bash
# 新しい認証URLを生成
python generate_auth_url_sandbox.py

# 生成されたURLをシークレットウィンドウで開く
```

---

### 解決策2: 別のRedirect URIを試す

`https://google.com` が問題の可能性があるため、別のURIを試す：

#### オプション1: localhost を使用

```bash
# .env を編集
TIKTOK_REDIRECT_URI=http://localhost:3000/callback
```

**Developer Portalでも同じURIを登録:**
1. Login Kit (Web) → Redirect URI
2. `http://localhost:3000/callback` を追加
3. Save → 10分待つ

#### オプション2: 実際のドメインを使用

もし自分のドメインがあれば：
```bash
TIKTOK_REDIRECT_URI=https://yourdomain.com/callback
```

---

### 解決策3: 新しいSandboxアプリを作成

現在のアプリに問題がある可能性があるため、新規作成：

#### ステップ1: 新しいアプリを作成

1. https://developers.tiktok.com/apps/
2. 「Create new app」をクリック
3. **App name**: `Test App 2` など
4. **Environment**: **Sandbox** を選択
5. 「Create」をクリック

#### ステップ2: 製品を追加

1. 新しいアプリを開く
2. 「Products」タブ
3. 「+ Add products」
4. 「Login Kit (Web)」を選択
5. 「Add」をクリック
6. **「Apply changes」を必ずクリック**

#### ステップ3: Redirect URIを設定

1. 左メニュー「Login Kit (Web)」
2. Redirect URI: `https://google.com`
3. 「Save」をクリック
4. ページをリロード → 保存されたか確認

#### ステップ4: 新しいClient Keyを取得

1. 「App details」タブ
2. Client Key をコピー（例: `sbawXXXXXXXXXX`）
3. Client Secret をコピー

#### ステップ5: .envを更新

```bash
TIKTOK_CLIENT_KEY=sbaw新しいキー
TIKTOK_CLIENT_SECRET=新しいシークレット
```

#### ステップ6: 10分待ってからテスト

```bash
# 10分後
python generate_auth_url_sandbox.py
```

---

### 解決策4: TikTok APIの直接検証

Developer Portalの設定が正しいか、APIレベルで検証：

```bash
python verify_sandbox_client_key.py
```

このスクリプトを作成して実行します（次のステップで作成）。

---

## 🔧 診断スクリプトの作成

### verify_sandbox_client_key.py

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sandbox Client Key の有効性を直接検証
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://google.com")

print("=" * 80)
print("🔍 Sandbox Client Key 検証")
print("=" * 80)

print(f"\nClient Key: {CLIENT_KEY}")
print(f"Redirect URI: {REDIRECT_URI}")

# 認証URLを構築
auth_url = (
    f"https://www.tiktok.com/v2/auth/authorize/"
    f"?client_key={CLIENT_KEY}"
    f"&scope=user.info.basic"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&state=test"
)

print(f"\n生成されたURL:")
print(auth_url)

print("\n" + "=" * 80)
print("📋 次の手順:")
print("=" * 80)
print("1. 上記URLをコピー")
print("2. シークレットウィンドウで開く")
print("3. 結果を報告:")
print()
print("   ✅ TikTokログイン画面が表示される → Client Key は有効")
print("   ❌ 'client_key is invalid' エラー → Developer Portal設定を確認")
print("   ❌ 'redirect_uri_mismatch' エラー → Redirect URI設定を確認")
print("=" * 80)
```

---

## 📋 完全チェックリスト

### Developer Portal（必ず全て確認）

- [ ] Sandboxアプリが作成されている
- [ ] Client Keyが `sbaw` で始まっている
- [ ] Client Keyを`.env`にコピーした
- [ ] Client Secretを`.env`にコピーした
- [ ] **Products** タブで「Login Kit (Web)」が追加されている
- [ ] **「Apply changes」ボタンを押した**
- [ ] 左メニューに「Login Kit (Web)」が表示される
- [ ] Login Kit (Web) → Redirect URI に `https://google.com` を入力
- [ ] **「Save」ボタンを押した**
- [ ] ページをリロードして設定が保存されているか確認
- [ ] **設定変更から10分以上経過している**

### ローカル環境

- [ ] `.env`ファイルが存在する
- [ ] `TIKTOK_CLIENT_KEY=sbaw...` が設定されている
- [ ] `TIKTOK_CLIENT_SECRET=...` が設定されている
- [ ] `TIKTOK_REDIRECT_URI=https://google.com` が設定されている
- [ ] `generate_auth_url_sandbox.py` が最新版
- [ ] スクリプトが `client_key` パラメータを使用している

---

## 🎯 最も可能性が高い原因と対策

### 原因: Developer Portalで「Apply changes」を押していない

**症状:**
- Login Kit (Web) を追加した
- Redirect URIを入力した
- しかし `client_key is invalid` エラーが出る

**解決策:**
1. Developer Portal → Products タブ
2. 画面下部に「Apply changes」ボタンがあるか確認
3. あれば必ずクリック
4. 10分待つ
5. 再テスト

---

## 🔄 推奨される手順（最も確実）

### フェーズ1: 完全リセット（30分）

```bash
# 1. 新しいSandboxアプリを作成（Developer Portal）
# 2. Login Kit (Web) を追加 → Apply changes
# 3. Redirect URI を設定 → Save
# 4. 10分待つ
```

### フェーズ2: ローカル設定（5分）

```bash
# 1. .envを更新
TIKTOK_CLIENT_KEY=sbaw新しいキー
TIKTOK_CLIENT_SECRET=新しいシークレット
TIKTOK_REDIRECT_URI=https://google.com

# 2. 認証URLを生成
python generate_auth_url_sandbox.py
```

### フェーズ3: テスト（5分）

```bash
# 1. シークレットウィンドウで認証URLを開く
# 2. 結果を確認:
#    - ログイン画面が表示される → 成功！
#    - エラーが出る → さらに10分待って再試行
```

---

## 💡 重要な注意事項

### TikTok Developer Portalの特性

1. **設定反映に時間がかかる**
   - 最低5分、通常10分
   - 場合によっては30分かかることも

2. **「Save」と「Apply changes」は別物**
   - Save: 個別設定の保存
   - Apply changes: 全体の変更を反映
   - **両方必要**

3. **ページリロードで確認**
   - 設定を保存したら必ずリロード
   - 表示されている値が実際に保存された値

4. **キャッシュの影響**
   - ブラウザのキャッシュをクリア
   - シークレットウィンドウを使用

---

## 🚨 それでも解決しない場合

### 最終手段1: Production環境を試す

Sandbox環境に問題がある可能性があるため、Production環境でテスト：

**注意**: Production環境では実際のドメインが必要

### 最終手段2: TikTokサポートに問い合わせ

Developer Portal → Support → Create ticket

**問い合わせ内容:**
```
Subject: Sandbox client_key validation error

Description:
I'm trying to use the Sandbox environment for testing, but I'm getting 
"client_key is invalid" error even though:
- Client Key starts with "sbaw"
- Login Kit (Web) is added and changes are applied
- Redirect URI is correctly configured
- Waited more than 10 minutes after configuration

Client Key: sbaw1046rijsqctfgx
App ID: [Your App ID]
Error: client_key is invalid

Please help investigate this issue.
```

---

## 📊 成功の判定基準

### ✅ 成功した場合

認証URLにアクセスすると：
1. TikTokのログイン画面が表示される
2. エラーメッセージが表示されない
3. ユーザー名/パスワード入力欄がある

### ❌ まだ失敗している場合

- `client_key is invalid` → Developer Portal設定を再確認
- `redirect_uri_mismatch` → Redirect URI設定を再確認
- その他のエラー → エラーメッセージを記録して調査

---

**作成日**: 2026-07-12  
**対象**: Sandbox環境の client_key エラー  
**推奨アクション**: 新しいSandboxアプリを作成 → 10分待つ → テスト
