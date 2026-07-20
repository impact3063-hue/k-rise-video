# Roo Code 0%フリーズ自己修復スキル（ripgrep消失バグ）

## 症状
Roo Codeが「API Request... 0%」で固まる。認証・残高・通信を疑う前にまずコレ。

## 診断（1コマンド・10秒以内・他ファイル読み込み禁止）
```bash
grep -m1 'Could not find ripgrep' "$(ls -td /c/Users/user/AppData/Roaming/Code/logs/*/ | head -1)/window1/exthost/exthost.log"
```
ヒットしたら原因確定：VS Code自動更新でインストールフォルダ名が変わり（例: 125df4672b→8a7abeba6e）、配置済みrg.exeが消失。

## 修復（1コマンド・即実行可）
```bash
APP=$(ls -d "/c/Users/user/AppData/Local/Programs/Microsoft VS Code/"*/resources/app | head -1); for b in "$APP/node_modules/@vscode/ripgrep/bin" "$APP/node_modules.asar.unpacked/@vscode/ripgrep/bin"; do mkdir -p "$b" && cp /c/Users/user/rg.exe "$b/rg.exe"; done && "$APP/node_modules/@vscode/ripgrep/bin/rg.exe" --version
```
成功したらVS Code完全再起動。以上。

## 過去の実績
- 2026-07-17: 初回発生。rg.exe配置+ユーザーPATHにC:\Users\userを追加済み
- 2026-07-19: VS Code自動更新で再発。上記コマンドで10秒修復
- rg.exe本体: C:\Users\user\rg.exe (ripgrep 15.2.0)

## 禁止事項
- ファイル全スキャン・広範囲grep禁止（トークン浪費）
- tasks/cache/state.vscdbの削除はこのバグには無関係（先にripgrep確認）
