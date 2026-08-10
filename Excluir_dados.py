import time
from Atualiza import deleta, deleta_todos_registros


def excluir():
    try:
        with open('Excluir.txt') as f:
            content = f. readlines()
            content = [x. rstrip('\n') for x in content]
            for i in content:
                i = i[:4]
                dados = '\'' + i + '\''
                deleta(dados)

        time.sleep(15)
    except:
        print('Arquivo não encontrado!')
        time.sleep(15)


excluir()
