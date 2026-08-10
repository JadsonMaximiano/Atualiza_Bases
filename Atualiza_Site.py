import datetime
import os
import shutil
import time
from datetime import datetime

import geopandas as gpd
import fiona
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from Atualiza import atualiza_bases, consulta, deleta_todos_registros

try:
    shutil.rmtree(rf'C:\Users\{os.getlogin()}\.wdm')
except Exception as erro:
    print(erro)

arquivo = r'Log\log.txt'


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
        print('Iniciando Analise')
        verifica_arquivo(arquivo)

        try:
            file = r"M:\TECNICO\GEOPLUS\Equipamentos Instalados\Bases_atualizadas_2024\ERAs_NTRIP_REDE\ERAs_NTRIP_REDE.dbf"

            Table = gpd.read_file(file)

        except Exception as erro:
            print(erro)
        with open(arquivo, 'a') as files:
            files.write('Iniciando analise')
        inicio = time.time()

        url = "http://acesso.geoplusbrasil.com:8181/gpprcvr_servlet/index.zul"

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        #options.add_argument("--ignore-certificate-errors")  # Ignorar erros de certificado
        #options.add_argument("--disable-web-security")  # Desativar a verificação de segurança web
        #options.add_argument("--allow-insecure-localhost")  # Permitir conexões inseguras no localhost (se aplicável)

        driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=options)
        driver.set_window_size(1000, 10000)

        driver.get(url)
        driver.execute_script("document.body.style.zoom='5%';")
        time.sleep(2)

        element = driver.find_elements(By.XPATH, '//tr[@class="main z-treerow"]')

        delete = open('Excluir.txt', 'r', encoding='utf-8')
        lista = delete.read()

        manutencao = open('Manutenção.txt', 'r', encoding='utf-8').read()

        with open(arquivo, 'a') as files:
            files.write('Lendo ERAs!\n')

        if gpp == 2:
            f = open("data/Relatorio_STATUS.csv", "a")
            f.write(f"\nGPP;{hora()};ONLINE")
            f.close()
            gpp = 1
        # cidade = pd.read_csv('ESTACAO_CIDADE_UF.txt', sep=';')

        print('LENDO BASES\n')
        for e in element:
            if str(e.text) in manutencao:
                teste1 = str(e.text)
                id_base = (teste1[:4])
                dados = '\'' + id_base + '\''
                try:
                    era = Table.loc[Table['NOME'] == id_base]
                    era = era["CIDADE"].values
                    city = '\'' + era[0] + '\''

                    status_base = '\'' + '2' + '\''
                    atualiza_bases(dados, city, status_base)
                    print(f'Era {id_base} em Manutenção!')
                except Exception as erro:
                    with open(arquivo, 'a') as files:
                        files.write(f'\nEra {id_base} não cadastrada!')
                    print(f'Era {id_base} não cadastrada!')
                    print(erro)

            elif str(e.text) not in lista:
                teste1 = str(e.text)
                print(teste1)
                id_base = (teste1[:4])
                dados = '\'' + id_base + '\''
                try:
                    era = Table.loc[Table['NOME'] == id_base]
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
                    # print(id_base, era[0], status_base)
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

schedule.every().day.at("01:05:30").do(deleta_todos_registros)
schedule.every(120).seconds.do(job)

if cont == 1:
    job()

while True:
    schedule.run_pending()
    cont = 2
