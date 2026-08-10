import mysql.connector
from mysql.connector import Error



try:
    con = mysql.connector.connect(
    host='179.188.16.100',
    user='atteras',
    password='GeoGuanda202',
    database='atteras')

    consulta_sql = "select * from status"
    cursor = con.cursor()
    cursor.execute(consulta_sql)
    linhas = cursor.fetchall()
    print("Número total de registros retornados: ", cursor.rowcount)

    print("\nMostrando os autores cadastrados")
    for linha in linhas:
        print("Id:", linha[0])
        print("Nome:", linha[1])
        print("Sobrenome:", linha[2], "\n")

except Error as e:
    print("Erro ao acessar tabela MySQL", e)

finally:
    if con.is_connected():
        cursor.close()
        con.close()
        print("Conexão ao MySQL encerrada")
