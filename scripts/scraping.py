import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 🔹 Configurar navegador
chrome_options = Options()
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
wait = WebDriverWait(driver, 10)

# 🔹 Cerrar el popup de cookies si aparece
try:
    boton_cookies = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Solo usar cookies necesarias")]')))
    boton_cookies.click()
    print("✅ Popup de cookies cerrado.")
except:
    print("⚠️ No se encontró el popup de cookies o ya estaba cerrado.")

# 🔹 Función para seleccionar una fecha en el calendario
def seleccionar_fecha(id_input, dia, mes, anio):
    fecha_input = driver.find_element(By.ID, id_input)
    fecha_input.click()
    time.sleep(1)
    
    # Seleccionar mes y año
    select_mes = Select(driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[1]'))
    select_mes.select_by_value(str(mes))
    select_anio = Select(driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[2]'))
    select_anio.select_by_value(str(anio))
    
    # Seleccionar día
    dia_elemento = driver.find_element(By.XPATH, f'//a[text()="{dia}"]')
    dia_elemento.click()

# 🔹 Seleccionar fecha DESDE (1 de enero de 1995)
seleccionar_fecha("qa_resultadoSorteo-buscador-fechaDesde-LNAC", 1, 0, 1995)  # Meses van de 0 a 11
print("✅ Fecha DESDE establecida: 01/01/1995")

# 🔹 Seleccionar fecha HASTA (hoy)
hoy = datetime.now()
seleccionar_fecha("qa_resultadoSorteo-buscador-fechaHasta-LNAC", hoy.day, hoy.month - 1, hoy.year)
print(f"✅ Fecha HASTA establecida: {hoy.strftime('%d/%m/%Y')}")

# 🔹 Hacer clic en el botón "Buscar"
try:
    boton_buscar = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Buscar")]')))
    boton_buscar.click()
    print("✅ Botón 'Buscar' presionado.")

    # 🔹 Esperar hasta que aparezcan los resultados
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "r-resultados-buscador")))
    print("✅ Resultados de sorteos cargados.")
except:
    print("❌ No se encontraron sorteos después de la búsqueda.")
    driver.quit()
    exit()

# 🔹 Obtener contenedor principal de resultados
contenedor_resultados = driver.find_element(By.CLASS_NAME, "r-resultados-buscador")

# 🔹 Obtener todos los sorteos dentro del contenedor
sorteos = contenedor_resultados.find_elements(By.CLASS_NAME, "c-resultado-sorteo--loteria-nacional-sabado")

# Lista para almacenar los datos
resultados = []

# 🔹 Iterar sobre cada sorteo y extraer la información
for sorteo in sorteos:
    try:
        # 📅 Extraer la fecha del sorteo
        fecha_sorteo = sorteo.find_element(By.XPATH, './/p[contains(@id, "qa_resultadoSorteo-fecha")]').text.strip()
        
        # 🔹 Buscar la tabla de premios dentro del sorteo
        try:
            tabla = sorteo.find_element(By.XPATH, './/table[contains(@id, "qa_resultadoSorteo-escrutinio")]')
            filas = tabla.find_elements(By.TAG_NAME, 'tr')

            # Iterar sobre cada fila de la tabla (omitir encabezados)
            for fila in filas[1:]:
                columnas = fila.find_elements(By.TAG_NAME, 'td')
                if len(columnas) >= 2:
                    categoria = columnas[0].text.strip()
                    premio = columnas[1].text.strip()
                    
                    # 🔹 Buscar y hacer clic en el botón de agraciados si existe
                    try:
                        boton_agraciados = columnas[2].find_element(By.TAG_NAME, 'a')
                        boton_agraciados.click()
                        time.sleep(2)  # Esperar a que cargue la información
                        
                        # Extraer información de agraciados
                        ubicaciones = driver.find_elements(By.CLASS_NAME, 'ubicaciones')
                        for ubicacion in ubicaciones:
                            direccion = ubicacion.find_element(By.XPATH, './/span[contains(text(), "Dirección:")]/following-sibling::span').text.strip()
                            poblacion = ubicacion.find_element(By.XPATH, './/span[contains(text(), "Población:")]/following-sibling::span').text.strip()
                            provincia = ubicacion.find_element(By.XPATH, './/span[contains(text(), "Provincia:")]/following-sibling::span').text.strip()
                            codigo_postal = ubicacion.find_element(By.XPATH, './/span[contains(text(), "Código Postal:")]/following-sibling::span').text.strip()
                            telefono = ubicacion.find_element(By.XPATH, './/span[contains(text(), "Teléfono:")]/following-sibling::span').text.strip()

                            print(f"📍 {categoria} - {direccion}, {poblacion}, {provincia} ({codigo_postal}), Tel: {telefono}")
                            
                            resultados.append([fecha_sorteo, categoria, premio, direccion, poblacion, provincia, codigo_postal, telefono])
                        
                        # Cerrar el modal
                        driver.find_element(By.CLASS_NAME, "ui-dialog-titlebar-close").click()
                        time.sleep(1)
                    except:
                        resultados.append([fecha_sorteo, categoria, premio, "N/A", "N/A", "N/A", "N/A", "N/A"])
        except:
            print(f"⚠️ No se encontró tabla de premios para el sorteo {fecha_sorteo}")
    except Exception as e:
        print(f"⚠️ Error extrayendo datos del sorteo: {e}")

# 🔹 Convertir a DataFrame de pandas y mostrar en consola
df = pd.DataFrame(resultados, columns=["Fecha Sorteo", "Categoría", "Premio", "Dirección", "Población", "Provincia", "Código Postal", "Teléfono"])
print("\n📊 Datos extraídos:\n", df)

# 🔹 Guardar en CSV
df.to_csv('data/raw/resultados_loteria_nacional.csv', index=False)
print("✅ Datos guardados en 'data/raw/resultados_loteria_nacional.csv'.")

# 🔹 Cerrar el navegador
driver.quit()
