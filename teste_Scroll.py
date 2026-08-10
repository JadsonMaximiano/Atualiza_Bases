import datetime
import os
import shutil
import time
from datetime import datetime
import numpy

import pandas as pd
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector
from selenium.webdriver.common.action_chains import ActionChains

url = "https://acesso.geoplusbrasil.com:8181/gpprcvr_servlet/index.zul"

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=options)
driver.set_window_size(1000, 10000)
driver.get(url)
time.sleep(2)

element = driver.find_elements(By.XPATH, '//tr[@class="main z-treerow"]')

for e in element:
    print(e.text)