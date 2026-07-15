# -*- coding: utf-8 -*-
"""
TikTok Production 認証URL生成スクリプト
本番環境（Production）専用の認証URLを生成します
"""
import os
import sys
from dotenv import load_dotenv

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# .envファイルから設定を読み込む
load_dotenv()

# Production環境の設定
# 注意: 本番用のClient Keyは 'aw' で始まります（'sbaw' はSandbox用）
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY_PROD", os.getenv("TIKTOK_CLIENT_KEY", ""))
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://google.com")

# Scopeの設定（必要に応じて追加）
# ⚠️ App Review前のテスト用: user.info.basic のみに制限
# App Review承認後は video.upload, video.publish を追加してください
SCOPES = [
    "user.info.basic",           # ユーザー基本情報（必須・App Review不要）
    # "video.upload",            # 動画アップロード（App Review必要）
    # "video.publish",           # 動画公開（App Review必要）
]

print("=" * 80)
print("🚀 TikTok Production 認証URL生成")
print("=" * 80)

print("\n📋 現在の設定:")
print("-" * 80)
print(f"  Client Key:    {CLIENT_KEY}")
print(f"  Redirect URI:  {REDIRECT_URI}")
print(f"  Scopes:        {', '.join(SCOPES)}")
print("-" * 80)

# Client Keyの検証
if not CLIENT_KEY:
    print("\n❌ エラー: Client Keyが設定されていません")
    print("   .envファイルに TIKTOK_CLIENT_KEY_PROD を設定してください")
    print("   または TIKTOK_CLIENT_KEY に本番用のClient Keyを設定してください")
    sys.exit(1)

if CLIENT_KEY.startswith("sbaw"):
    print("\n⚠️  警告: Sandbox用のClient Keyが検出されました")
    print("   本番環境用のClient Key ('aw' で始まる) を使用してください")
    print("   現在のClient Key: " + CLIENT_KEY)
    print()
    response = input("このまま続行しますか？ (y/N): ")
    if response.lower() != 'y':
        print("中断しました")
        sys.exit(1)

# Production用の認証URL生成
# 重要: 認証URLは本番・Sandbox共通（Client Keyで環境が判別される）
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

print("\n✅ Production認証URLを生成しました:")
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
print("    → 本番環境とSandbox環境で同じURLを使用（これが正しい仕様です）")
print()
print("  ✓ API URL: https://open.tiktokapis.com/v2/")
print("    → トークン取得やAPI呼び出しは本番環境のURLを使用")
print()
print("  ✓ Client Key: aw で始まる（Production専用）")
print("    → sbaw で始まる場合はSandbox用です")
print()
print("  ✓ パラメータ名: client_key を使用（TikTok API v2の正式仕様）")
print("-" * 80)

print("\n⚠️  本番環境の注意事項:")
print("-" * 80)
print("  ⚠️  App Reviewが必要です")
print("     - video.upload と video.publish スコープを使用するには")
print("     - TikTok Developer Portalで App Review を申請・承認される必要があります")
print()
print("  ⚠️  本番のTikTokアカウントに投稿されます")
print("     - テストではなく、実際のTikTokアカウントに動画が投稿されます")
print()
print("  ⚠️  Redirect URIの登録が必要です")
print("     - Developer Portalの「Production」タブで Redirect URI を登録してください")
print("-" * 80)

print("\n=" * 80)
print("📝 次の手順:")
print("=" * 80)
print("1. 上記のProduction認証URLをコピー")
print("2. ブラウザで開く")
print("3. TikTokアカウントでログイン・承認")
print("4. リダイレクトされたGoogle URLをコピー")
print("   例: https://google.com/?code=ABC123&state=random_state&scopes=...")
print("5. 次のコマンドを実行:")
print("   python get_token.py")
print("6. リダイレクトURLを貼り付け")
print("=" * 80)

print("\n💡 ヒント:")
print("  - 本番環境では、実際のTikTokアカウントを使用します")
print("  - Client Keyは 'aw' で始まる必要があります（'sbaw' はSandbox用）")
print("  - Redirect URIはDeveloper Portalの「Production」タブに登録されている必要があります")
print("  - TikTok API v2では 'client_key' パラメータを使用します（client_idではない）")
print("  - App Reviewが承認されていない場合、video.upload/video.publish は使用できません")
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
