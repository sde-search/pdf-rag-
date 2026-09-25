# pdf-rag — Hybrid RAG search service

Готовый к развёртыванию пакет гибридного поиска:
векторный (ChromaDB + nomic-embed-text) + BM25 + FlashRank reranker + фильтр по продукту.
Все операции доступны через HTTP-эндпоинты — shell не требуется.

## Включает
- Индексы ChromaDB + BM25 (готовые, предварительно наполненные)
- Исходные документы (PDF, DOCX, PPTX)
- HTTP-сервер поиска (FastAPI, порт 11436)
- Скрипт индексации (полная и инкрементальная)
- Полную инструкцию (INSTRUCTIONS.md)

## Быстрый старт

```bash
chmod +x setup.sh
./setup.sh            # установка .venv + зависимостей + проверка Ollama
./setup.sh --systemd  # то же + установка systemd-сервиса
```

Сервер встанет на порту 11436.

## Поиск

```bash
# базовый
curl 'http://localhost:11436/search?query=ваш+запрос'

# с фильтром по продукту
curl 'http://localhost:11436/search?query=ваш+запрос&product=Название+продукта'

# больше результатов
curl 'http://localhost:11436/search?query=запрос&k=20'
```

## Добавление документов (через HTTP)

### Загрузка файла
```bash
curl -X POST http://localhost:11436/upload \
  -F "file=@/путь/к/файлу.pdf"
```
Проверка дубликата по SHA256 — если файл уже есть, вернёт 409.

### Инкрементальная индексация
```bash
curl -X POST http://localhost:11436/ingest \
  -H "Content-Type: application/json" \
  -d '{"product": "Название", "summary": "Описание"}'
```
Индекс перезагружается автоматически.

### Полная переиндексация (CLI)
```bash
cd pdf-rag && .venv/bin/python src/ingestion_hybrid.py \
    --product "Название продукта" \
    --summary "Краткое описание"
```

## Валидация ответа

```bash
curl -X POST http://localhost:11436/validate \
  -H "Content-Type: application/json" \
  -d '{"query": "вопрос", "response": "ответ агента"}'
```

## Список файлов и статус

```bash
curl http://localhost:11436/files      # проиндексированные файлы
curl http://localhost:11436/status     # статистика индекса
curl http://localhost:11436/info       # описание системы
```

## Требования
- Python 3.13+
- Ollama с моделью nomic-embed-text (ставится автоматически)
- ~500 MB свободного места + место под файлы

## Технические детали
- Коллекция ChromaDB: `docs`
- Чанкование: 768 слов, overlap 128, разделение по `[.!?]`
- Поиск: ChromaDB (n_results=30) + BM25 (n_results=30) → RRF fusion → FlashRank reranker
- Эмбеддинги: nomic-embed-text через Ollama, метрика cosine
- Дедупликация: SHA256+mtime (проверка при загрузке + при инкрементальной индексации)
- Метаданные чанка: source, product, summary
- Сервер: FastAPI + uvicorn, порт 11436, все операции через эндпоинты