# -*- coding: utf-8 -*-
"""
TikTok Sandbox 認証URL生成スクリプト
Sandbox環境専用の認証URLを生成します
"""
import os
import sys
from dotenv import load_dotenv
import urllib.parse

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# .envファイルから設定を読み込む
load_dotenv()

# Sandbox環境の設定
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "sbaw1046rijsqctfgx")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://google.com")

# Scopeの設定（必要に応じて追加）
SCOPES = [
    "user.info.basic",           # ユーザー基本情報（必須）
    # "video.upload",            # 動画アップロード（必要な場合）
    # "video.publish",           # 動画公開（必要な場合）
]

print("=" * 80)
print("🔧 TikTok Sandbox 認証URL生成")
print("=" * 80)

print("\n📋 現在の設定:")
print("-" * 80)
print(f"  Client Key:    {CLIENT_KEY}")
print(f"  Redirect URI:  {REDIRECT_URI}")
print(f"  Scopes:        {', '.join(SCOPES)}")
print("-" * 80)

# Client Keyの検証
if not CLIENT_KEY.startswith("sbaw"):
    print("\n⚠️  警告: Client Keyが 'sbaw' で始まっていません")
    print("   Sandbox環境用のClient Keyは 'sbaw' で始まる必要があります")
    print("   本番環境用のClient Key ('aw' で始まる) を使用していませんか？")
    print()
    response = input("このまま続行しますか？ (y/N): ")
    if response.lower() != 'y':
        print("中断しました")
        sys.exit(1)

# Sandbox用の認証URL生成
# 重要: 認証URLは本番環境と同じものを使用（APIエンドポイントのみSandbox用）
# 参考: https://developers.tiktok.com/doc/sandbox-environment
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"

# パラメータの構築
# 重要: TikTok API v2では "client_key" を使用（"client_id" ではない）
# 公式ドキュメント: https://developers.tiktok.com/doc/login-kit-web
# 重要: すべてのパラメータをURLエンコードせず、生の文字列のまま使用
# （ブラウザが自動的に適切にエンコードするため）

# すべてのパラメータを生の文字列として構築（URLエンコードしない）
scope_value = ",".join(SCOPES)

# 完全なURLを手動構築（エンコードなし）
# 注意: client_key パラメータを使用（client_id ではない）
auth_url = (
    f"{AUTH_URL}"
    f"?client_key={CLIENT_KEY}"
    f"&scope={scope_value}"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&state=random_state"
)

print("\n✅ Sandbox認証URLを生成しました:")
print("=" * 80)
print("【生成されたURL（エンコードなし）】")
print(auth_url)
print("=" * 80)

# URLの各パラメータを個別に表示して検証
print("\n🔍 URLパラメータの詳細検証:")
print("-" * 80)
print(f"  ベースURL:      {AUTH_URL}")
print(f"  client_key:     {CLIENT_KEY}")
print(f"  scope:          {scope_value}")
print(f"  response_type:  code")
print(f"  redirect_uri:   {REDIRECT_URI}")
print(f"  state:          random_state")
print("-" * 80)

# 期待される完全一致の確認
expected_url = (
    "https://www.tiktok.com/v2/auth/authorize/"
    f"?client_key={CLIENT_KEY}"
    f"&scope={scope_value}"
    "&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    "&state=random_state"
)

print("\n✅ 期待されるURL（完全一致確認）:")
print("-" * 80)
print(expected_url)
print("-" * 80)

if auth_url == expected_url:
    print("\n✅ 生成URLと期待URLが完全一致しています！")
else:
    print("\n⚠️  警告: 生成URLと期待URLが一致しません")
    print(f"   差分を確認してください")

print("\n📊 URL文字列の詳細情報:")
print("-" * 80)
print(f"  URL長:          {len(auth_url)} 文字")
print(f"  エンコード確認: '%3A' が含まれる = {('%3A' in auth_url) or ('%3a' in auth_url)}")
print(f"  エンコード確認: '%2F' が含まれる = {('%2F' in auth_url) or ('%2f' in auth_url)}")
print(f"  エンコード確認: '%2C' が含まれる = {('%2C' in auth_url) or ('%2c' in auth_url)}")
if ('%3A' in auth_url) or ('%3a' in auth_url) or ('%2F' in auth_url) or ('%2f' in auth_url):
    print("  ⚠️  URLエンコードが検出されました！")
else:
    print("  ✅ URLエンコードは検出されませんでした")
print("-" * 80)

print("\n🔍 重要なポイント:")
print("-" * 80)
print("  ✓ 認証URL: https://www.tiktok.com/v2/auth/authorize/")
print("    → 本番環境と同じURLを使用（これが正しい仕様です）")
print()
print("  ✓ API URL: https://sandbox-open.tiktokapis.com/v2/")
print("    → トークン取得やAPI呼び出しはSandbox専用URLを使用")
print()
print("  ✓ Client Key: sbaw で始まる（Sandbox専用）")
print()
print("  ✓ パラメータ名: client_key を使用（TikTok API v2の正式仕様）")
print("-" * 80)

print("=" * 80)
print("📝 次の手順:")
print("=" * 80)
print("1. 上記のSandbox認証URLをコピー")
print("2. ブラウザで開く")
print("3. TikTokアカウントでログイン・承認")
print("4. リダイレクトされたGoogle URLをコピー")
print("   例: https://google.com/?code=ABC123&state=random_state&scopes=...")
print("5. 次のコマンドを実行:")
print("   python get_token_sandbox.py")
print("6. リダイレクトURLを貼り付け")
print("=" * 80)

print("\n💡 ヒント:")
print("  - Sandbox環境では、テスト用のTikTokアカウントが必要です")
print("  - Client Keyは 'sbaw' で始まる必要があります")
print("  - Redirect URIはDeveloper Portalに登録されている必要があります")
print("  - TikTok API v2では 'client_key' パラメータを使用します（client_idではない）")
print()

# URLをクリップボードにコピー（オプション）
try:
    import pyperclip
    pyperclip.copy(auth_url)
    print("✅ URLをクリップボードにコピーしました！")
except ImportError:
    print("💡 pyperclip をインストールすると、URLを自動的にクリップボードにコピーできます")
    print("   pip install pyperclip")
except Exception:
    pass

print()
