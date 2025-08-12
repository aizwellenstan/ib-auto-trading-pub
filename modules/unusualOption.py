import csv
import requests

CSV_URL = 'https://www.barchart.com/options/unusual-activity/etfs?orderBy=expirationDate&orderDir=asc#:~:text=flipcharts-,download,-Symbol'


with requests.Session() as s:
    download = s.get(CSV_URL)

    decoded_content = download.content.decode('utf-8')

    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)
    for row in my_list:
        print(row)


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
import os
import time

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

DRIVER_PATH = "C://temp/webscraping/chromedriver.exe"
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
#set download path (set to current working directory in this example)
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow','downloadPath':os.getcwd()}}
command_result = driver.execute("send_command", params)

driver.get("https://propertyinfo.revenue.wi.gov/WisconsinProd/Search/Disclaimer.aspx?FromUrl=../search/advancedsearch.aspx?mode=advanced")
wait = WebDriverWait(driver,60)
driver.get("https://propertyinfo.revenue.wi.gov/WisconsinProd/search/advancedsearch.aspx?mode=advanced")
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btAgree"))).click()
box = Select(wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#sCriteria"))))
box.select_by_index(4)
iE = driver.find_element(By.ID, "txtCrit")
iE.send_keys('IOWA')
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btAdd"))).click()
box = Select(wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#sCriteria"))))
box.select_by_index(3)
iE = driver.find_element(By.ID, "txtCrit")
iE.send_keys('358407')
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btAdd"))).click()                                  
submit = driver.find_element(By.ID, "btSearch").click()
myTable = driver.find_element(By.CLASS_NAME, 'SearchResults')
dataSelect = myTable.click()

box2 = Select(wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#DTLNavigator_Report2_ReportsListBox"))))
box2.select_by_value('CSVMailingList')

submit2 = driver.find_element(By.ID, "ReportListButton").click()

# wait for csv download to complete
time.sleep(5)
