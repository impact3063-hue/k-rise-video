# Anthropic API 問題の診断と解決策

## 問題の概要
`make_script_auto.py` を実行すると、すべてのClaude モデルで404エラーが発生していました。

## 診断結果

### APIキーの状態
- ✅ APIキーは正しく `.env` から読み込まれています
- ✅ APIキーの形式は正しい（`sk-ant-api03-...`、108文字）
- ❌ **すべてのClaudeモデルへのアクセスが拒否されています（404エラー）**

### テストしたモデル
以下のすべてのモデルで404エラーが発生：
1. `claude-3-5-sonnet-20241022` (最新Sonnet)
2. `claude-3-5-sonnet-20240620` (旧Sonnet)
3. `claude-3-haiku-20240307` (Haiku)
4. `claude-3-opus-20240229` (Opus)
5. `claude-2.1` (Claude 2.1)
6. `claude-2.0` (Claude 2.0)

## 根本原因

404エラーは以下のいずれかが原因です：

1. **APIキーが無効化されている**
   - APIキーが取り消された、または期限切れ

2. **Anthropicアカウントに請求情報が設定されていない**
   - 無料トライアルが終了している
   - 支払い方法が登録されていない

3. **アカウントに利用制限がかかっている**
   - 使用量制限に達している
   - アカウントが一時停止されている

## 実装した解決策

### 1. 診断スクリプトの作成
[`test_anthropic_api.py`](test_anthropic_api.py) を作成し、APIキーの状態を詳細に診断できるようにしました。

実行方法：
```bash
python test_anthropic_api.py
```

### 2. OpenAI GPT-4へのフォールバック機能
[`make_script_auto.py`](make_script_auto.py) を更新し、以下の機能を追加：

- ✅ Anthropic APIが失敗した場合、自動的にOpenAI GPT-4にフォールバック
- ✅ 複数のClaudeモデルを順番に試行
- ✅ 詳細なエラーメッセージとデバッグ情報
- ✅ Windows環境でのUnicode出力の修正

### 3. 動作フロー
```
1. Anthropic Claude API を試行
   ├─ claude-3-5-sonnet-20241022
   ├─ claude-3-5-sonnet-20240620
   ├─ claude-3-haiku-20240307
   ├─ claude-3-opus-20240229
   ├─ claude-2.1
   └─ claude-2.0
   
2. すべて失敗 → OpenAI GPT-4 にフォールバック
   └─ ✅ 成功！スクリプト生成完了
```

## Anthropic APIを修正する方法

Anthropic APIを使用したい場合は、以下の手順を実行してください：

### ステップ1: Anthropicコンソールにアクセス
https://console.anthropic.com/

### ステップ2: アカウント状態を確認
- ダッシュボードでアカウントステータスを確認
- 請求情報が設定されているか確認
- 使用量制限を確認

### ステップ3: 請求情報を設定
1. Settings → Billing に移動
2. 支払い方法を追加（クレジットカードなど）
3. 必要に応じてクレジットを購入

### ステップ4: 新しいAPIキーを生成
1. Settings → API Keys に移動
2. 新しいAPIキーを作成
3. `.env` ファイルの `ANTHROPIC_API_KEY` を更新

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-新しいキーをここに貼り付け
```

### ステップ5: テスト
```bash
python test_anthropic_api.py
```

## 現在の状態

✅ **スクリプト生成は正常に動作しています**
- OpenAI GPT-4を使用してスクリプトを生成
- 日本語出力が正しく表示される
- `today_script.json` と `today_script.txt` が正常に保存される

## 使用方法

### スクリプト生成（現在の設定で動作）
```bash
python make_script_auto.py
```

### API診断
```bash
python test_anthropic_api.py
```

## ファイル一覧

- [`make_script_auto.py`](make_script_auto.py) - メインスクリプト（Anthropic + OpenAI フォールバック）
- [`test_anthropic_api.py`](test_anthropic_api.py) - API診断ツール
- [`.env`](.env) - APIキー設定ファイル
- [`ANTHROPIC_API_ISSUE.md`](ANTHROPIC_API_ISSUE.md) - このドキュメント

## まとめ

- ❌ Anthropic APIキーは現在使用できません（404エラー）
- ✅ OpenAI GPT-4へのフォールバックが実装され、正常に動作しています
- ✅ スクリプト生成機能は問題なく使用できます
- 📝 Anthropic APIを使用したい場合は、上記の手順でアカウントを修正してください
