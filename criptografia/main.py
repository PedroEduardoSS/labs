from modules.hash import hash_file, verify_integrity
from modules.encryption import aes_ed, rsa_ed
from modules.password import check_strength, hash_pw, verify_pw
from getpass import getpass
import argparse


def main():
    """
    Ponto de entrada principal para a ferramenta de criptografia. Analisa os argumentos da linha de comando para realizar várias operações criptográficas, como hash de arquivos, verificação de integridade, criptografia/descriptografia de arquivos com AES ou RSA, verificação de força de senha e hash/verificação de senhas.

    Argumentos de linha de comando:
        --hash-file FILE
            Gera o hash para o arquivo especificado.
        --verify-integrity FILE HASH
            Verifica a integridade de um arquivo comparando seu hash com o valor fornecido.
        --aes-encrypt INFILE OUTFILE
            Criptografa um arquivo usando AES e grava a saída em OUTFILE.
        --aes-decrypt INFILE OUTFILE
            Descriptografa um arquivo usando AES e grava a saída em OUTFILE.
        --rsa-encrypt INFILE OUTFILE
            Criptografa um arquivo usando RSA e grava a saída em OUTFILE.
        --rsa-decrypt INFILE OUTFILE
            Descriptografa um arquivo usando RSA e grava a saída em OUTFILE.
        --check-strength PASSWORD
            Verifica a força da senha fornecida.
        --hash-pw PASSWORD
            Gera o hash para a senha fornecida.
        --verify-pw PASSWORD HASH
            Verifica uma senha em relação ao hash fornecido.

    Nota:
        O parâmetro 'nargs' no argparse especifica o número de argumentos da linha de comando que devem ser consumidos. Por exemplo, 'nargs=2' significa que o argumento espera dois valores (por exemplo, nomes de arquivo de entrada e saída).
    """
    parser = argparse.ArgumentParser(
        description='Testes de criptografias',
    )
    parser.add_argument('--hash-file', metavar='FILE', help='Gera hash de um arquivo')
    parser.add_argument('--verify-integrity', nargs=2, metavar=('FILE_1', 'FILE_2'), help='Verifica integridade de um arquivo')
    parser.add_argument('--aes-encrypt', nargs=2, metavar=('INFILE', 'OUTFILE'), help='Criptografa arquivo com AES')
    parser.add_argument('--aes-decrypt', nargs=2, metavar=('INFILE', 'OUTFILE'), help='Descriptografa arquivo com AES')
    parser.add_argument('--rsa-encrypt', nargs=2, metavar=('INFILE', 'OUTFILE'), help='Criptografa arquivo com RSA')
    parser.add_argument('--rsa-decrypt', nargs=2, metavar=('INFILE', 'OUTFILE'), help='Descriptografa arquivo com RSA')
    parser.add_argument('--check-strength', metavar='PASSWORD', help='Verifica força da senha')
    parser.add_argument('--hash-pw', metavar='PASSWORD', help='Gera hash de uma senha')
    parser.add_argument('--verify-pw', nargs=2, metavar=('PASSWORD', 'HASH'), help='Verifica senha com hash')
    args = parser.parse_args()

    if args.hash_file:
        print(hash_file(args.hash_file))
    if args.verify_integrity:
        file_1, file_2 = args.verify_integrity
        print(verify_integrity(file_1, file_2))
    if args.aes_encrypt:
        infile, outfile = args.aes_encrypt
        aes_ed('encrypt', infile, outfile)
        print(f'Arquivo {infile} criptografado para {outfile} com AES.')
    if args.aes_decrypt:
        infile, outfile = args.aes_decrypt
        aes_ed('decrypt', infile, outfile)
        print(f'Arquivo {infile} descriptografado para {outfile} com AES.')
    if args.rsa_encrypt:
        infile, outfile = args.rsa_encrypt
        rsa_ed('encrypt', infile, outfile)
        print(f'Arquivo {infile} criptografado para {outfile} com RSA.')
    if args.rsa_decrypt:
        infile, outfile = args.rsa_decrypt
        rsa_ed('decrypt', infile, outfile)
        print(f'Arquivo {infile} descriptografado para {outfile} com RSA.')
    if args.check_strength:
        print(check_strength(args.check_strength))
    if args.hash_pw:
        print(hash_pw(args.hash_pw))
    if args.verify_pw:
        password, hash_value = args.verify_pw
        print(verify_pw(password, hash_value))

main()
