import os
import shutil
import subprocess
import threading
import time
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector  # noqa: F401  (necessário para o PyInstaller incluir o conector)

from Atualiza import atualiza_bases, consulta

arquivo = r'Log\log.txt'
URL_GEOPLUS = "https://acesso.geoplusbrasil.com:8181/gpprcvr_servlet/index.zul"
ENDERECO_CONTINGENCIA = "localhost:8080"

INTERVALO_SEGUNDOS = 120        # intervalo entre o fim de uma execução e o início da próxima
TIMEOUT_PAGINA = 60             # tempo máximo para carregar a página do GeoPlus
TIMEOUT_JOB = 10 * 60           # tempo máximo de uma execução completa antes de matar o Chrome
TAMANHO_MAX_LOG = 5 * 1024 * 1024  # rotaciona o log ao passar de 5 MB

os.makedirs('Log', exist_ok=True)

try:
    shutil.rmtree(rf'C:\Users\{os.getlogin()}\.wdm')
except Exception as erro:
    print(erro)


def hora():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def escreve_log(texto):
    try:
        with open(arquivo, 'a') as files:
            files.write(texto)
    except Exception as erro:
        print(f'Falha ao escrever no log: {erro}')


def escreve_relatorio(texto):
    try:
        with open("data/Relatorio_STATUS.csv", "a") as f:
            f.write(texto)
    except Exception as erro:
        print(f'Falha ao escrever no relatório: {erro}')


def verifica_arquivo(file):
    """Cria o log se não existir e rotaciona quando fica grande demais."""
    try:
        if os.path.isfile(file) and os.path.getsize(file) > TAMANHO_MAX_LOG:
            antigo = file + '.old'
            if os.path.isfile(antigo):
                os.remove(antigo)
            os.rename(file, antigo)
    except Exception as erro:
        print(f'Falha ao rotacionar o log: {erro}')
    escreve_log(f'{hora()}\n')


# ---------------------------------------------------------------- ChromeDriver
_caminho_driver = None


def obter_chromedriver():
    """Baixa o ChromeDriver uma única vez e reutiliza nas próximas execuções."""
    global _caminho_driver
    if _caminho_driver and os.path.isfile(_caminho_driver):
        return _caminho_driver
    try:
        _caminho_driver = ChromeDriverManager().install()
    except Exception as erro:
        print(f'Falha no ChromeDriverManager: {erro}')
        if os.path.isfile('chromedriver.exe'):
            _caminho_driver = os.path.abspath('chromedriver.exe')
        else:
            _caminho_driver = None  # deixa o Selenium Manager localizar o driver
    return _caminho_driver


def criar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1000,10000")

    caminho = obter_chromedriver()
    service = Service(executable_path=caminho) if caminho else Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(TIMEOUT_PAGINA)
    driver.set_script_timeout(TIMEOUT_PAGINA)
    return driver


def matar_driver(driver):
    """Encerra o chromedriver e todos os processos do Chrome abertos por ele."""
    if driver is None:
        return
    try:
        pid = driver.service.process.pid
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    except Exception as erro:
        print(f'Falha ao matar o chromedriver: {erro}')


def fechar_driver(driver):
    if driver is None:
        return
    try:
        driver.quit()
    except Exception as erro:
        print(f'Falha ao fechar o navegador: {erro}')
    # garante que não sobrem processos do Chrome mesmo se o quit falhar
    matar_driver(driver)


# ---------------------------------------------------------------- GeoPlus
def gerar_url_contingencia(url):
    """Mantém o caminho da URL original e direciona a requisição ao servidor local."""
    url_separada = urlsplit(url)
    return urlunsplit(("http", ENDERECO_CONTINGENCIA, url_separada.path,
                       url_separada.query, url_separada.fragment))


def acessar_geoplus(driver, url=URL_GEOPLUS):
    """Acessa o servidor principal e usa o servidor local somente se ele falhar."""
    url_contingencia = gerar_url_contingencia(url)

    try:
        driver.get(url)
        if str(driver.current_url).startswith("chrome-error://"):
            raise WebDriverException("O servidor principal retornou uma página de erro")
        return url
    except WebDriverException as erro_principal:
        print(f"Falha ao acessar {url}: {erro_principal}. Tentando {url_contingencia}.")
        driver.get(url_contingencia)
        if str(driver.current_url).startswith("chrome-error://"):
            raise WebDriverException("O servidor de contingência retornou uma página de erro")
        return url_contingencia


_driver_atual = None


def job():
    global gpp, _driver_atual
    driver = None
    try:
        verifica_arquivo(arquivo)
        escreve_log('Iniciando analise')
        inicio = time.time()

        driver = criar_driver()
        _driver_atual = driver
        acessar_geoplus(driver)
        time.sleep(2)
        driver.execute_script("document.body.style.zoom='5%';")
        elementos = driver.find_elements(By.XPATH, '//tr[@class="main z-treerow"]')

        # lê texto e título de uma vez só e libera o navegador antes de falar com o MySQL
        linhas = []
        for e in elementos:
            try:
                linhas.append((str(e.text), e.get_attribute("title")))
            except WebDriverException as erro:
                print(f'Falha ao ler linha da tabela: {erro}')
        fechar_driver(driver)
        driver = None
        _driver_atual = None

        with open('Excluir.txt', 'r', encoding='utf-8') as delete:
            lista = delete.read()
        cidade = pd.read_csv('ESTACAO_CIDADE_UF.txt', sep=';')

        escreve_log('Lendo ERAs!\n')

        if gpp == 2:
            escreve_relatorio(f"\nGPP;{hora()};ONLINE")
            gpp = 1
        print('LENDO BASES\n')
        for texto, titulo in linhas:
            if texto in lista:
                continue
            id_base = texto[:4]
            dados = '\'' + id_base + '\''
            try:
                era = cidade.loc[(cidade['ESTACAO'] == id_base), ['CIDADE']]
                era = era["CIDADE"].values
                city = '\'' + era[0] + '\''

                cons = consulta(dados, city)
                online = texto == titulo
                if online and cons == 1:
                    escreve_relatorio(f"\n{id_base};{hora()};ONLINE")
                elif not online and cons == 0:
                    escreve_relatorio(f"\n{id_base};{hora()};OFFLINE")

                status_base = '\'' + ('0' if online else '1') + '\''
                atualiza_bases(dados, city, status_base)
            except Exception:
                escreve_log(f'\nEra {id_base} não cadastrada!')
                print(f'Era {id_base} não cadastrada!')

        escreve_log('\nFinaliza a atualização!')
        print("Finaliza a atualização!")

        final = time.time()
        horario = hora()
        dados = '\'' + 'Hora' + '\''
        city = '\'' + horario[:16] + '\''
        atualiza_bases(dados, city, status=0)
        escreve_log(f'\nAtualização: {horario[:16]}Duração: {(final - inicio):,.2f} segundos\n')

    except Exception as erro:
        if gpp == 1:
            escreve_relatorio(f"\nGPP;{hora()};OFFLINE")
            gpp = 2
        escreve_log(f'\nNão atualizado! Erro Geral {erro}\n')
        print(f'Não atualizado! Erro Geral {erro}')
    finally:
        fechar_driver(driver)
        _driver_atual = None


def executa_com_timeout():
    """Roda o job numa thread; se travar além do limite, mata o Chrome para destravar."""
    global _driver_atual
    t = threading.Thread(target=job, daemon=True)
    t.start()
    t.join(TIMEOUT_JOB)
    if t.is_alive():
        escreve_log(f'\n{hora()} Execução travada há mais de {TIMEOUT_JOB}s, encerrando o Chrome\n')
        print('Execução travada, encerrando o Chrome...')
        matar_driver(_driver_atual)
        t.join(60)
        if t.is_alive():
            # a thread ficou presa (ex.: MySQL); segue em frente para não parar o monitoramento
            escreve_log(f'\n{hora()} Thread anterior ainda presa, iniciando nova execução\n')
            _driver_atual = None


gpp = 2
if __name__ == '__main__':
    verifica_arquivo(arquivo)
    while True:
        executa_com_timeout()
        time.sleep(INTERVALO_SEGUNDOS)
