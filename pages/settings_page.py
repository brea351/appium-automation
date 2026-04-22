import time
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
from utils.gestures import scroll_to_text

logger = get_logger()

class SettingsPage:
    def __init__(self, driver):
        self.driver = driver
        # Standard wait for CI lag
        self.wait = WebDriverWait(driver, 20)

    @allure.step("Open Network & Internet settings")
    def open_network(self):
        """
        🚀 CI ENHANCED: Tries UI navigation first, falls back to Android Intent 
        if the menus are not visible.
        """
        logger.info("Attempting to open Network & Internet")
        try:
            # 1. Try standard UI scroll/click
            network = scroll_to_text(self.driver, "Network")
            network.click()
            logger.info("Opened Network & Internet via UI")
        except Exception as e:
            logger.warning(f"UI navigation failed: {e}. Trying Direct Intent...")
            try:
                # 2. THE NUCLEAR OPTION: Direct Deep Link to Wi-Fi settings
                # This works even if the 'Network' button is hidden or different.
                self.driver.execute_script('mobile: startActivity', {
                    'intent': 'android.settings.WIFI_SETTINGS'
                })
                logger.info("Opened settings via Intent navigation")
            except Exception as intent_e:
                logger.error(f"Intent failed: {intent_e}. Final attempt via resource-id.")
                # 3. Last resort: click the first dashboard item
                self.driver.find_element(AppiumBy.ID, "android:id/title").click()

    @allure.step("Open Wi-Fi settings")
    def open_wifi(self):
        """
        If we used an Intent in the previous step, we might already be here.
        If not, we perform the click.
        """
        logger.info("Checking if Wi-Fi navigation is required")
        if self.is_wifi_screen_open():
            logger.info("Already on Wi-Fi screen (likely via Intent)")
            return

        try:
            wifi = self.wait.until(
                EC.element_to_be_clickable((
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().textMatches("(?i)Wi.*Fi")'
                ))
            )
            wifi.click()
            logger.info("Clicked Wi-Fi entry")
        except Exception:
            logger.warning("Wi-Fi not clickable, attempting scroll...")
            wifi = scroll_to_text(self.driver, "Wi-Fi")
            wifi.click()

    @allure.step("Verify Wi-Fi screen is displayed")
    def is_wifi_screen_open(self):
        """
        Uses 'any_of' to check for the switch OR the title for better CI stability.
        """
        logger.info("Checking if Wi-Fi screen is open")
        try:
            self.wait.until(
                EC.any_of(
                    EC.visibility_of_element_located((AppiumBy.CLASS_NAME, "android.widget.Switch")),
                    EC.visibility_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i).*Wi.*Fi.*")'))
                )
            )
            result = True
        except Exception:
            result = False

        logger.info(f"Wi-Fi screen open: {result}")
        return result

    @allure.step("Toggle Wi-Fi and validate state change")
    def toggle_wifi(self):
        logger.info("Attempting to toggle Wi-Fi")

        toggle = self.wait.until(
            EC.visibility_of_element_located((AppiumBy.CLASS_NAME, "android.widget.Switch"))
        )

        state_before = toggle.get_attribute("checked") == "true"
        logger.info(f"Wi-Fi state before: {state_before}")

        toggle.click()
        
        # Buffer for slow emulator processing
        time.sleep(2) 

        # Refresh reference
        toggle = self.driver.find_element(AppiumBy.CLASS_NAME, "android.widget.Switch")
        state_after = toggle.get_attribute("checked") == "true"
        
        logger.info(f"Wi-Fi state after: {state_after}")
        return state_before, state_after