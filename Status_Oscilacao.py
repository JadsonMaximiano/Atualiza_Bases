import datetime
import time
import pandas as pd
import schedule
import winsound
from datetime import datetime
from mysql.connector import Error
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from Atualiza_Local import consulta, atualiza_bases


def hora():
    data = datetime.now()
    data = str(data)
    hora = data[11:13]
    minuto = data[14:16]
    segundo = data[17:19]
    return f"{data[8:10]}-{data[5:7]}-{data[0:4]} {hora}:{minuto}:{segundo}"


def job():
    try:
        print('\nIniciando Analise!')
        inicio = time.time()
        url = "http://acesso.cegat.com.br:8181/gpprcvr_servlet/index.zul"

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=options)
        driver.set_window_size(1000, 1000)
        driver.get(url)
        time.sleep(2)
        driver.execute_script("document.body.style.zoom='25%';")
        element = driver.find_elements(By.XPATH, '//tr[@class="main z-treerow"]')

        delete = open('Excluir.txt', 'r', encoding='utf-8')
        lista = delete.read()

        for e in element:
            cidade = pd.read_csv('ESTACAO_CIDADE_UF.txt', sep=';')
            if str(e.text) not in lista:
                teste1 = str(e.text)
                id_base = (teste1[:4])
                dados = '\'' + id_base + '\''

                era = cidade.loc[(cidade['ESTACAO'] == id_base), ['CIDADE']]
                era = era["CIDADE"].values
                city = '\'' + era[0] + '\''

                cons = consulta(dados, city)
                if e.text == e.get_attribute("title") and cons == 1:
                    print(f'🟢```ATENÇÃO```🟢\n\nA ERA de {era[0]} *({id_base})* está _on-line_ novamente!\n')

                    freq = 180
                    dur = 100

                    # loop iterates 5 times i.e, 5 beeps will be produced.
                    for i in range(0, 5):
                        winsound.Beep(freq, dur)
                        freq += 150
                        dur += 50

                elif e.text != e.get_attribute("title") and cons == 0:
                    print(f'🛑```ATENÇÃO```🛑\n\nA ERA de {era[0]} *({id_base})* está _off-line_!\n')

                    freq = 1050
                    dur = 100

                    # loop iterates 5 times i.e, 5 beeps will be produced.
                    for i in range(0, 5):
                        winsound.Beep(freq, dur)
                        freq -= 150
                        dur += 50

                if e.text == e.get_attribute("title"):
                    status_base = '\'' + '0' + '\''
                    atualiza_bases(dados, city, status_base)

                else:
                    status_base = '\'' + '1' + '\''
                    atualiza_bases(dados, city, status_base)

        driver.close()
        driver.quit()
        final = time.time()
        horario = hora()

        print('\nAtualização: ', horario)
        print(f'Duração: {final - inicio}')

    except:
        print(f'Não atualizado!')


while True:
    try:
        schedule.every(25).seconds.do(job)
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Error as erro:
        print(f'Erro ao executar: {erro}')
        time.sleep(30)


