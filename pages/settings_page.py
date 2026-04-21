from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
import allure
from utils.gestures import scroll_to_text

logger = get_logger()

# ... (existing imports)

class SettingsPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    @allure.step("Open Network & Internet settings")
    def open_network(self):
        logger.info("Attempting to open Network & Internet")
        
        # 🔹 FIX: Use a case-insensitive regex scroll to find the entry point
        # This is MUCH more reliable than a static text search
        try:
            network = scroll_to_text(self.driver, "Network")
            network.click()
        except Exception as e:
            logger.error(f"Could not find Network entry: {e}")
            # Fallback for some emulators where it's called 'Connections'
            network = scroll_to_text(self.driver, "Connections")
            network.click()

        logger.info("Opened Network & Internet")

    @allure.step("Open Wi-Fi settings")
    def open_wifi(self):
        logger.info("Scrolling to Wi-Fi")
        # 🔹 FIX: Ensure we use the full word or regex to avoid matching 'Wired'
        wifi = scroll_to_text(self.driver, "Wi-Fi")
        wifi.click()
        logger.info("Opened Wi-Fi")

    @allure.step("Verify Wi-Fi screen is displayed")
    def is_wifi_screen_open(self):
        logger.info("Checking if Wi-Fi screen is open")
        # 🔹 FIX: Use visibility check rather than just presence
        try:
            wifi_title = self.wait.until(
                EC.visibility_of_element_located((
                    "-android uiautomator",
                    'new UiSelector().textMatches("(?i)Wi-Fi")'
                ))
            )
            result = True
        except:
            result = False

        logger.info(f"Wi-Fi screen open: {result}")
        return result

    @allure.step("Toggle Wi-Fi and validate state change")
    def toggle_wifi(self):
        logger.info("Attempting to toggle Wi-Fi")

        # 🔹 FIX: Some switches have a specific ID, but className is okay.
        # Ensure we wait for visibility.
        toggle = self.wait.until(
            EC.visibility_of_element_located((
                "-android uiautomator",
                'new UiSelector().className("android.widget.Switch")'
            ))
        )

        state_before = toggle.get_attribute("checked") == "true"
        logger.info(f"Wi-Fi state before: {state_before}")

        toggle.click()
        
        # 🔹 IMPROVEMENT: Use a short wait for the toggle state to actually flip
        import time
        time.sleep(1) 

        # Refresh element
        toggle = self.driver.find_element(
            "-android uiautomator",
            'new UiSelector().className("android.widget.Switch")'
        )

        state_after = toggle.get_attribute("checked") == "true"
        logger.info(f"Wi-Fi state after: {state_after}")

        return state_before, state_after