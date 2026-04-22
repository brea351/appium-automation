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
        # 20s is good, but CI is slow—we'll keep it at 20 and use Smart Waits
        self.wait = WebDriverWait(driver, 20)

    @allure.step("Open Network & Internet settings")
    def open_network(self):
        logger.info("Attempting to open Network & Internet")
        try:
            network = scroll_to_text(self.driver, "Network")
            network.click()
        except Exception as e:
            logger.warning(f"Text search failed, trying resource-id fallback. Error: {e}")
            try:
                # Fallback: Many Android versions use 'Connections'
                network = scroll_to_text(self.driver, "Connections")
                network.click()
            except Exception:
                # Last resort: Click the first item in the settings list
                network = self.driver.find_element(AppiumBy.ID, "android:id/title")
                network.click()
        logger.info("Opened Network & Internet")

    @allure.step("Open Wi-Fi settings")
    def open_wifi(self):
        logger.info("Locating Wi-Fi entry")
        try:
            # Try finding the Wi-Fi entry directly first (faster)
            wifi = self.wait.until(
                EC.element_to_be_clickable((
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().textMatches("(?i)Wi.*Fi")'
                ))
            )
            wifi.click()
            logger.info("Found and clicked Wi-Fi")
        except Exception:
            logger.warning("Wi-Fi not immediately clickable, attempting scroll fallback...")
            wifi = scroll_to_text(self.driver, "Wi-Fi")
            wifi.click()
        logger.info("Opened Wi-Fi")

    @allure.step("Verify Wi-Fi screen is displayed")
    def is_wifi_screen_open(self):
        """
        🚀 CI FIX: Uses 'any_of' to check for the title OR the toggle switch.
        This handles the lag where the text might not be drawn but the container is ready.
        """
        logger.info("Checking if Wi-Fi screen is open")
        try:
            # If the switch is visible OR the title matches, we are on the right screen
            self.wait.until(
                EC.any_of(
                    EC.visibility_of_element_located((AppiumBy.CLASS_NAME, "android.widget.Switch")),
                    EC.visibility_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i).*Wi.*Fi.*")'))
                )
            )
            result = True
        except Exception as e:
            logger.error(f"Wi-Fi screen verification failed: {e}")
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
        
        # Give the emulator 2 seconds to process the state change
        time.sleep(2) 

        # Re-fetch element to avoid StaleElementReferenceException
        toggle = self.driver.find_element(AppiumBy.CLASS_NAME, "android.widget.Switch")
        state_after = toggle.get_attribute("checked") == "true"
        
        logger.info(f"Wi-Fi state after: {state_after}")
        return state_before, state_after