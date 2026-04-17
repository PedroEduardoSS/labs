#!/bin/bash

DIRETORIO="$HOME/Documentos"

# Verifica se o diretório existe
if [ ! -d "$DIRETORIO" ]; then
    echo "Erro: O diretório $DIRETORIO não existe."
    exit 1
fi

cd "$DIRETORIO" || exit

for item in *; do
    if [ -d "$item" ]; then
        echo "Compactando a pasta: $item..."
        tar -czf "${item}.tar.gz" "$item"
        echo "Concluído: ${item}.tar.gz criado."
    fi
done

echo "Processo finalizado com sucesso."