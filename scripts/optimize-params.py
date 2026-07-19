#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
📈 K-RISE 演出パラメータ自動最適化 — docs/tiktok-analytics-log.json を解析し、
上位25% vs 下位25% の勝ちパラメータを docs/params-current.json に反映する。
週1回（または毎晩）実行想定。10%の確率で1変数を意図的に変異させ局所最適を回避。

使い方: python scripts/optimize-params.py [--log 別ログパス] [--dry-run]
"""
import argparse, json, os, random, statistics, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
TUNABLE = {"fontVw": (7.0, 12.0), "glow": (0.6, 1.8), "scaleFactor": (1.05, 1.3), "ttsSpeed": (0.9, 1.15)}
MIN_SAMPLES = 8  # これ未満のデータでは統計的に無意味なので変更しない


def score(row):
    s = row.get("stats", {})
    # 完了率を最重視(×2)、シェアは拡散トリガーとして加点
    return (s.get("views", 0) * (1 + s.get("avgWatchPct", 50) / 50)
            + s.get("shares", 0) * 500 + s.get("lineClicks", 0) * 300)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=os.path.join(DOCS, "tiktok-analytics-log.json"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    try:
        with open(args.log, encoding="utf-8") as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        sys.exit(f"❌ ログが読めません: {args.log}")

    rows = [r for r in log if r.get("params") and r.get("stats", {}).get("views") is not None]
    params_path = os.path.join(DOCS, "params-current.json")
    try:
        with open(params_path, encoding="utf-8") as f:
            current = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        current = {}

    if len(rows) < MIN_SAMPLES:
        print(f"ℹ️ 有効データ{len(rows)}件 < {MIN_SAMPLES}件 — 統計不足のためパラメータ据え置き。")
        return

    rows.sort(key=score, reverse=True)
    q = max(1, len(rows) // 4)
    top, bottom = rows[:q], rows[-q:]
    changes = {}
    for key, (lo, hi) in TUNABLE.items():
        tv = [r["params"][key] for r in top if key in r["params"]]
        bv = [r["params"][key] for r in bottom if key in r["params"]]
        if not tv or not bv:
            continue
        t_med, b_med = statistics.median(tv), statistics.median(bv)
        if abs(t_med - b_med) > (hi - lo) * 0.05:  # 明確な差がある時だけ動かす
            changes[key] = round(min(hi, max(lo, t_med)), 3)

    # 10%: 探索のため1変数をランダム変異（A/B実験枠）
    if random.random() < 0.10:
        key = random.choice(list(TUNABLE))
        lo, hi = TUNABLE[key]
        base = changes.get(key, current.get(key, (lo + hi) / 2))
        changes[key] = round(min(hi, max(lo, base * random.uniform(0.9, 1.1))), 3)
        print(f"🧪 実験変異: {key} → {changes[key]}")

    if not changes:
        print("ℹ️ 上位/下位に有意差なし — パラメータ据え置き。")
        return

    print(f"🏆 上位{q}本(中央スコア{score(top[q//2]):.0f}) vs 下位{q}本 の勝ちパラメータ:")
    for k, v in changes.items():
        print(f"   {k}: {current.get(k, '(未設定)')} → {v}")
    if args.dry_run:
        print("(dry-run: 書き込みスキップ)")
        return
    current.update(changes)
    os.makedirs(DOCS, exist_ok=True)
    with open(params_path, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    print(f"✅ {params_path} を更新しました。次回 generate-master.py 実行分から自動適用。")


if __name__ == "__main__":
    main()
