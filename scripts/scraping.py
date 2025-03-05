import time
import datetime
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 🔹 Configurar opciones del navegador (modo visible, NO headless)
chrome_options = Options()
# chrome_options.add_argument("--headless")  # ❌ NO usar headless para ver el navegador
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 🔹 Iniciar WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 🔹 URL de la página de SELAE
url = "https://www.loteriasyapuestas.es/es/resultados/loteria-nacional"
driver.get(url)

# 🔹 Esperar a que la página cargue completamente
time.sleep(5)

# 🔹 Cerrar el popup de cookies si aparece
try:
    wait = WebDriverWait(driver, 5)
    boton_cookies = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Solo usar cookies necesarias")]')))
    boton_cookies.click()
    print("✅ Popup de cookies cerrado.")
except:
    print("⚠️ No se encontró el popup de cookies o ya estaba cerrado.")

# 🔹 Seleccionar la fecha "Desde"
wait = WebDriverWait(driver, 15)
try:
    fecha_desde = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[contains(@class, "c-buscador-sorteos__input-fecha-inicial")]')))
    fecha_desde.click()
    time.sleep(2)
    
    Select(driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[1]')).select_by_value("0")  # Enero
    Select(driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[2]')).select_by_value("1995")
    
    driver.find_element(By.XPATH, '//table[@class="ui-datepicker-calendar"]//a[text()="1"]').click()
    print("✅ Fecha 'Desde' seleccionada: 01/01/1995")
except:
    print("❌ No se pudo seleccionar la fecha 'Desde'.")
    driver.quit()
    exit()

# 🔹 Seleccionar la fecha "Hasta" con la fecha actual
fecha_actual = datetime.datetime.now()
mes_actual = str(fecha_actual.month - 1)  # Los valores de los meses van de 0 a 11
anio_actual = str(fecha_actual.year)
dia_actual = str(fecha_actual.day)

try:
    fecha_hasta = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[contains(@class, "c-buscador-sorteos__input-fecha-final")]')))
    fecha_hasta.click()
    time.sleep(2)

    Select(driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[1]')).select_by_value(mes_actual)
    Select(driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[2]')).select_by_value(anio_actual)

    driver.find_element(By.XPATH, f'//table[@class="ui-datepicker-calendar"]//a[text()="{dia_actual}"]').click()
    print(f"✅ Fecha 'Hasta' seleccionada: {fecha_actual.strftime('%d/%m/%Y')}")
except:
    print("❌ No se pudo seleccionar la fecha 'Hasta'.")
    driver.quit()
    exit()

# 🔹 Hacer clic en el botón "Buscar"
try:
    boton_buscar = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Buscar")]')))
    boton_buscar.click()
    print("✅ Botón 'Buscar' presionado.")

    # 🔹 Esperar hasta que aparezcan los resultados
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@id, "qa_resultadoSorteo-sorteo-LNAC")]')))
    print("✅ Resultados de sorteos cargados.")
except:
    print("❌ No se encontraron sorteos después de la búsqueda.")
    driver.quit()
    exit()

# 🔹 Esperar a que aparezcan los resultados
try:
    primer_sorteo = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@id, "qa_resultadoSorteo-sorteo-LNAC")]')))
    print("✅ Resultados de sorteos cargados.")
except:
    print("❌ No se encontraron sorteos.")
    driver.quit()
    exit()

# 🔹 Extraer datos del primer sorteo
try:
    fecha_sorteo = driver.find_element(By.XPATH, '//*[@id="qa_resultadoSorteo-fecha-LNAC-0"]/span').text
    # primer_premio = driver.find_element(By.XPATH, '//h3[contains(text(), "1ER PREMIO")]/following-sibling::p').text
    # segundo_premio = driver.find_element(By.XPATH, '//h3[contains(text(), "2º PREMIO")]/following-sibling::p').text

    print(f"📅 Fecha Sorteo: {fecha_sorteo}")
    # print(f"🥇 1er Premio: {primer_premio}")
    # print(f"🥈 2º Premio: {segundo_premio}")
except:
    print("❌ No se pudo extraer la información del primer sorteo.")
    driver.quit()
    exit()

# # 🔹 Abrir la pestaña "+ Info" para ver agraciados
# try:
#     boton_info = driver.find_element(By.XPATH, '//a[contains(text(), "+ Info")]')
#     boton_info.click()
#     time.sleep(2)

#     agraciados = driver.find_element(By.XPATH, '//table[contains(@class, "c-resultado-sorteo--detalles")]').text
#     print(f"🎟️ Agraciados: {agraciados}")
# except:
#     print("⚠️ No se encontró información de agraciados.")

# 🔹 Guardar la información en un archivo CSV
csv_file = "data/raw/loteria_nacional.csv"

with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Fecha Sorteo"])
    writer.writerow([fecha_sorteo])

print(f"✅ Datos guardados en {csv_file}")

# 🔹 Cerrar el navegador
driver.quit()
