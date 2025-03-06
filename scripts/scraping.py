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
import pandas as pd
from datetime import datetime
import json

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

# 📌 Cargar todos los resultados disponibles presionando el botón "Más Resultados"
def cargar_todos_los_resultados(driver):
    boton_mas_resultados_xpath = '//*[@id="qa_resultadoSorteo-buscador-botonMasResultados-LNAC"]'

    while True:
        try:
            # Buscar el botón "Más Resultados"
            boton = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, boton_mas_resultados_xpath)))
            
            # Desplazar hasta el botón y hacer clic
            driver.execute_script("arguments[0].scrollIntoView();", boton)
            driver.execute_script("arguments[0].click();", boton)

            print("✅ Se presionó el botón 'Más Resultados'.")

            # Esperar un momento para que carguen los nuevos sorteos
            time.sleep(10)

        except Exception as e:
            print("🚀 No hay más resultados para cargar.")
            break  # Salir del bucle si el botón ya no está disponible

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

# Llamar la función antes de iniciar la extracción de datos
cargar_todos_los_resultados(driver)

# Lista para almacenar los resultados
resultados = []

# Conjunto para almacenar todas las categorías de premios dinámicamente
categorias_globales = set()

for i in range(200):  # Ajusta 'num_sorteos' con el total de sorteos a extraer

    # 📌 Hacer clic en el botón "+ Info" para expandir los detalles
    try:
        boton_info_xpath = f'//*[@id="qa_resultadoSorteo-masInfo-LNAC-{i}"]'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, boton_info_xpath)))
        
        boton_info = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, boton_info_xpath)))
        driver.execute_script("arguments[0].scrollIntoView();", boton_info)
        driver.execute_script("arguments[0].click();", boton_info)

        # Esperar a que la información se expanda
        detalles_xpath = f'//*[@id="more-info-LNAC-{i}"]'
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, detalles_xpath)))

        print(f"✅ Se hizo clic en '+ Info' para el sorteo {i}")

    except Exception as e:
        print(f"⚠️ No se pudo hacer clic en '+ Info' para el sorteo {i}: {e}")
        continue  # Si no se puede abrir el sorteo, pasamos al siguiente

    # 📌 Extraer la fecha del sorteo
    try:
        fecha_sorteo_xpath = f'//*[@id="qa_resultadoSorteo-fecha-LNAC-{i}"]'
        fecha_sorteo_element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, fecha_sorteo_xpath)))
        fecha_sorteo = fecha_sorteo_element.text.strip()
    except:
        fecha_sorteo = "N/A"

    # 📌 Extraer el tipo de sorteo
    try:
        tipo_sorteo_xpath = f'//*[@id="qa_resultadoSorteo-nombreSorteo-LNAC-{i}"]'
        tipo_sorteo_element = driver.find_element(By.XPATH, tipo_sorteo_xpath)
        tipo_sorteo = tipo_sorteo_element.text.strip() if tipo_sorteo_element.text.strip() else "Sorteo Regular"
    except:
        tipo_sorteo = "Sorteo Regular"

    # 📌 Extraer reintegros correctamente
    try:
        reintegro_xpath = f'//*[@id="qa_resultadoSorteo-sorteo-LNAC-{i}"]//ul[@class="c-resultado-sorteo__reintegros"]/li'
        reintegro_elementos = driver.find_elements(By.XPATH, reintegro_xpath)
        reintegros = [elem.text.strip().replace("R", "").strip() for elem in reintegro_elementos if elem.text.strip()]
        reintegro_lista = ", ".join(reintegros) if reintegros else "N/A"
    except:
        reintegro_lista = "N/A"

    # 📌 Extraer fracción y serie (si existen)
    try:
        fraccion_xpath = f'//*[@id="qa_resultadoSorteo-fraccion-LNAC-{i}"]'
        serie_xpath = f'//*[@id="qa_resultadoSorteo-serie-LNAC-{i}"]'

        fraccion_element = driver.find_elements(By.XPATH, fraccion_xpath)
        serie_element = driver.find_elements(By.XPATH, serie_xpath)

        fraccion = fraccion_element[0].text.strip() if fraccion_element else "N/A"
        serie = serie_element[0].text.strip() if serie_element else "N/A"
    except:
        fraccion, serie = "N/A", "N/A"



    # 📌 Extraer premios dinámicamente
    try:
        categorias_xpath = f'//*[@id="qa_resultadoSorteo-escrutinio-LNAC-{i}"]//span[contains(@class, "c-resultado-escrutinio__categoria")]'
        premios_xpath = f'//*[@id="qa_resultadoSorteo-escrutinio-LNAC-{i}"]//span[contains(@class, "c-resultado-escrutinio__premios")]'

        categorias_elementos = driver.find_elements(By.XPATH, categorias_xpath)
        premios_elementos = driver.find_elements(By.XPATH, premios_xpath)

        categorias_texto = [c.text.strip() for c in categorias_elementos if c.text.strip()]
        premios_texto = [p.text.strip() for p in premios_elementos if p.text.strip()]

        premios_dict = {}
        for idx, categoria in enumerate(categorias_texto):
            premios_dict[categoria] = premios_texto[idx] if idx < len(premios_texto) else "N/A"

        # Agregar categorías al conjunto global
        categorias_globales.update(premios_dict.keys())

    except Exception as e:
        print(f"⚠️ No se pudieron extraer los premios del sorteo {i}: {e}")
        premios_dict = {}



    # 📌 Extraer puntos de venta de los premios principales (1º y 2º premio)
    premios_puntos_venta = {}

    # XPaths específicos del 1er y 2º premio
    premios_xpaths = {
        "1er Premio": f'//*[@id="qa_resultadoSorteo-premio-LNAC-{i}G10"]',
        "2º Premio": f'//*[@id="qa_resultadoSorteo-premio-LNAC-{i}Z11"]'
    }

    for categoria, premio_xpath in premios_xpaths.items():
        try:
            # Encontrar el elemento del premio
            premio_elementos = driver.find_elements(By.XPATH, premio_xpath)

            if premio_elementos:
                premio_element = premio_elementos[0]  
                driver.execute_script("arguments[0].scrollIntoView();", premio_element)
                ActionChains(driver).move_to_element(premio_element).click().perform()

                # 📌 Esperar a que el modal se abra y cargue completamente
                modal_xpath = '//*[@id="inline_content"]'
                WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, modal_xpath)))

                # 📌 Esperar a que los puntos de venta estén disponibles dentro del modal
                puntos_venta_xpath = '//div[@class="contenedorAgraciados"]//div[@class="puntoVentaPremio"]'
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, puntos_venta_xpath)))

                # 📌 Extraer la información del punto de venta
                puntos_venta = []
                puntos_venta_elementos = driver.find_elements(By.XPATH, puntos_venta_xpath)

                for pv_element in puntos_venta_elementos:
                    try:
                        direccion = pv_element.find_element(By.XPATH, './/p[span[contains(text(), "Dirección:")]]').text.replace("Dirección:", "").strip()
                        poblacion = pv_element.find_element(By.XPATH, './/p[span[contains(text(), "Población:")]]').text.replace("Población:", "").strip()
                        provincia = pv_element.find_element(By.XPATH, './/p[span[contains(text(), "Provincia:")]]').text.replace("Provincia:", "").strip()
                        codigo_postal = pv_element.find_element(By.XPATH, './/p[span[contains(text(), "Código Postal:")]]').text.replace("Código Postal:", "").strip()
                        telefono = pv_element.find_element(By.XPATH, './/p[span[contains(text(), "Teléfono:")]]').text.replace("Teléfono:", "").strip()

                        puntos_venta.append({
                            "Dirección": direccion,
                            "Población": poblacion,
                            "Provincia": provincia,
                            "Código Postal": codigo_postal,
                            "Teléfono": telefono
                        })
                    except Exception as e:
                        print(f"⚠️ Error extrayendo información de punto de venta: {e}")
                        continue  

                # Guardar en JSON dentro de la celda del CSV
                premios_puntos_venta[categoria] = json.dumps(puntos_venta, ensure_ascii=False)

                # 📌 Cerrar el modal
                cerrar_modal_xpath = '//*[@id="cboxClose"]'
                try:
                    close_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, cerrar_modal_xpath)))
                    close_button.click()
                    WebDriverWait(driver, 3).until(EC.invisibility_of_element_located((By.XPATH, modal_xpath)))
                    print(f"✅ Modal de {categoria} cerrado correctamente.")
                except Exception as e:
                    print(f"⚠️ No se pudo cerrar el modal de {categoria}: {e}")

                print(f"✅ Extraída información del punto de venta para {categoria} en sorteo {i}")

            else:
                print(f"⚠️ No se encontró el elemento del premio para {categoria} en sorteo {i}")
                premios_puntos_venta[categoria] = json.dumps([])

        except Exception as e:
            print(f"⚠️ No se pudo obtener información del punto de venta para {categoria} en el sorteo {i}: {e}")
            premios_puntos_venta[categoria] = json.dumps([])


    # 📌 Construcción del resultado del sorteo
    resultado_fila = {
        "Fecha Sorteo": fecha_sorteo,
        "Tipo Sorteo": tipo_sorteo,
        "Reintegros": reintegro_lista,
        "Fracción": fraccion,
        "Serie": serie,
    }

    # 📌 Agregar premios y sus puntos de venta al diccionario
    for categoria in categorias_globales:
        resultado_fila[categoria] = premios_dict.get(categoria, "N/A")

    for categoria in ["1er Premio", "2º Premio"]:
        resultado_fila[f"{categoria} - Puntos de Venta"] = premios_puntos_venta.get(categoria, json.dumps([]))

    # 📌 Agregar la fila a la lista de resultados
    resultados.append(resultado_fila)
    
# Guardar CSV con timestamp
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
file_name = f"data/raw/resultados_loteria_nacional-{timestamp}.csv"
df = pd.DataFrame(resultados)
df.to_csv(file_name, index=False)

print(f"✅ Datos guardados en '{file_name}'.")


# # 🔹 Guardar en CSV
# df.to_csv("data/raw/resultados_loteria_nacional.csv", index=False)
# print("✅ Datos guardados en 'data/raw/resultados_loteria_nacional.csv'.")

# 🔹 Cerrar el navegador
driver.quit()
