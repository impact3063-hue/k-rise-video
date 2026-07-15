# -*- coding: utf-8 -*-
"""
TikTok Production トークン取得スクリプト
本番環境（Production）用のアクセストークンを取得します
"""
import requests
import os
import sys
import json
from dotenv import load_dotenv

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# .envファイルから設定を読み込む
load_dotenv()

# Production環境の設定
# 注意: 本番用のClient Keyは 'aw' で始まります（'sbaw' はSandbox用）
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY_PROD", os.getenv("TIKTOK_CLIENT_KEY", ""))
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET_PROD", os.getenv("TIKTOK_CLIENT_SECRET", ""))
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://google.com")

# Scopeの設定（generate_auth_url.pyと一致させる）
SCOPES = [
    "user.info.basic",
    "video.upload",
    "video.publish",
]

print("=" * 80)
print("🚀 TikTok Production トークン取得")
print("=" * 80)

# 設定の検証
print("\n📋 現在の設定:")
print("-" * 80)
print(f"  Client Key:     {CLIENT_KEY}")
print(f"  Client Secret:  {'*' * 20 if CLIENT_SECRET else '(未設定)'}")
print(f"  Redirect URI:   {REDIRECT_URI}")
print(f"  Scopes:         {', '.join(SCOPES)}")
print("-" * 80)

if not CLIENT_KEY or not CLIENT_SECRET:
    print("\n❌ エラー: Client KeyまたはClient Secretが設定されていません")
    print("   .envファイルに以下を設定してください:")
    print("   TIKTOK_CLIENT_KEY_PROD=your_production_client_key")
    print("   TIKTOK_CLIENT_SECRET_PROD=your_production_client_secret")
    sys.exit(1)

if CLIENT_KEY.startswith("sbaw"):
    print("\n⚠️  警告: Sandbox用のClient Keyが検出されました")
    print("   本番環境用のClient Key ('aw' で始まる) を使用してください")
    print()
    response = input("このまま続行しますか？ (y/N): ")
    if response.lower() != 'y':
        print("中断しました")
        sys.exit(1)

print("\n" + "=" * 80)
print("【ステップ1】 認証URLを生成")
print("=" * 80)

# 認証URL生成（client_keyパラメータを使用）
scope_value = ",".join(SCOPES)
auth_url = (
    f"https://www.tiktok.com/v2/auth/authorize/"
    f"?client_key={CLIENT_KEY}"
    f"&scope={scope_value}"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&state=random_state"
)

print("\n以下のURLをブラウザで開いてください:")
print("-" * 80)
print(auth_url)
print("-" * 80)
print("\n【手順】")
print("1. 上記URLをコピーしてブラウザで開く")
print("2. TikTokアカウントでログイン・承認")
print("3. リダイレクトされたGoogleのURL全体をコピー")
print("4. 下記のプロンプトに貼り付けてEnterを押す")
print("=" * 80)

# ユーザーからリダイレクトURLを取得
redirect_url = input("\nリダイレクトされたURL全体を貼り付けてください: ").strip()

# URLからcodeパラメータを抽出
if "code=" in redirect_url:
    code = redirect_url.split("code=")[1].split("&")[0]
    print(f"\n✅ 認証コードを抽出しました: {code[:20]}...")
    
    print("\n" + "=" * 80)
    print("【ステップ2】 アクセストークンを取得")
    print("=" * 80)
    
    # トークン取得の実行（本番環境のエンドポイント）
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }
    
    print(f"\n📡 リクエスト送信中: {token_url}")
    print(f"   Client Key: {CLIENT_KEY}")
    print(f"   Grant Type: authorization_code")
    print(f"   Redirect URI: {REDIRECT_URI}")
    
    try:
        response = requests.post(token_url, headers=headers, data=data, timeout=30)
        
        print(f"\n📥 レスポンス受信:")
        print(f"   ステータスコード: {response.status_code}")
        
        result = response.json()
        
        print("\n【API レスポンス】")
        print("-" * 80)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("-" * 80)
        
        if "access_token" in result:
            print("\n✅ トークン取得成功!")
            
            # open_idも取得できた場合は表示
            open_id = result.get("open_id", "")
            
            print("\n【ステップ3】 .envファイルを更新してください")
            print("-" * 80)
            print(f"TIKTOK_ACCESS_TOKEN={result['access_token']}")
            print(f"TIKTOK_REFRESH_TOKEN={result['refresh_token']}")
            print(f"TIKTOK_TOKEN_EXPIRES_IN={result['expires_in']}")
            if open_id:
                print(f"TIKTOK_OPEN_ID={open_id}")
            print("-" * 80)
            print("\n上記の行を .env ファイルに追加・更新してください。")
            
            # トークン情報の詳細
            print("\n📊 トークン情報:")
            print("-" * 80)
            print(f"  アクセストークン: {result['access_token'][:30]}...")
            print(f"  リフレッシュトークン: {result['refresh_token'][:30]}...")
            print(f"  有効期限: {result['expires_in']} 秒 ({result['expires_in'] // 3600} 時間)")
            if open_id:
                print(f"  Open ID: {open_id}")
            print(f"  トークンタイプ: {result.get('token_type', 'Bearer')}")
            if 'scope' in result:
                print(f"  付与されたスコープ: {result['scope']}")
            print("-" * 80)
            
            print("\n✅ 次のステップ:")
            print("  1. 上記のトークン情報を .env ファイルに保存")
            print("  2. python test_tiktok_connection.py を実行して接続をテスト")
            print("  3. 問題なければ python upload_tiktok_auto.py で動画をアップロード")
            
        elif "error" in result:
            print("\n❌ トークン取得失敗")
            error_code = result.get("error", "unknown")
            error_description = result.get("error_description", "詳細不明")
            
            print(f"\n🔍 エラー詳細:")
            print(f"   エラーコード: {error_code}")
            print(f"   説明: {error_description}")
            
            print("\n💡 トラブルシューティング:")
            if "invalid_client" in error_code:
                print("  - Client KeyまたはClient Secretが間違っています")
                print("  - Developer Portalで正しい値を確認してください")
            elif "invalid_grant" in error_code:
                print("  - 認証コードが無効または期限切れです")
                print("  - 認証コードは1回のみ使用可能で、数分で期限切れになります")
                print("  - generate_auth_url.py を再実行して新しいコードを取得してください")
            elif "redirect_uri_mismatch" in error_code:
                print("  - Redirect URIが一致しません")
                print("  - Developer Portalに登録されているRedirect URIと一致させてください")
            else:
                print("  - Developer Portalの設定を確認してください")
                print("  - 本番環境の場合、App Reviewが承認されているか確認してください")
        else:
            print("\n❌ 予期しないレスポンス形式")
            print("エラー内容を確認してください。")
            
    except requests.exceptions.Timeout:
        print("\n❌ リクエストがタイムアウトしました")
        print("   ネットワーク接続を確認してください")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ リクエストエラー: {e}")
    except json.JSONDecodeError:
        print("\n❌ レスポンスのJSON解析に失敗しました")
        print(f"   生のレスポンス: {response.text}")
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n❌ URLに 'code=' パラメータが見つかりません")
    print("正しいリダイレクトURLを貼り付けてください。")
    print("\n例: https://google.com/?code=ABC123&state=random_state&scopes=...")

print("\n" + "=" * 80)