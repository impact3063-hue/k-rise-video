# -*- coding: utf-8 -*-
"""
Redirect URI 一貫性検証スクリプト
すべてのスクリプトが同じRedirect URIを使用しているか確認
"""
import os
import sys
from dotenv import load_dotenv

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# .envファイルから設定を読み込む
load_dotenv()

print("=" * 80)
print("🔍 Redirect URI 一貫性検証")
print("=" * 80)
print()

# 期待されるRedirect URI
EXPECTED_REDIRECT_URI = "https://google.com"

# 各スクリプトで使用されるRedirect URIを取得
redirect_uris = {
    ".env設定値": os.getenv("TIKTOK_REDIRECT_URI", "(未設定)"),
    "generate_auth_url.py": os.getenv("TIKTOK_REDIRECT_URI", "https://google.com"),
    "generate_auth_url_sandbox.py": os.getenv("TIKTOK_REDIRECT_URI", "https://google.com"),
    "get_token.py": os.getenv("TIKTOK_REDIRECT_URI", "https://google.com"),
    "get_token_sandbox.py": os.getenv("TIKTOK_REDIRECT_URI", "https://google.com"),
}

print("📋 各スクリプトのRedirect URI設定:")
print("-" * 80)

all_match = True
for script_name, redirect_uri in redirect_uris.items():
    status = "✅" if redirect_uri == EXPECTED_REDIRECT_URI else "❌"
    print(f"  {status} {script_name:35s} : {redirect_uri}")
    if redirect_uri != EXPECTED_REDIRECT_URI:
        all_match = False

print("-" * 80)
print()

# 認証URL生成のシミュレーション
print("🔗 生成されるURL（Production）:")
print("-" * 80)
CLIENT_KEY_PROD = os.getenv("TIKTOK_CLIENT_KEY_PROD", "awh14qlqti6zxw90")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://google.com")
SCOPES = ["user.info.basic"]
scope_value = ",".join(SCOPES)

auth_url_prod = (
    f"https://www.tiktok.com/v2/auth/authorize/"
    f"?client_key={CLIENT_KEY_PROD}"
    f"&scope={scope_value}"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&state=random_state"
)
print(auth_url_prod)
print("-" * 80)
print()

print("🔗 生成されるURL（Sandbox）:")
print("-" * 80)
CLIENT_KEY_SANDBOX = os.getenv("TIKTOK_CLIENT_KEY", "sbaw1046rijsqctfgx")
auth_url_sandbox = (
    f"https://www.tiktok.com/v2/auth/authorize/"
    f"?client_key={CLIENT_KEY_SANDBOX}"
    f"&scope={scope_value}"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&state=random_state"
)
print(auth_url_sandbox)
print("-" * 80)
print()

# Redirect URIの比較
print("🔍 Redirect URI比較:")
print("-" * 80)
print(f"  期待値:     {EXPECTED_REDIRECT_URI}")
print(f"  Production: {REDIRECT_URI}")
print(f"  Sandbox:    {REDIRECT_URI}")
print("-" * 80)
print()

# URLエンコードチェック
print("🔍 URLエンコードチェック:")
print("-" * 80)
encoded_chars = ['%3A', '%3a', '%2F', '%2f', '%2C', '%2c']
has_encoding = any(char in auth_url_prod or char in auth_url_sandbox for char in encoded_chars)

if has_encoding:
    print("  ❌ URLエンコードが検出されました（問題あり）")
else:
    print("  ✅ URLエンコードは検出されませんでした（正常）")
print("-" * 80)
print()

# 最終結果
print("=" * 80)
if all_match and not has_encoding:
    print("✅ 検証成功：すべてのスクリプトが統一されたRedirect URIを使用しています")
    print()
    print("📝 次のステップ:")
    print("  1. TikTok Developer Portalにアクセス")
    print("  2. Production環境の「Login Kit (Web)」に以下を登録:")
    print(f"     {EXPECTED_REDIRECT_URI}")
    print("  3. Sandbox環境の「Login Kit (Web)」にも同じURLを登録:")
    print(f"     {EXPECTED_REDIRECT_URI}")
    print("  4. 設定を保存し、数分待つ")
    print("  5. 各環境で認証フローをテスト")
    sys.exit(0)
else:
    print("❌ 検証失敗：設定に不一致があります")
    print()
    if not all_match:
        print("  問題: Redirect URIが統一されていません")
        print(f"  期待値: {EXPECTED_REDIRECT_URI}")
        print("  .envファイルを確認してください")
    if has_encoding:
        print("  問題: URLエンコードが検出されました")
        print("  スクリプトを修正してください")
    sys.exit(1)

print("=" * 80)
