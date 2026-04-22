import time
import allure
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
from utils.gestures import scroll_to_text

logger = get_logger()

class SettingsPage:
    def __init__(self, driver):
        self.driver = driver
        # Increased timeout slightly for slow emulator rendering
        self.wait = WebDriverWait(driver, 20)

    @allure.step("Open Network & Internet settings")
    def open_network(self):
        logger.info("Attempting to open Network & Internet")
        
        try:
            # 🔹 Primary: Scroll to find "Network" using regex (case-insensitive)
            network = scroll_to_text(self.driver, "Network")
            network.click()
        except Exception as e:
            logger.warning(f"Could not find 'Network' by text, trying 'Connections' or ID fallback. Error: {e}")
            try:
                # 🔹 Fallback 1: Many emulators use "Connections"
                network = scroll_to_text(self.driver, "Connections")
                network.click()
            except Exception:
                # 🔹 Fallback 2: Direct click on the first dashboard tile by ID
                network = self.driver.find_element(AppiumBy.ID, "android:id/title")
                network.click()

        logger.info("Opened Network & Internet")

    @allure.step("Open Wi-Fi settings")
    def open_wifi(self):
        logger.info("Locating Wi-Fi entry")
        
        # 🔹 FIX: First try to find it without scrolling (since the sub-menu is usually short)
        try:
            # Use a wait to ensure the sub-menu has loaded
            wifi = self.wait.until(
                EC.element_to_be_clickable((
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().textMatches("(?i)Wi.*Fi")'
                ))
            )
            wifi.click()
            logger.info("Found and clicked Wi-Fi")
        except Exception:
            # 🔹 Fallback: Only scroll if it's really not there
            logger.warning("Wi-Fi not immediately visible, attempting scroll fallback...")
            wifi = scroll_to_text(self.driver, "Wi-Fi")
            wifi.click()
            
        logger.info("Opened Wi-Fi")

    @allure.step("Verify Wi-Fi screen is displayed")
    def is_wifi_screen_open(self):
        logger.info("Checking if Wi-Fi screen is open")
        try:
            self.wait.until(
                EC.visibility_of_element_located((
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().textMatches("(?i)Wi-Fi")'
                ))
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
            EC.visibility_of_element_located((
                AppiumBy.CLASS_NAME, "android.widget.Switch"
            ))
        )

        state_before = toggle.get_attribute("checked") == "true"
        logger.info(f"Wi-Fi state before: {state_before}")

        toggle.click()
        
        # 🔹 Wait for the UI thread to update the switch state
        time.sleep(2) 

        # Refresh the element reference to get the new state
        toggle = self.driver.find_element(AppiumBy.CLASS_NAME, "android.widget.Switch")
        state_after = toggle.get_attribute("checked") == "true"
        
        logger.info(f"Wi-Fi state after: {state_after}")
        return state_before, state_after