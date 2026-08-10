import mysql.connector
from mysql.connector import Error


# Atualizar registros em um banco de dados MySQL
def conectar():
    try:
        global con
        con = mysql.connector.connect(
            host='atteras.mysql.dbaas.com.br',
            user='atteras',
            password='GeoGuanda202!',
            database='atteras',
            use_pure=True
        )
    except Error as erro:
        print(f'Erro de conexão: {erro}')


def consulta(id1, cidade):
    try:
        conectar()
        consulta_slq = f'select * from status WHERE base = {id1}'
        cursor = con.cursor()
        cursor.execute(consulta_slq)
        linhas = cursor.fetchall()

        if not linhas:
            insere(id1, cidade)
            return '0'
        else:
            for linha in linhas:
                linha
            return linha[1]

    except Error as erro:

        print(f'Falha ao consultar a tabela: {erro}')
    finally:
        if con.is_connected():
            cursor.close()
            con.close()


def insere(nome, cidade):
    try:
        conectar()
        inserir_base = f"""INSERT INTO status (base, cidade) VALUES ({nome}, {cidade})"""
        cursor = con.cursor()
        cursor.execute(inserir_base)
        con.commit()
        print(f'ERA ({nome}) adicionada na tabela!')
    except Error as erro:
        print(f'Falha ao inserir dados no MySQL: {erro}')
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
            print('Conexão MySQL finalizada')


def atualiza(base, status):
    try:
        conectar()
        altera_status = f"""UPDATE status SET status = {status} WHERE base = {base}"""
        cursor = con.cursor()
        cursor.execute(altera_status)
        con.commit()
    except Error as erro:
        print(f'Falha ao atualizar dados na tabela: {erro}')
    finally:
        if con.is_connected():
            cursor.close()
            con.close()


def deleta(id):
    try:
        conectar()
        cursor = con.cursor()
        sql = f"DELETE FROM status WHERE base = {id}"
        cursor.execute(sql)
        con.commit()
        print(cursor.rowcount, f"registro excluído: {id}")  # 1 registro excluído
    except Error as erro:
        print(f'Erro ao deletar: {erro}')
    finally:
        if con.is_connected():
            cursor.close()
            con.close()


def atualiza_bases(base, cidade, status):
    consulta(base, cidade)
    dados = '\'' + 'Hora' + '\''
    if base == dados:
        atualiza_hora(base, cidade)
    else:
        atualiza(base, status)


def atualiza_hora(base, cidade):
    try:
        conectar()
        altera_status = f"""UPDATE status SET cidade = {cidade} WHERE base = {base}"""
        cursor = con.cursor()
        cursor.execute(altera_status)
        con.commit()
    except Error as erro:
        print(f'Falha ao atualizar dados na tabela: {erro}')
    finally:
        if con.is_connected():
            cursor.close()
            con.close()


def deleta_todos_registros():
    print('Deletando todos os registros...')
    try:
        conectar()
        sql = 'DELETE FROM status;'
        cursor = con.cursor()
        cursor.execute(sql)
        con.commit()
    except Error as erro:
        print(f'Falha em Deletar todos os registros! {erro}')

