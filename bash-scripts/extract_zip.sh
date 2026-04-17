#!/bin/bash
DIRETORIO="$HOME/Documentos"
cd "$DIRETORIO" || exit

for arquivo in *.zip; do
    [ -e "$arquivo" ] || continue # Se não houver .zip, pula
    NOME_PASTA="${arquivo%.zip}"
    
    if [ -d "$NOME_PASTA" ]; then
        echo "Aviso: A pasta '$NOME_PASTA' já existe. Pulando..."
    else
        echo "Extraindo: $arquivo..."
        unzip -q "$arquivo"
    fi
done