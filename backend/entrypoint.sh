#!/bin/sh
mkdir -p /app/data

echo "🟡 [1/4] Aguardando banco de dados..."

python -m scripts.create_tables
echo "✅ Tabelas verificadas/criadas."

LOCK_FILE="/app/data/setup_v1.lock"

if [ -f "$LOCK_FILE" ]; then
    echo "🟢 [2/4] Setup inicial já realizado anteriormente. Pulando inserção de PDFs."
else
    echo "🟠 [2/4] Primeira execução detectada! Inserindo documentos no Qdrant/MinIO..."

    python -m app.modules.base_de_conhecimento.script_insercao_pdfs
    
    if [ $? -eq 0 ]; then
        touch "$LOCK_FILE"
        echo "✅ Inserção concluída com sucesso."
    else
        echo "🔴 Erro na inserção de documentos. O sistema tentará novamente no próximo reinício."
    fi
fi

echo "🚀 [3/4] Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000