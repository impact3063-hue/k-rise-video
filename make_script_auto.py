import os
import json
import sys
from dotenv import load_dotenv

# Windows環境でのUnicode出力を修正
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# .env ファイルからAPIキーなどの環境変数を読み込む
load_dotenv()

from anthropic import Anthropic

def load_video_config():
    config_file = "video_config.json"
    default_config = {
        "industry": "K-POPオーディション",
        "theme": "BTSを日本進出させた伝説のプロデューサー出口氏が直々に審査してくれる特別なチャンス",
        "target_audience": "K-POPの世界を目指す人、オーディションで絶対に失敗したくない人",
        "tone_style": "熱量が高く、説得力があり、思わず最後まで見てしまうバズるトーン",
        "cta_text": "次は君の番かもしれない。応募はLINEから！プロフィールのリンクをチェックしてね！",
        "length_limit": "150文字〜180文字程度"
    }

    if not os.path.exists(config_file):
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        return default_config

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load config. Using defaults. Error: {e}")
        return default_config

def generate_daily_script():
    """Claude Sonnet 5を使用してスクリプトを生成"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERROR] Anthropic API key is not set.")
        return False

    print(f"[OK] Anthropic API Key loaded: {api_key[:20]}...{api_key[-10:]}")
    
    client = Anthropic(api_key=api_key)
    config = load_video_config()
    
    prompt = f"""
あなたはSNS（TikTok/Instagram/YouTube Shorts）のショート動画プロモーション台本を作成する超一流のAIエージェントです。
特に日本語の「バズる心理トリガー」や「感情を揺さぶる表現」を熟知しています。

以下の設定シート（スタッフが書き換えたもの）を読み込み、視聴者が1秒目でスクロールを止め、最後まで見てしまうナレーション台本を1つ作成してください。

【設定シート】
■ 業界ジャンル: {config.get("industry")}
■ 動画の訴求テーマ: {config.get("theme")}
■ ターゲット視聴者: {config.get("target_audience")}
■ 文章 of トーン: {config.get("tone_style")}
■ 文字数制限: {config.get("length_limit")}

【絶対ルール】
1. ナレーションの最後は、必ず寸分違わず以下のテキストで締めくくってください。
「{config.get("cta_text")}」
※途中で切ったり、ニュアンスを変えたり、改行を入れたりしないでください。

2. 出力は、確実に指定した日本語 of ナレーションのみを含むJSON形式で返してください。
{{
  "narration_body": "ここに作成したナレーション台本を記入"
}}
"""

    try:
        print(f"[INFO] Using model: claude-sonnet-5")
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1000,
            system="あなたは返答を必ず純粋なJSONオブジェクトのみで出力するシステムです。説明テキストは一切出力しません。",
            messages=[{"role": "user", "content": prompt}]
        )
        
        print(f"[SUCCESS] Claude Sonnet 5 responded successfully!")
        
        # Claude Sonnet 5はThinkingBlockを含む可能性があるため、TextBlockのみを抽出
        res_text = ""
        for block in response.content:
            if type(block).__name__ == 'TextBlock':
                res_text = block.text.strip()
                break
        
        if not res_text:
            raise Exception(f"No text content found in response. Content blocks: {[type(b).__name__ for b in response.content]}")
        
        if res_text.startswith("```json"):
            res_text = res_text[7:]
        if res_text.startswith("```"):
            res_text = res_text[3:]
        if res_text.endswith("```"):
            res_text = res_text[:-3]
            
        data = json.loads(res_text.strip())
        
        with open("today_script.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        with open("today_script.txt", "w", encoding="utf-8") as f:
            f.write(data["narration_body"])
            
        print("\n✨ Claude Sonnet 5が完璧なバズ台本を作成し、保存しました！")
        print(data["narration_body"])
        return True
        
    except Exception as e:
        print(f"[ERROR] Claude API failed: {e}")
        print("\nPlease check:")
        print("1. Your API key is valid and not expired")
        print("2. Your Anthropic account has access to Claude Sonnet 5")
        print("3. Billing is set up correctly")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Script Generation Starting with Claude Sonnet 5...")
    print("="*60)
    generate_daily_script()