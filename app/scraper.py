import sys
import types
import time
from packaging.version import Version

if sys.version_info >= (3, 12):
    class LooseVersion(Version):
        def __init__(self, vstring):
            self.vstring = vstring
            super().__init__(vstring)
        @property
        def version(self):
            return self.release

    distutils = types.ModuleType("distutils")
    distutils.version = types.ModuleType("distutils.version")
    distutils.version.LooseVersion = LooseVersion
    sys.modules["distutils"] = distutils
    sys.modules["distutils.version"] = distutils.version

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import undetected_chromedriver as uc

class AdresScraper:
    """
    Scraper class for ADRES website handling specific table structures.
    """

    BASE_URL = "https://www.adres.gov.co/consulte-su-eps"

    KEY_MAPPING = {
        # Table 1 Keys (Vertical)
        "TIPO DE IDENTIFICACIÓN": "type_identity",
        "NÚMERO DE IDENTIFICACION": "identity",
        "NOMBRES": "names",
        "APELLIDOS": "last_names",
        "FECHA DE NACIMIENTO": "birthday",
        "DEPARTAMENTO": "province",
        "MUNICIPIO": "municipality",

        # Table 2 Keys (Horizontal Headers)
        "ESTADO": "status",
        "ENTIDAD": "entity",
        "REGIMEN": "regime",
        "FECHA DE AFILIACIÓN EFECTIVA": "effective_date_membership",
        "FECHA DE FINALIZACIÓN DE AFILIACIÓN": "end_date_membership",
        "TIPO DE AFILIADO": "type_member"
    }

    def _get_driver_options(self):
        """Configure Chrome options."""
        options = uc.ChromeOptions()
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--mute-audio")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        return options

    def _switch_to_iframe(self, driver: uc.Chrome, wait: WebDriverWait):
        """Finds and switches to the iframe containing the form."""
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            iframes = driver.find_elements(By.TAG_NAME, "iframe")

            for frame in iframes:
                driver.switch_to.default_content()
                try:
                    driver.switch_to.frame(frame)
                    if len(driver.find_elements(By.ID, "txtNumDoc")) > 0:
                        return True
                except:
                    continue

            driver.switch_to.default_content()
            return False
        except Exception:
            return False

    def _clean_text(self, text: str) -> str:
        """Helper to clean string data."""
        return text.strip().replace("\n", " ") if text else ""

    def _extract_table_data(self, driver: uc.Chrome) -> dict:
        """
        Extracts data from the two distinct tables in the popup.
        Table 1: Vertical (Basic Info).
        Table 2: Horizontal (Affiliation Data).
        """
        data = {}

        # Locate all tables in the result page
        tables = driver.find_elements(By.TAG_NAME, "table")

        # --- PROCESS TABLE 1: Basic Information (Vertical Key-Value) ---
        if len(tables) > 0:
            basic_info_rows = tables[0].find_elements(By.TAG_NAME, "tr")
            for row in basic_info_rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                # We expect 2 cells: [Label] [Value]
                if len(cells) == 2:
                    raw_key = self._clean_text(cells[0].text)
                    value = self._clean_text(cells[1].text)

                    # Map Spanish key to JSON key
                    if raw_key in self.KEY_MAPPING:
                        data[self.KEY_MAPPING[raw_key]] = value

        # --- PROCESS TABLE 2: Affiliation Data (Horizontal Headers) ---
        if len(tables) > 1:
            aff_rows = tables[1].find_elements(By.TAG_NAME, "tr")

            # We need at least 2 rows: Header and Data
            if len(aff_rows) >= 2:
                # Row 0 contains Headers (th or td with blue background)
                header_cells = aff_rows[0].find_elements(By.XPATH, ".//*[self::td or self::th]")
                # Row 1 contains Values
                value_cells = aff_rows[1].find_elements(By.TAG_NAME, "td")

                # Iterate by index to match Header[i] -> Value[i]
                limit = min(len(header_cells), len(value_cells))
                for i in range(limit):
                    raw_header = self._clean_text(header_cells[i].text)
                    val = self._clean_text(value_cells[i].text)

                    if raw_header in self.KEY_MAPPING:
                        data[self.KEY_MAPPING[raw_header]] = val

        return data

    def get_adres_info(self, document_number: str) -> dict:
        """Main execution method."""
        driver = uc.Chrome(options=self._get_driver_options(), version_main=142)
        result_data = {}

        try:
            driver.get(self.BASE_URL)
            wait = WebDriverWait(driver, 20)

            self._switch_to_iframe(driver, wait)

            try:
                doc_type = wait.until(EC.element_to_be_clickable((By.ID, "tipoDoc")))
                Select(doc_type).select_by_value("CC")
            except:
                pass

            input_field = wait.until(EC.element_to_be_clickable((By.ID, "txtNumDoc")))
            input_field.click()
            input_field.clear()

            for digit in document_number:
                input_field.send_keys(digit)
                time.sleep(0.05)

            consult_btn = driver.find_element(By.ID, "btnConsultar")
            main_window = driver.current_window_handle
            consult_btn.click()

            # Wait for popup
            WebDriverWait(driver, 60).until(EC.number_of_windows_to_be(2))

            # Switch to popup
            for handle in driver.window_handles:
                if handle != main_window:
                    driver.switch_to.window(handle)
                    break

            try:
                # Wait up to 10 seconds for body to load to ensure text is present
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                not_found_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'no se encuentra en BDUA')]")

                if len(not_found_elements) > 0:
                    result_data = {"found": False}
                else:
                    # Case: User exists, wait for table
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                    result_data = self._extract_table_data(driver)
                    result_data["found"] = True

            except Exception as e:
                print(f"Error extracting popup data: {e}")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass

        return result_data
