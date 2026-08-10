import datetime

import mysql.connector
import pandas as pd
from Atualiza import deleta, deleta_todos_registros
from Atualiza_Local import ordena


mydb = mysql.connector.connect(
    host='179.188.16.100',
    user='atteras',
    password='GeoGuanda202',
    database='atteras'
)

mycursor = mydb.cursor()

mycursor.execute('SELECT * FROM status;')

result = mycursor.fetchall()


for row in result:
    print(row)

# mycursor.execute('CREATE TABLE status_novo SELECT * FROM status;')

mycursor = mydb.cursor()

mycursor.execute("Show tables;")

myresult = mycursor.fetchall()

for x in myresult:
    print(x)



i = 'Serv'
dados = '\'' + i + '\''
deleta(dados)

i = 'Rece'
dados = '\'' + i + '\''
deleta(dados)

i = 'SPSP'
dados = '\'' + i + '\''
deleta(dados)

cidade = pd.read_csv('ESTACAO_CIDADE_UF.txt', sep=';')
id_Base = 'SPSP'

#print(f'teste{era[0]}teste')
#deleta_todos_registros()
"""
print(f'🟢```ATENÇÃO```🟢\n\nA ERA de {era[0]} *({id_base})* está _on-line_ novamente!\n')

                    freq = 180
                    dur = 100

                    # loop iterates 5 times i.e, 5 beeps will be produced.
                    for i in range(0, 5):
                        winsound.Beep(freq, dur)
                        freq += 150
                        dur += 50
"""
DIAS = [
    'Segunda-feira',
    'Terça-feira',
    'Quarta-feira',
    'Quinta-Feira',
    'Sexta-feira',
    'Sábado',
    'Domingo'
]

data = datetime.date.today()
print(data)

indice_da_semana = data.weekday()
print(indice_da_semana)

dia_da_semana = DIAS[indice_da_semana]
print(dia_da_semana)

numero_do_dia_da_semana = data.isoweekday()
