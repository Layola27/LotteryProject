import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 🔹 Configuración del navegador
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--headless")  # Para ejecución en segundo plano

# 🔹 Iniciar WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)

# 🔹 URL de la página
url = "https://www.loteriasyapuestas.es/es/resultados/loteria-nacional"
driver.get(url)

# 🔹 Esperar carga de la página
time.sleep(5)

# 🔹 Cerrar popup de cookies si aparece
try:
    boton_cookies = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Solo usar cookies necesarias")]')))
    boton_cookies.click()
except:
    print("⚠️ No se encontró el popup de cookies o ya estaba cerrado.")

# 🔹 Obtener todos los sorteos visibles en la página
sorteos = driver.find_elements(By.CLASS_NAME, "c-resultado-sorteo--loteria-nacional-sabado")

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


# Lista para almacenar los resultados
resultados = []

for i, sorteo in enumerate(sorteos):
    try:
        try:
            # Espera a que la lista de sorteos se cargue nuevamente antes de interactuar
            sorteos = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "c-resultado-sorteo__mas-info")))

            # Asegura que el índice `i` no sea mayor que la cantidad de sorteos encontrados
            if i < len(sorteos):
                boton_info_xpath = f'//*[@id="qa_resultadoSorteo-masInfo-LNAC-{i}"]/p[3]/i'

                # Buscar el botón justo antes de hacer clic
                boton_info = wait.until(EC.presence_of_element_located((By.XPATH, boton_info_xpath)))

                # Intenta hacer clic con diferentes métodos
                try:
                    boton_info.click()  # Método estándar de Selenium
                except:
                    try:
                        ActionChains(driver).move_to_element(boton_info).click().perform()  # Simula movimiento y clic
                    except:
                        driver.execute_script("arguments[0].click();", boton_info)  # JavaScript click

                print(f"✅ Se hizo clic en '+ Info' para el sorteo {i}")
                time.sleep(2)  # Esperar a que la información se expanda
            else:
                print(f"⚠️ El botón '+ Info' no se encontró para el sorteo {i}")

        except Exception as e:
            print(f"❌ Error al intentar hacer clic en '+ Info' para el sorteo {i}: {e}")



        # 📌 Extraer la fecha del sorteo
        try:
            fecha_sorteo_xpath = f'//*[@id="qa_resultadoSorteo-fecha-LNAC-{i}"]'
            fecha_sorteo_element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, fecha_sorteo_xpath)))
            fecha_sorteo = fecha_sorteo_element.text.strip() if fecha_sorteo_element.text.strip() else "N/A"
        except:
            fecha_sorteo = "N/A"

        # 📌 Esperar a que la sección de detalles del sorteo se expanda antes de extraer los datos
        try:
            detalles_xpath = f'//*[@id="more-info-LNAC-{i}"]'
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, detalles_xpath)))
        except:
            print(f"⚠️ No se pudo verificar la expansión de los detalles para el sorteo {i}")

        # 📌 Extraer premios de manera dinámica
        try:
            premios_xpath = f'//*[@id="qa_resultadoSorteo-escrutinio-LNAC-{i}"]//td[contains(@class, "c-resultado-escrutinio__td--aliado-derecha")]/span'
            premios_elementos = driver.find_elements(By.XPATH, premios_xpath)
            
            premios_texto = [p.text.strip() for p in premios_elementos if p.text.strip()]
            
            # Validar si hay suficientes premios
            primer_premio = premios_texto[0] if len(premios_texto) > 0 else "N/A"
            segundo_premio = premios_texto[1] if len(premios_texto) > 1 else "N/A"
            reintegro = premios_texto[2] if len(premios_texto) > 2 else "N/A"

        except Exception as e:
            print(f"⚠️ No se pudieron extraer los premios del sorteo {i}: {e}")
            primer_premio, segundo_premio, reintegro = "N/A", "N/A", "N/A"

        # 📌 Extraer reintegros desde la lista de `<li>`
        try:
            reintegro_xpath = f'//*[@id="qa_resultadoSorteo-sorteo-LNAC-{i}"]//ul[@class="c-resultado-sorteo__reintegros"]/li'
            reintegro_elementos = driver.find_elements(By.XPATH, reintegro_xpath)
            
            # Unir los valores de los reintegros encontrados
            reintegro = ", ".join([elem.text.strip() for elem in reintegro_elementos if elem.text.strip()])
            if not reintegro:
                reintegro = "N/A"
        except:
            reintegro = "N/A"

        print(f"📅 {fecha_sorteo} | 🏆 1º Premio: {primer_premio} | 🥈 2º Premio: {segundo_premio} | 🔄 Reintegro: {reintegro}")


        resultados.append([fecha_sorteo, primer_premio, segundo_premio, reintegro])

    except Exception as e:
        print(f"❌ Error en sorteo {i}: {e}")

# 🔹 Convertir los datos a un DataFrame
df = pd.DataFrame(resultados, columns=["Fecha Sorteo", "1er Premio", "2do Premio", "Reintegro"])

# # 🔹 Guardar en CSV
# df.to_csv("data/raw/resultados_loteria_nacional.csv", index=False)
# print("✅ Datos guardados en 'data/raw/resultados_loteria_nacional.csv'.")

# 🔹 Cerrar el navegador
driver.quit()
