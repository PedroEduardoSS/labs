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
        read -p "Deseja compactar essa pasta: $item ? (y/n)" confirm
        case "$confirm" in
            [yY][eE][sS]|[yY]) 
                echo "Prosseguindo..."
                ;;
            [nN][oO]|[nN])
                echo "Abortando."
                continue
                ;;
            *)
                echo "Input inválido."
                ;;
        esac
        echo "Compactando a pasta: $item para ZIP..."
        zip -r "${item}.zip" "$item" > /dev/null
        echo "Concluído: ${item}.zip criado."
    fi
done

echo "Processo finalizado com sucesso."