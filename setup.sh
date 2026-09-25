#!/usr/bin/env bash
set -e

echo "=== Установка pdf-rag (Hybrid RAG search) ==="

# Определяем папку установки (текущая директория скрипта)
INSTALL_DIR="$(cd "$(dirname "$0")/pdf-rag" && pwd)"
cd "$INSTALL_DIR"

echo "Установка в: $INSTALL_DIR"

# Проверка Python 3.13+
PY_VER=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
echo "Python: $(python3 --version)"

# 1. Виртуальное окружение
if [ ! -d .venv ]; then
    echo ">>> Создание виртуального окружения..."
    python3 -m venv .venv
fi

# 2. Зависимости
echo ">>> Установка зависимостей..."
.venv/bin/pip install -r REQUIREMENTS.txt -q

# 3. Ollama и модель
if ! command -v ollama &>/dev/null; then
    echo ">>> Ollama не найден. Установите: https://ollama.com"
    echo "    После установки выполните: ollama pull nomic-embed-text"
else
    echo ">>> Проверка модели nomic-embed-text..."
    if ! ollama list 2>/dev/null | grep -q nomic-embed-text; then
        echo "    Модель не найдена. Скачивание..."
        ollama pull nomic-embed-text
    else
        echo "    Модель уже установлена"
    fi
fi

# 4. Установка systemd-сервиса (опционально)
if [ "$1" == "--systemd" ]; then
    echo ">>> Установка systemd-сервиса..."
    sed "s|/home/hermes/projects/pdf-rag|$INSTALL_DIR|g" ../pdf-rag-search.service.template > /tmp/pdf-rag-search.service
    mkdir -p ~/.config/systemd/user/
    cp /tmp/pdf-rag-search.service ~/.config/systemd/user/pdf-rag-search.service
    systemctl --user daemon-reload
    systemctl --user enable pdf-rag-search.service
    systemctl --user start pdf-rag-search.service
    sleep 3
    if systemctl --user is-active pdf-rag-search.service &>/dev/null; then
        echo "    Сервер запущен на порту 11436"
    else
        echo "    [ОШИБКА] Сервер не запустился. Проверьте: systemctl --user status pdf-rag-search.service"
    fi
fi

# 5. Проверка
echo ">>> Проверка индекса..."
.venv/bin/python -c "
import chromadb, pickle
c = chromadb.PersistentClient('data/chroma')
try:
    cnt = c.get_collection('documents').count()
    print(f'    ChromaDB: {cnt} чанков')
except: print('    ChromaDB: нет коллекции (нужно проиндексировать)')
try:
    d = pickle.load(open('data/chroma/bm25_data.pkl','rb'))
    print(f'    BM25: {d.shape[0] if hasattr(d,\"shape\") else len(d)} чанков')
except: print('    BM25: нет индекса')
"

echo ""
echo "=== Готово! ==="
echo ""
echo "Запуск сервера вручную:"
echo "  cd $INSTALL_DIR && .venv/bin/python src/search_server.py"
echo ""
echo "Поиск:"
echo "  curl 'http://localhost:11436/search?q=ваш+запрос'"
echo ""
echo "Добавление файлов:"
echo "  1. Положить .pdf/.docx/.pptx в data/pdfs/"
echo "  2. .venv/bin/python src/ingestion_hybrid.py"
echo "  3. systemctl --user restart pdf-rag-search.service  (если установлен сервис)"
echo ""
echo "Более подробно: см. INSTRUCTIONS.md"