#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sandbox Client Key の有効性を直接検証
Developer Portalの設定が正しく反映されているかを確認
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://google.com")

print("=" * 80)
print("🔍 Sandbox Client Key 完全検証")
print("=" * 80)

# 環境変数チェック
print("\n📋 環境変数の確認:")
print("-" * 80)

issues = []

if not CLIENT_KEY:
    print("  ❌ TIKTOK_CLIENT_KEY が設定されていません")
    issues.append("CLIENT_KEY未設定")
else:
    print(f"  ✅ Client Key: {CLIENT_KEY}")
    if not CLIENT_KEY.startswith("sbaw"):
        print("  ⚠️  警告: Client Keyが 'sbaw' で始まっていません")
        print("     これはSandbox用のClient Keyではない可能性があります")
        issues.append("Client KeyがSandbox用ではない")

if not CLIENT_SECRET:
    print("  ❌ TIKTOK_CLIENT_SECRET が設定されていません")
    issues.append("CLIENT_SECRET未設定")
else:
    print(f"  ✅ Client Secret: {'*' * 20}{CLIENT_SECRET[-4:]}")

print(f"  ✅ Redirect URI: {REDIRECT_URI}")

print("-" * 80)

if issues:
    print("\n❌ 環境変数に問題があります:")
    for issue in issues:
        print(f"  - {issue}")
    print("\n.envファイルを確認してください")
    sys.exit(1)

# 認証URLを構築（複数パターン）
print("\n🔧 認証URLの生成:")
print("-" * 80)

# パターン1: 基本的なURL（user.info.basicのみ）
auth_url_basic = (
    f"https://www.tiktok.com/v2/auth/authorize/"
    f"?client_key={CLIENT_KEY}"
    f"&scope=user.info.basic"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&state=test_basic"
)

print("\n【パターン1】基本スコープのみ:")
print(auth_url_basic)

# パターン2: 複数スコープ
auth_url_multi = (
    f"https://www.tiktok.com/v2/auth/authorize/"
    f"?client_key={CLIENT_KEY}"
    f"&scope=user.info.basic,video.upload"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&state=test_multi"
)

print("\n【パターン2】複数スコープ:")
print(auth_url_multi)

# URLの詳細分析
print("\n" + "=" * 80)
print("🔍 URL構造の詳細分析:")
print("=" * 80)

print("\n✅ 使用しているパラメータ:")
print(f"  - ベースURL: https://www.tiktok.com/v2/auth/authorize/")
print(f"  - client_key: {CLIENT_KEY}")
print(f"  - scope: user.info.basic")
print(f"  - response_type: code")
print(f"  - redirect_uri: {REDIRECT_URI}")
print(f"  - state: test_basic")

print("\n✅ 正しい仕様:")
print("  - パラメータ名: 'client_key' (client_idではない)")
print("  - 認証URL: 本番環境と同じURL")
print("  - Client Key: 'sbaw' で始まる")
print("  - URLエンコード: 不要（ブラウザが自動処理）")

print("\n" + "=" * 80)
print("📊 Developer Portal 設定チェックリスト:")
print("=" * 80)

checklist = [
    ("Sandboxアプリを作成済み", "https://developers.tiktok.com/apps/"),
    ("Client Keyが 'sbaw' で始まる", "App details タブで確認"),
    ("Login Kit (Web) を追加済み", "Products タブで確認"),
    ("「Apply changes」ボタンを押した", "Products タブ下部"),
    ("Redirect URI を設定済み", "Login Kit (Web) → Redirect URI"),
    ("「Save」ボタンを押した", "Redirect URI設定後"),
    ("ページをリロードして確認", "設定が保存されているか確認"),
    ("設定から10分以上経過", "TikTokサーバーへの反映待ち"),
]

print("\n以下を全て確認してください:\n")
for i, (item, note) in enumerate(checklist, 1):
    print(f"  {i}. [ ] {item}")
    print(f"      → {note}")

print("\n" + "=" * 80)
print("🧪 テスト手順:")
print("=" * 80)

print("\n【ステップ1】シークレットウィンドウで認証URLを開く")
print("\n  推奨URL（基本スコープ）:")
print(f"  {auth_url_basic}")

print("\n【ステップ2】結果を確認")
print("\n  ✅ 成功パターン:")
print("     - TikTokログイン画面が表示される")
print("     - ユーザー名/パスワード入力欄がある")
print("     - エラーメッセージが表示されない")

print("\n  ❌ 失敗パターン1: 'client_key is invalid'")
print("     原因:")
print("     - Developer Portalで「Apply changes」を押していない")
print("     - Login Kit (Web) が正しく追加されていない")
print("     - 設定反映の待機時間が不足（10分以上待つ）")
print("     - Client Keyが間違っている")
print("\n     対策:")
print("     1. Developer Portal → Products → 「Apply changes」を確認")
print("     2. 10分待つ")
print("     3. 新しいSandboxアプリを作成")

print("\n  ❌ 失敗パターン2: 'redirect_uri_mismatch'")
print("     原因:")
print("     - Redirect URIが完全一致していない")
print("     - Developer Portalで「Save」を押していない")
print("\n     対策:")
print("     1. Login Kit (Web) → Redirect URI を確認")
print("     2. 完全一致を確認（末尾のスラッシュも含めて）")
print("     3. 「Save」→ ページリロード → 確認")

print("\n  ❌ 失敗パターン3: その他のエラー")
print("     対策:")
print("     1. エラーメッセージをコピー")
print("     2. SANDBOX_CLIENT_KEY_DIAGNOSIS.md を参照")
print("     3. TikTokサポートに問い合わせ")

print("\n" + "=" * 80)
print("🔄 推奨される解決フロー:")
print("=" * 80)

print("\n【最も確実な方法】新しいSandboxアプリを作成")
print("\n  1. Developer Portal で新しいSandboxアプリを作成")
print("  2. Login Kit (Web) を追加 → 「Apply changes」")
print("  3. Redirect URI を設定 → 「Save」")
print("  4. 新しいClient Key/Secretを.envに設定")
print("  5. 10分待つ")
print("  6. このスクリプトを再実行")
print("  7. 生成されたURLをテスト")

print("\n" + "=" * 80)
print("💾 次のアクション:")
print("=" * 80)

print("\n1. 上記のチェックリストを全て確認")
print("2. Developer Portalの設定を再確認")
print("3. 10分待つ")
print("4. 以下のURLをシークレットウィンドウで開く:")
print()
print("   " + auth_url_basic)
print()
print("5. 結果を報告:")
print("   - 成功 → get_token_sandbox.py を実行")
print("   - 失敗 → SANDBOX_CLIENT_KEY_DIAGNOSIS.md を参照")

print("\n" + "=" * 80)
print("📚 参考ドキュメント:")
print("=" * 80)
print("  - SANDBOX_CLIENT_KEY_DIAGNOSIS.md (詳細な診断)")
print("  - TIKTOK_CLIENT_KEY_FIX.md (修正履歴)")
print("  - TIKTOK_SANDBOX_AUTH_SOLUTION.md (認証フロー)")
print("=" * 80)

# URLをクリップボードにコピー（オプション）
try:
    import pyperclip
    pyperclip.copy(auth_url_basic)
    print("\n✅ 基本URLをクリップボードにコピーしました！")
except ImportError:
    print("\n💡 pyperclip をインストールすると、URLを自動コピーできます")
    print("   pip install pyperclip")
except Exception:
    pass

print()
