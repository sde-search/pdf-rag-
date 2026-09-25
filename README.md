# pdf-rag — Гибридный RAG-поиск по документам

Векторный поиск (ChromaDB + Ollama) + BM25 + FlashRank reranker + фильтр по продукту.  
Всё локально, без облаков. Все операции через HTTP-эндпоинты.

## Быстрый старт

```bash
chmod +x setup.sh
./setup.sh            # установка .venv + зависимостей + проверка Ollama
./setup.sh --systemd  # то же + установка systemd-сервиса
```

Перед запуском положи свои PDF, DOCX, PPTX в `pdf-rag/data/pdfs/`.

Сервер встанет на порту 11436. После первого запуска проиндексируй документы:

```bash
cd pdf-rag && .venv/bin/python src/ingestion_hybrid.py \
    --product "Название продукта" \
    --summary "Краткое описание"
```

## Поиск

```bash
curl 'http://localhost:11436/search?query=ваш+запрос'
curl 'http://localhost:11436/search?query=запрос&product=Название+продукта'
curl 'http://localhost:11436/search?query=запрос&k=20'
```

## Добавление документов

Через HTTP:
```bash
curl -X POST http://localhost:11436/upload -F "file=@/путь/к/файлу.pdf"
curl -X POST http://localhost:11436/ingest \
  -H "Content-Type: application/json" \
  -d '{"product": "Название", "summary": "Описание"}'
```

## Структура репозитория

```
pdf-rag/
├── src/
│   ├── search_server.py      # HTTP-сервер (FastAPI, порт 11436)
│   ├── hybrid_search.py      # библиотека поиска (ChromaDB + BM25 + FlashRank)
│   └── ingestion_hybrid.py   # скрипт индексации
├── scripts/                  # вспомогательные скрипты
├── data/                     # создаётся при установке — сюда класть документы
├── setup.sh                  # установка зависимостей
├── INSTRUCTIONS.md           # полная документация
├── REQUIREMENTS.txt          # зависимости Python
└── pdf-rag-search.service.template  # шаблон systemd-сервиса
```

## Требования

- Python 3.13+
- Ollama с моделью `nomic-embed-text` (скачивается автоматически при установке)
- ~500 MB + место под твои документы и индексы

## Технические детали

- Поиск: ChromaDB (n_results=30) + BM25 (n_results=30) → RRF fusion → FlashRank reranker
- Эмбеддинги: nomic-embed-text через Ollama, метрика cosine
- Чанкование: 768 слов, overlap 128
- Дедупликация по SHA256 при загрузке
- Все операции доступны через HTTP — shell не требуется