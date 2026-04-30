from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options



import time


Service  = Service(executable_path = "/usr/local/bin/chromedriver.exe")

brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

options = Options()
options.binary_location = brave_path


driver = webdriver.Chrome(service=Service, options=options)
driver.get("https://google.com")

time.sleep(10)
driver.quit()
