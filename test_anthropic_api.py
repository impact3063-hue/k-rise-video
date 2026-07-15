"""
Anthropic API診断スクリプト
APIキーの有効性とアクセス可能なモデルをテストします
"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from anthropic import Anthropic
except ImportError:
    print("[ERROR] anthropic library is not installed.")
    print("Run: pip install anthropic")
    exit(1)

def test_api_key():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not found in .env file")
        return False
    
    print(f"[OK] API Key found: {api_key[:20]}...{api_key[-10:]}")
    print(f"[OK] API Key length: {len(api_key)}")
    
    if not api_key.startswith("sk-ant-"):
        print("[WARNING] API key format looks unusual. Should start with 'sk-ant-'")
    
    client = Anthropic(api_key=api_key)
    
    # テストするモデルのリスト
    test_models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620", 
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229",
        "claude-2.1",
        "claude-2.0",
    ]
    
    print("\n" + "="*60)
    print("Testing models...")
    print("="*60)
    
    working_models = []
    
    for model in test_models:
        try:
            print(f"\n[TEST] {model}...", end=" ")
            response = client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            print("[SUCCESS]")
            working_models.append(model)
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not_found" in error_msg:
                print("[FAIL] Model not found (404)")
            elif "401" in error_msg or "authentication" in error_msg.lower():
                print("[FAIL] Authentication error")
            elif "403" in error_msg or "permission" in error_msg.lower():
                print("[FAIL] Permission denied")
            else:
                print(f"[FAIL] {error_msg[:80]}")
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    if working_models:
        print(f"\n[SUCCESS] {len(working_models)} model(s) working:")
        for model in working_models:
            print(f"  - {model}")
        return True
    else:
        print("\n[ERROR] No models are accessible with this API key.")
        print("\nPossible causes:")
        print("1. API key is invalid or has been revoked")
        print("2. Anthropic account has no active billing/payment method")
        print("3. API key is from a free trial that has expired")
        print("4. Account has usage limits or restrictions")
        print("\nNext steps:")
        print("1. Visit https://console.anthropic.com/")
        print("2. Check your account status and billing")
        print("3. Generate a new API key if needed")
        print("4. Update the ANTHROPIC_API_KEY in your .env file")
        return False

if __name__ == "__main__":
    print("Anthropic API Diagnostic Tool")
    print("="*60)
    test_api_key()
