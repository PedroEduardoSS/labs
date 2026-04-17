#!/bin/bash
DIRETORIO="$HOME/Documentos"
cd "$DIRETORIO" || exit

for arquivo in *.tar.gz; do
    [ -e "$arquivo" ] || continue
    # Remove a extensão .tar.gz para checar o nome da pasta
    NOME_PASTA="${arquivo%.tar.gz}"
    
    if [ -d "$NOME_PASTA" ]; then
        echo "Aviso: A pasta '$NOME_PASTA' já existe. Pulando..."
    else
        echo "Extraindo: $arquivo..."
        tar -xzf "$arquivo"
    fi
done