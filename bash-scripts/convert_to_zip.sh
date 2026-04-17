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
        echo "Compactando a pasta: $item para ZIP..."
        zip -r "${item}.zip" "$item" > /dev/null
        echo "Concluído: ${item}.zip criado."
    fi
done

echo "Processo finalizado com sucesso."