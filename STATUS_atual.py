import datetime
import pandas as pd
from mysql.connector import Error
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
from Atualiza import consulta
from selenium.webdriver.chrome.service import Service


def hora():
    data = datetime.now()
    data = str(data)
    hora = data[11:13]
    minuto = data[14:16]
    segundo = data[17:19]
    return f"{data[:10]}_{hora}-{minuto}-{segundo}"


def job(status):
    try:
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

        excluir = open('Excluir.txt', 'r', encoding='utf-8')
        lista = excluir.read()

        dias = [
            'Segunda-feira',
            'Terça-feira',
            'Quarta-feira',
            'Quinta-Feira',
            'Sexta-feira',
            'Sábado',
            'Domingo'
        ]

        data = datetime.now()
        indice_da_semana = data.weekday()
        dia_da_semana = dias[indice_da_semana]

        data = str(data)
        print(f'*Bom dia a todos*\n\nPara hoje, {dia_da_semana}, {data[8:10]}-{data[5:7]}-{data[0:4]}, '
              f'as seguintes ERAs estão *fora do ar*\n')

        for e in element:
            cidade = pd.read_csv('ESTACAO_CIDADE_UF.txt', sep=';')
            if str(e.text) not in lista:
                teste1 = str(e.text)
                id_base = (teste1[:4])

                era = cidade.loc[(cidade['ESTACAO'] == id_base), ['CIDADE']]
                era = era["CIDADE"].values

                if status == 'OFFLINE' and e.text != e.get_attribute("title"):
                    print(f'{id_base}, {era[0]}')
                elif status == 'ONLINE':
                    print(f'Base {id_base} ONLINE')
            cidade = None
        driver.close()
        driver.quit()
        final = time.time()
        print(hora())
        print(f'Duração: {final - inicio}')
        print('\n')

    except Error:
        print('Não atualizado!')


while True:
    try:
        job('OFFLINE')
        time.sleep(600)
    except Error as erro:
        print(f'Erro ao executar: {erro}')
        time.sleep(60)
