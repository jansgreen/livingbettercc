from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


def exequatur_consurt(nombre: str) -> bool:

    """Devuelve True si el nombre consultado tiene exequátur en MSP, False en caso contrario."""
    options = Options()
    options.add_argument('--headless')  # para que no abra ventana
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://msp.gob.do/web/?page_id=276")
        time.sleep(3)  # Espera a que cargue (ajustar según el sitio)

        # Aquí debes identificar bien el campo (esto depende del ID real en el HTML)
        search_input = driver.find_element(By.NAME, "nombre")  # Cambia a lo que corresponda
        search_input.send_keys(nombre)

        submit_button = driver.find_element(By.ID, "btn-consultar")  # Cambia si es otro
        submit_button.click()

        time.sleep(4)  # Esperar a que cargue el resultado

        # Verifica si aparece algún mensaje de exequátur encontrado
        if "Exequátur otorgado" in driver.page_source:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        driver.quit()