import datetime
import os
import time
from datetime import datetime
import fiona
import geopandas as gpd
import simplekml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

fiona.drvsupport.supported_drivers['KML'] = 'rw'


def hora():
    data = datetime.now()
    data = str(data)
    hora = data[11:13]
    minuto = data[14:16]
    segundo = data[17:19]
    return f"{data[8:10]}-{data[5:7]}-{data[0:4]} {hora}:{minuto}:{segundo}"


def job(save):
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

    kml = simplekml.Kml()
    fol = kml.newfolder()

    fol.altitudemode = simplekml.AltitudeMode.relativetoground
    fol.lookat.gxaltitudemode = simplekml.GxAltitudeMode.relativetoseafloor
    fol.lookat.latitude = -22.469418
    fol.lookat.longitude = -46.664066
    fol.lookat.range = 1097494
    fol.lookat.heading = 0
    fol.lookat.tilt = 0

    ok = simplekml.Style()
    ok.iconstyle.color = simplekml.Color.green  # Green
    ok.iconstyle.icon.href = 'https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png'
    ok.iconstyle.scale = 0.5
    ok.labelstyle.scale = 0.5

    rc = simplekml.Style()
    rc.iconstyle.color = simplekml.Color.blue  # Yellow
    rc.iconstyle.icon.href = 'https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png'
    rc.iconstyle.scale = 0.5
    rc.labelstyle.scale = 0.5

    seco = simplekml.Style()
    seco.iconstyle.color = simplekml.Color.red  # Red
    seco.iconstyle.icon.href = 'https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png'
    seco.iconstyle.scale = 0.5
    seco.labelstyle.scale = 0.5

    for e in element:
        teste1 = str(e.text)
        id_base = (teste1[:4])
        mapa = meu_mapa.loc[meu_mapa['Name'] == id_base]

        if not mapa.empty:
            name = mapa['Name'].values
            long = mapa["long"].values
            lat = mapa["lat"].values
            desc = mapa["Description"].values
            ls = fol.newpoint()
            ls.name = str(name[0])
            ls.style.iconstyle.scale = 3
            ls.description = desc[0].upper()
            ls.coords = [(long[0], lat[0])]


            if e.text == e.get_attribute("title"):
                if save == 'ERAs_NTRIP_atualizado.kml':
                    ls.style = ok
                else:
                    ls.style = rc

            else:
                ls.style = seco

    driver.close()
    driver.quit()
    final = time.time()
    horario = hora()

    kml.save(save)
    os.startfile(save)

    print('\nAtualização: ', horario)
    print(f'Duração: {final - inicio}')


while True:
    meu_mapa = gpd.read_file('ERAs_REDE.kml', driver='KML')
    meu_mapa["long"] = meu_mapa.geometry.map(lambda p: p.x)
    meu_mapa["lat"] = meu_mapa.geometry.map(lambda p: p.y)
    save = 'ERAs_REDE_atualizado.kml'
    try:
        job(save)
    except Exception as erro:
        print(erro)

    meu_mapa = gpd.read_file('ERAs_NTRIP.kml', driver='KML')
    meu_mapa["long"] = meu_mapa.geometry.map(lambda p: p.x)
    meu_mapa["lat"] = meu_mapa.geometry.map(lambda p: p.y)
    save = 'ERAs_NTRIP_atualizado.kml'
    try:
        job(save)
    except Exception as erro:
        print(erro)
    time.sleep(20)

