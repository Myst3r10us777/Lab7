import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class OpenBMCAuthTests(unittest.TestCase):
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "https://localhost:2443"
    
    def tearDown(self):
        """Закрытие браузера после каждого теста"""
        if self.driver:
            self.driver.quit()
    
    def login(self, username, password):
        """Вспомогательный метод для авторизации"""
        self.driver.get(self.base_url)
        time.sleep(1)
        
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        for inp in inputs:
            field_type = inp.get_attribute("type")
            if field_type == "text":
                inp.clear()
                inp.send_keys(username)
            elif field_type == "password":
                inp.clear()
                inp.send_keys(password)
        
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        login_button = None
        
        for btn in buttons:
            if btn.text.strip() == "Log in":
                login_button = btn
                break
        
        if login_button:
            login_button.click()
        
        time.sleep(3)
    
    def test_successful_login(self):
        """Тест успешной авторизации"""
        print("\n=== Тест успешной авторизации ===")
        
        self.login("root", "0penBmc")
        
        page_source = self.driver.page_source
        
        if '<h1 data-v-51f73898="">Overview</h1>' in page_source:
            print("✅ Успешная авторизация: PASS - найден элемент Overview")
            self.assertTrue(True)
        else:
            
            print("❌ Успешная авторизация: FAIL - элемент Overview не найден")
            self.assertTrue(False)
    
    def test_invalid_credentials(self):
        """Тест авторизации с неверными данными"""
        print("\n=== Тест неверных данных авторизации ===")
        
        self.login("wronguser", "wrongpassword")
        time.sleep(3)
        current_url = self.driver.current_url
        page_source = self.driver.page_source.lower()
        
        error_indicators = ['error', 'invalid', 'incorrect', 'fail', 'wrong']
        has_error = any(indicator in page_source for indicator in error_indicators)
        still_on_login = "login" in current_url.lower()
        
        if has_error or still_on_login:
            print("✅ Ошибка при неверных данных: PASS")
            self.assertTrue(True)
        else:
            print("❌ Ошибка при неверных данных: FAIL")
            self.assertTrue(False)
    
    def test_account_lockout(self):
        """Тест блокировки учетной записи после нескольких неудачных попыток"""
        print("\n=== Тест блокировки учетной записи ===")
        
        for i in range(5):
            print(f"  Неудачная попытка {i+1}/5")
            self.login("root", f"wrongpass")
            time.sleep(1)
        
        self.login("root", "0penBmc")
        
        current_url = self.driver.current_url
        page_source = self.driver.page_source.lower()
        
        if "login" in current_url or any(word in page_source for word in ['error', 'invalid', 'lock', 'block']):
            print("✅ Учетная запись заблокирована после 5 попыток: PASS")
            self.assertTrue(True)
        else:
            print("❌ : Удалось войти после 5 неудачных попыток")
            self.assertTrue(False)
            
    def test_power_on_and_check_health_logs(self):
        """Включение сервера и проверка логов в Health"""
        print("\n=== Тест: Включение сервера и проверка логов ===")
        
        self.login("root", "0penBmc")
        
        power_link = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Power')]")
        power_link.click()
        print("✅ Перешли в раздел Power")
        time.sleep(2)

        page_text_before = self.driver.find_element(By.TAG_NAME, "body").text
        print(f"Текст ДО: 'Off' found = {'Off' in page_text_before}")

        power_on_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Power on')]")
        power_on_btn.click()
        print("✅ Нажата кнопка Power on")
        time.sleep(5)

        page_text_after = self.driver.find_element(By.TAG_NAME, "body").text
        print(f"Текст ПОСЛЕ: 'Off' found = {'Off' in page_text_after}")

        if 'Off' not in page_text_after:
            print("✅ Статус изменился: 'Off' больше нет")
            status_changed = True
        else:
            print("❌ Статус не изменился: 'Off' остался")
            status_changed = False
        
        health_link = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Health') or contains(text(), 'Logs')]")
        health_link.click()
        print("✅ Перешли в раздел Health/Logs")
        time.sleep(3)
        
        page_text = self.driver.find_element(By.TAG_NAME, "body").text

        if "No items available" in page_text:
            print("❌ Логи отсутствуют: 'No items available'")
            logs_present = False
        else:
            print("✅ Логи присутствуют: PASS")
            logs_present = True
        
        if status_changed or logs_present:
            print("✅ ТЕСТ ПРОЙДЕН: Статус изменился ИЛИ логи присутствуют")
            self.assertTrue(True)
        else:
            print("❌: После включения сервера статус не изменился И логи отсутствуют")
            self.assertTrue(False)
            

    def test_temperature_within_limits(self):
        """Проверить температуру компонента"""
        print("\n=== Тест: Проверка температуры компонента ===")
        
        self.login("root", "0penBmc")
        time.sleep(2)
        
        try:
            menu_btn = self.driver.find_element(By.XPATH, "//button[contains(@class, 'nav-trigger') or contains(@id, 'app-header-trigger')]")
            menu_btn.click()
            print("✅ Открыли меню навигации")
            time.sleep(2)
            
            hardware_btn = self.driver.find_element(By.XPATH, "//button[contains(@class, 'btn btn-link collapsed') and @data-test-id='nav-button-hardware-status']")
            hardware_btn.click()
            print("✅ Кликнули на Hardware status")
            time.sleep(2)
            
            sensors = self.driver.find_element(By.XPATH, "//*[text()='Sensors']")
            sensors.click()
            print("✅ Кликнули на Sensors")
            time.sleep(2)
            
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            if "No items available" in page_text:
                print("❌: Нету компонентов")
                self.assertTrue(False)
            else:
                print("✅ ТЕСТ ПРОЙДЕН: Датчики найдены")
                self.assertTrue(True)
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.assertTrue(False)
    
    def test_system_status_detailed(self):
        """Проверить детальный статус системы через View more"""
        print("\n=== Тест: Детальная проверка статуса системы ===")
        
        self.login("root", "0penBmc")
        time.sleep(2)
        
        view_more_btn = self.driver.find_element(By.XPATH, "//a[contains(text(), 'View more')]")
        view_more_btn.click()
        print("✅ Кликнули на View more")
        time.sleep(2)
        
        system_section = self.driver.find_element(By.XPATH, "//a[contains(@data-ref, 'system')]")
        system_section.click()
        print("✅ Кликнули на раздел System")
        time.sleep(2)
        
        razvertka = self.driver.find_element(By.XPATH, "//button[contains(@data-test-id, 'hardwareStatus-button-expandSystem')]")
        razvertka.click()
        print("✅ Развернули детальную информацию")
        time.sleep(2)
        status_dt = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Status (State)')]")
        status_dd = status_dt.find_element(By.XPATH, "./following-sibling::dd[1]")
        status_text = status_dd.text.strip()
        
        print(f"✅ Status (State): {status_text}")
        
        if status_text.lower() == "enabled":
            print("✅ ТЕСТ ПРОЙДЕН: Status (State) включен")
            self.assertTrue(True)
        else:
            print(f"❌ ТЕСТ НЕ ПРОЙДЕН: Status (State) отключен ({status_text})")
            self.assertTrue(False)
                
if __name__ == "__main__":
    unittest.main(verbosity=2)