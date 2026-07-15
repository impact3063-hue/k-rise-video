# -*- coding: utf-8 -*-
import requests
import os
import sys
from dotenv import load_dotenv

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# .envファイルから設定を読み込む
load_dotenv()

# 1. あなたの情報をセット
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "sbawl046rijsqctfgx")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "ycxooL6kRrWlFXq8epIlEvBQtk42uQex")
REDIRECT_URI = "https://google.com"

print("=" * 70)
print("[TikTok リダイレクトURL処理]")
print("=" * 70)

# ユーザーからリダイレクトURLを取得
redirect_url = input("\nリダイレクトされたURL全体を貼り付けてください: ").strip()

# URLからcodeパラメータを抽出
if "code=" in redirect_url:
    code = redirect_url.split("code=")[1].split("&")[0]
    print(f"\n✅ 認証コードを抽出しました: {code[:20]}...")
    
    print("\n" + "=" * 70)
    print("【アクセストークンを取得中】")
    print("=" * 70)
    
    # トークン取得の実行
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    result = response.json()
    
    print("\n【API レスポンス】")
    print("-" * 70)
    print(result)
    print("-" * 70)
    
    if "access_token" in result:
        print("\n✅ トークン取得成功!")
        print("\n【.envファイルに追加する内容】")
        print("=" * 70)
        print(f"TIKTOK_ACCESS_TOKEN={result['access_token']}")
        print(f"TIKTOK_REFRESH_TOKEN={result['refresh_token']}")
        print(f"TIKTOK_TOKEN_EXPIRES_IN={result['expires_in']}")
        print("=" * 70)
        print("\n上記の3行を .env ファイルに追加・更新してください。")
    else:
        print("\n❌ トークン取得失敗")
        print("エラー内容を確認してください。")
        if "error" in result:
            print(f"\nエラー: {result.get('error')}")
            print(f"詳細: {result.get('error_description', 'N/A')}")
else:
    print("\n❌ URLに 'code=' パラメータが見つかりません")
    print("正しいリダイレクトURLを貼り付けてください。")
    print(f"\n入力されたURL: {redirect_url}")

print("\n" + "=" * 70)
