from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
import allure
from utils.gestures import scroll_to_text

logger = get_logger()


class SettingsPage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # 🔹 Open Network & Internet
    @allure.step("Open Network & Internet settings")
    def open_network(self):
        logger.info("Attempting to open Network & Internet")

        network = self.wait.until(
            EC.presence_of_element_located((
                "-android uiautomator",
                'new UiSelector().textContains("Network")'
            ))
        )
        network.click()

        logger.info("Opened Network & Internet")

    # 🔹 Open Wi-Fi (UPDATED WITH SCROLL)
    @allure.step("Open Wi-Fi settings")
    def open_wifi(self):
        logger.info("Scrolling to Wi-Fi")

        wifi = scroll_to_text(self.driver, "Wi")

        wifi.click()

        logger.info("Opened Wi-Fi")

    # 🔹 Verify Wi-Fi screen
    @allure.step("Verify Wi-Fi screen is displayed")
    def is_wifi_screen_open(self):
        logger.info("Checking if Wi-Fi screen is open")

        wifi_title = self.wait.until(
            EC.presence_of_element_located((
                "-android uiautomator",
                'new UiSelector().textContains("Wi")'
            ))
        )

        result = wifi_title is not None

        logger.info(f"Wi-Fi screen open: {result}")
        allure.attach(str(result), name="Wi-Fi Screen Status", attachment_type=allure.attachment_type.TEXT)

        return result

    # 🔹 Toggle Wi-Fi
    @allure.step("Toggle Wi-Fi and validate state change")
    def toggle_wifi(self):
        logger.info("Attempting to toggle Wi-Fi")

        toggle = self.wait.until(
            EC.presence_of_element_located((
                "-android uiautomator",
                'new UiSelector().className("android.widget.Switch")'
            ))
        )

        state_before = toggle.get_attribute("checked")
        logger.info(f"Wi-Fi state before: {state_before}")

        allure.attach(state_before, name="State Before", attachment_type=allure.attachment_type.TEXT)

        toggle.click()
        logger.info("Clicked Wi-Fi toggle")

        # Refresh element
        toggle = self.driver.find_element(
            "-android uiautomator",
            'new UiSelector().className("android.widget.Switch")'
        )

        state_after = toggle.get_attribute("checked")
        logger.info(f"Wi-Fi state after: {state_after}")

        allure.attach(state_after, name="State After", attachment_type=allure.attachment_type.TEXT)

        return state_before, state_after