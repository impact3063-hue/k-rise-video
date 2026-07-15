# -*- coding: utf-8 -*-
"""
TikTok Sandbox トークン取得スクリプト
リダイレクトURLから認証コードを抽出し、アクセストークンを取得します
"""
import os
import sys
import json
import requests
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# .envファイルから設定を読み込む
load_dotenv()

# Sandbox環境の設定
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "sbaw1046rijsqctfgx")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://google.com")

# Sandbox API エンドポイント
SANDBOX_TOKEN_URL = "https://sandbox-open.tiktokapis.com/v2/oauth/token/"

print("=" * 80)
print("🔧 TikTok Sandbox トークン取得")
print("=" * 80)

# Client Secretの確認
if not CLIENT_SECRET:
    print("\n⚠️  エラー: TIKTOK_CLIENT_SECRET が設定されていません")
    print()
    print("📝 設定方法:")
    print("1. TikTok Developer Portal にアクセス")
    print("   https://developers.tiktok.com/apps/")
    print("2. アプリを選択")
    print("3. 'App details' から 'Client secret' をコピー")
    print("4. .env ファイルに追加:")
    print("   TIKTOK_CLIENT_SECRET=your_client_secret_here")
    print()
    sys.exit(1)

print("\n📋 現在の設定:")
print("-" * 80)
print(f"  Client Key:    {CLIENT_KEY}")
print(f"  Client Secret: {'*' * 20}{CLIENT_SECRET[-4:] if len(CLIENT_SECRET) > 4 else '未設定'}")
print(f"  Redirect URI:  {REDIRECT_URI}")
print(f"  Token URL:     {SANDBOX_TOKEN_URL}")
print("-" * 80)

# リダイレクトURLの入力
print("\n📥 リダイレクトURLを入力してください:")
print("   例: https://google.com/?code=ABC123&state=random_state&scopes=user.info.basic")
print()
redirect_url = input("URL: ").strip()

if not redirect_url:
    print("❌ URLが入力されていません")
    sys.exit(1)

# URLをパース
try:
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    
    # 認証コードを取得
    if 'code' not in query_params:
        print("❌ エラー: URLに認証コード (code) が含まれていません")
        print(f"   入力されたURL: {redirect_url}")
        sys.exit(1)
    
    auth_code = query_params['code'][0]
    state = query_params.get('state', [''])[0]
    scopes = query_params.get('scopes', [''])[0]
    
    print("\n✅ 認証コードを抽出しました:")
    print("-" * 80)
    print(f"  Code:   {auth_code[:20]}...")
    print(f"  State:  {state}")
    print(f"  Scopes: {scopes}")
    print("-" * 80)
    
except Exception as e:
    print(f"❌ エラー: URLのパースに失敗しました: {e}")
    sys.exit(1)

# アクセストークンを取得
print("\n🔄 アクセストークンを取得中...")
print("-" * 80)

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Cache-Control": "no-cache"
}

data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "code": auth_code,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI
}

try:
    response = requests.post(SANDBOX_TOKEN_URL, headers=headers, data=data, timeout=30)
    
    print(f"  ステータスコード: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        
        print("\n✅ トークン取得成功！")
        print("=" * 80)
        print(json.dumps(token_data, indent=2, ensure_ascii=False))
        print("=" * 80)
        
        # トークン情報を抽出
        access_token = token_data.get('access_token', '')
        refresh_token = token_data.get('refresh_token', '')
        expires_in = token_data.get('expires_in', 0)
        open_id = token_data.get('open_id', '')
        scope = token_data.get('scope', '')
        token_type = token_data.get('token_type', '')
        
        # .envファイルに追加する内容を表示
        print("\n📝 .env ファイルに以下を追加してください:")
        print("=" * 80)
        print(f"TIKTOK_ACCESS_TOKEN={access_token}")
        print(f"TIKTOK_REFRESH_TOKEN={refresh_token}")
        print(f"TIKTOK_OPEN_ID={open_id}")
        print(f"TIKTOK_TOKEN_EXPIRES_IN={expires_in}")
        print("=" * 80)
        
        # 自動的に.envファイルを更新するか確認
        print("\n💾 .env ファイルを自動的に更新しますか？")
        print("   (既存の値は上書きされます)")
        response_update = input("更新する (y/N): ").strip().lower()
        
        if response_update == 'y':
            try:
                # .envファイルを読み込む
                env_path = ".env"
                env_lines = []
                
                if os.path.exists(env_path):
                    with open(env_path, 'r', encoding='utf-8') as f:
                        env_lines = f.readlines()
                
                # 既存の値を更新または追加
                keys_to_update = {
                    'TIKTOK_ACCESS_TOKEN': access_token,
                    'TIKTOK_REFRESH_TOKEN': refresh_token,
                    'TIKTOK_OPEN_ID': open_id,
                    'TIKTOK_TOKEN_EXPIRES_IN': str(expires_in)
                }
                
                updated_keys = set()
                new_lines = []
                
                for line in env_lines:
                    updated = False
                    for key, value in keys_to_update.items():
                        if line.startswith(f"{key}="):
                            new_lines.append(f"{key}={value}\n")
                            updated_keys.add(key)
                            updated = True
                            break
                    if not updated:
                        new_lines.append(line)
                
                # 新しいキーを追加
                for key, value in keys_to_update.items():
                    if key not in updated_keys:
                        new_lines.append(f"{key}={value}\n")
                
                # .envファイルに書き込む
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                
                print("✅ .env ファイルを更新しました！")
                
            except Exception as e:
                print(f"❌ .env ファイルの更新に失敗しました: {e}")
                print("   手動で上記の内容を .env ファイルに追加してください")
        
        print("\n📊 トークン情報:")
        print("-" * 80)
        print(f"  Token Type:  {token_type}")
        print(f"  Expires In:  {expires_in} 秒 ({expires_in // 3600} 時間)")
        print(f"  Scope:       {scope}")
        print("-" * 80)
        
        print("\n✅ 次のステップ:")
        print("=" * 80)
        print("1. トークンが .env ファイルに保存されていることを確認")
        print("2. API接続をテスト:")
        print("   python test_tiktok_connection_sandbox.py")
        print("3. 動画アップロードをテスト:")
        print("   python upload_tiktok_auto.py")
        print("=" * 80)
        
    else:
        print(f"\n❌ トークン取得失敗 (HTTP {response.status_code})")
        print("=" * 80)
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        print("=" * 80)
        
        print("\n🔍 トラブルシューティング:")
        print("-" * 80)
        print("1. Client Secret が正しいか確認")
        print("2. 認証コードが期限切れでないか確認（通常5分で期限切れ）")
        print("3. Redirect URI が Developer Portal の設定と一致しているか確認")
        print("4. 新しい認証コードを取得:")
        print("   python generate_auth_url_sandbox.py")
        print("-" * 80)
        
        sys.exit(1)

except requests.exceptions.Timeout:
    print("❌ リクエストタイムアウト")
    sys.exit(1)
except requests.exceptions.RequestException as e:
    print(f"❌ リクエストエラー: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 予期しないエラー: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
