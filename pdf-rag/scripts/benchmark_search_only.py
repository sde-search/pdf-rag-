#!/usr/bin/env python3
"""Только поиск + реранкер (без LLM)."""
import sys, time, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.hybrid_search import build_query_engine

queries = [
    "какие видео форматы поддерживаются для layout в IconStation",
    "как добавить событие в Transmission List",
    "настройка Versio playout каналов",
    "поддерживаемые кодеки для clip в Creation Station",
]

results = []
search_fn = build_query_engine()

for q in queries:
    t0 = time.time()
    docs = search_fn(q, top_k=5)
    t = time.time() - t0
    scores = [d.get("rerank_score", 0) for d in docs]
    sources = list(set(d.get("source","") for d in docs))
    results.append({
        "query": q[:50],
        "search_time_s": round(t, 2),
        "n_docs_final": len(docs),
        "rerank_scores": [round(float(s), 4) for s in scores],
        "sources": sources,
    })
    print(f"[OK] {q[:40]}...  {t:.2f}s  docs={len(docs)}  scores={[round(s,3) for s in scores]}")

print("\n--- ИТОГО ---")
ts = [r["search_time_s"] for r in results]
avg_rr = sum(r["rerank_scores"][0] if r["rerank_scores"] else 0 for r in results) / len(results)
print(f"Поиск (среднее): {sum(ts)/len(ts):.2f}s  (макс: {max(ts):.2f}s)")
print(f"Средний score топ-документа: {avg_rr:.4f}")

with open("benchmark_after_search.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Сохранено в benchmark_after_search.json")