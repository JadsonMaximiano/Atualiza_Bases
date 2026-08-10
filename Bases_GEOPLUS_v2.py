import datetime
import os
import shutil
import time
from datetime import datetime

import pandas as pd
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector

from Atualiza import atualiza_bases, consulta

arquivo = r'Log\log.txt'

try:
    shutil.rmtree(rf'C:\Users\{os.getlogin()}\.wdm')
except Exception as erro:
    print(erro)


def hora():
    data = datetime.now()
    data = str(data)
    hora = data[11:13]
    minuto = data[14:16]
    segundo = data[17:19]
    return f"{data[8:10]}/{data[5:7]}/{data[0:4]} {hora}:{minuto}:{segundo}"


def job():
    global gpp
    try:
        verifica_arquivo(arquivo)
        with open(arquivo, 'a') as files:
            files.write('Iniciando analise')
        inicio = time.time()
        
        url = "https://acesso.geoplusbrasil.com:8181/gpprcvr_servlet/index.zul"

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=options)
        driver.set_window_size(1000, 10000)
        driver.get(url)
        time.sleep(2)
        driver.execute_script("document.body.style.zoom='5%';")
        element = driver.find_elements(By.XPATH, '//tr[@class="main z-treerow"]')

        delete = open('Excluir.txt', 'r', encoding='utf-8')
        lista = delete.read()

        with open(arquivo, 'a') as files:
            files.write('Lendo ERAs!\n')

        if gpp == 2:
            f = open("data/Relatorio_STATUS.csv", "a")
            f.write(f"\nGPP;{hora()};ONLINE")
            f.close()
            gpp = 1
        print('LENDO BASES\n')
        for e in element:

            cidade = pd.read_csv('ESTACAO_CIDADE_UF.txt', sep=';')
            if str(e.text) not in lista:
                teste1 = str(e.text)
                id_base = (teste1[:4])
                dados = '\'' + id_base + '\''
                try:
                    era = cidade.loc[(cidade['ESTACAO'] == id_base), ['CIDADE']]
                    era = era["CIDADE"].values
                    city = '\'' + era[0] + '\''



                    cons = consulta(dados, city)
                    if e.text == e.get_attribute("title") and cons == 1:
                        f = open("data/Relatorio_STATUS.csv", "a")
                        f.write(f"\n{id_base};{hora()};ONLINE")
                        f.close()

                    elif e.text != e.get_attribute("title") and cons == 0:
                        f = open("data/Relatorio_STATUS.csv", "a")
                        f.write(f"\n{id_base};{hora()};OFFLINE")
                        f.close()

                    if e.text == e.get_attribute("title"):
                        status_base = '\'' + '0' + '\''
                        atualiza_bases(dados, city, status_base)

                    else:
                        status_base = '\'' + '1' + '\''
                        atualiza_bases(dados, city, status_base)
                    #print(id_base, era[0], status_base)
                except Exception as erro:
                    with open(arquivo, 'a') as files:
                        files.write(f'\nEra {id_base} não cadastrada!')
                    print(f'Era {id_base} não cadastrada!')

        driver.close()
        driver.quit()
        with open(arquivo, 'a') as files:
            files.write(f'\nFinaliza a atualização!')

        print("Finaliza a atualização!")

        final = time.time()
        horario = hora()
        dados = '\'' + 'Hora' + '\''
        city = '\'' + horario[:16] + '\''
        atualiza_bases(dados, city, status=0)
        with open(arquivo, 'a') as files:
            files.write(f'\nAtualização: {horario[:16]}')
            files.write(f'Duração: {(final - inicio):,.2f} segundos\n')

    except Exception as erro:
        if gpp == 1:
            f = open("data/Relatorio_STATUS.csv", "a")
            f.write(f"\nGPP;{hora()};OFFLINE")
            f.close()
            gpp = 2
        with open(arquivo, 'a') as files:
            files.write(f'\nNão atualizado! Erro Geral {erro}')


def verifica_arquivo(file):
    if os.path.isfile(file):
        with open(file, 'a') as files:
            files.write(f'{hora()}\n')
    else:
        with open(file, 'w') as files:
            files.write(f'{hora()}\n')


verifica_arquivo(arquivo)
gpp = 2
cont = 1
if cont == 1:
    job()
while True:
    schedule.run_pending()
    schedule.every(120).seconds.do(job)
    cont = 2


