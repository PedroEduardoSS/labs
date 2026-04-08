import socket

# --- Servidor UDP ---
def servidor_udp():
    host = '127.0.0.1'
    porta = 5005
    
    # 1. Cria o socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 2. Associa o socket ao endereço e porta
    sock.bind((host, porta))
    
    print(f"Servidor ouvindo em {host}:{porta}")
    
    while True:
        # 3. Recebe dados
        dados, endereco = sock.recvfrom(1024)
        print(f"Recebido de {endereco}: {dados.decode('utf-8')}")
        
        # 4. Responde (opcional)
        sock.sendto(b"Mensagem recebida", endereco)

# --- Cliente UDP ---
def cliente_udp():
    host = '127.0.0.1'
    porta = 5005
    mensagem = b"Ola, Servidor!"
    
    # 1. Cria o socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 2. Envia dados
    sock.sendto(mensagem, (host, porta))
    print(f"Enviado: {mensagem.decode('utf-8')}")
    
    # 3. Recebe resposta (opcional)
    dados, endereco = sock.recvfrom(1024)
    print(f"Resposta: {dados.decode('utf-8')}")
    sock.close()
