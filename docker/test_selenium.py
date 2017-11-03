from pyvirtualdisplay import Display
from selenium import webdriver

display = Display(visible=0, size=(1024, 768))
display.start()

print('Inicializando o Chrome.')
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=options)

URL = 'https://example.com'
print('Acessando url.')
driver.get(URL)

print(driver.page_source)

driver.close()
driver.quit()
display.stop()
