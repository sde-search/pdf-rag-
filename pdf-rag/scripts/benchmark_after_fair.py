#!/usr/bin/env python3
"""Честный замер: один build_query_engine(), 4 запроса."""
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

t0 = time.time()
search_fn = build_query_engine()
t_init = time.time() - t0
print(f"Init (BM25+Chroma+reranker): {t_init:.2f}s")

results = []
for q in queries:
    t0 = time.time()
    docs = search_fn(q, top_k=5)
    t = time.time() - t0
    scores = [float(d.get("rerank_score", 0)) for d in docs]
    sources = list(set(d.get("source","") for d in docs))
    results.append({
        "query": q[:50],
        "search_time_s": round(t, 2),
        "n_docs_final": len(docs),
        "rerank_scores": [round(s, 4) for s in scores],
        "rerank_active": any(s > 0 for s in scores),
        "sources": sources,
    })
    print(f"[{q[:35]}]  {t:.2f}s  scores={[round(s,3) for s in scores]}")

print("\n-- ИТОГО — после Reranker --")
ts = [r["search_time_s"] for r in results]
avg_rr = sum(r["rerank_scores"][0] if r["rerank_scores"] else 0 for r in results) / len(results)
rr_active = sum(1 for r in results if r["rerank_active"])
print(f"Init:           {t_init:.2f}s")
print(f"Поиск (среднее): {sum(ts)/len(ts):.2f}s  (макс: {max(ts):.2f}s)")
print(f"Reranker активен: {rr_active}/4 запросов")
print(f"Средний score топа: {avg_rr:.4f}")

with open("benchmark_after_fair.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Сохранено в benchmark_after_fair.json")