#!/usr/bin/env python3
"""Замер производительности hybrid_search: время поиска + LLM."""
import sys, time, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.hybrid_search import build_query_engine, ask

queries = [
    "какие видео форматы поддерживаются для layout в IconStation",
    "как добавить событие в Transmission List",
    "настройка Versio playout каналов",
    "поддерживаемые кодеки для clip в Creation Station",
]

results = []
for q in queries:
    # только поиск (без LLM)
    t0 = time.time()
    search_fn = build_query_engine()
    docs = search_fn(q, top_k=5)
    t_search = time.time() - t0

    # полный цикл с LLM
    t0 = time.time()
    answer = ask(q, top_k=5)
    t_full = time.time() - t0

    results.append({
        "query": q,
        "search_time_s": round(t_search, 2),
        "full_time_s": round(t_full, 2),
        "n_docs": len(docs),
        "sources": list(set(d.get("source","") for d in docs)),
        "answer_preview": answer[:200],
    })
    print(f"[OK] \"{q[:40]}...\"  search={t_search:.2f}s  full={t_full:.2f}s  docs={len(docs)}")

print("\n--- ИТОГО ---")
times_search = [r["search_time_s"] for r in results]
times_full = [r["full_time_s"] for r in results]
print(f"Поиск (среднее): {sum(times_search)/len(times_search):.2f}s")
print(f"Поиск (макс):    {max(times_search):.2f}s")
print(f"Полный (среднее): {sum(times_full)/len(times_full):.2f}s")
print(f"Полный (макс):   {max(times_full):.2f}s")

with open("benchmark_before.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Результаты сохранены в benchmark_before.json")