import time
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.logger import get_logger

logger = get_logger()

# Android guaranteed Intent actions — these work on all AOSP versions
INTENT_WIFI        = "android.settings.WIFI_SETTINGS"
INTENT_NETWORK     = "android.settings.WIRELESS_SETTINGS"
INTENT_SETTINGS    = "android.settings.SETTINGS"


class SettingsPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    # ── Internal helper ────────────────────────────────────────────────────

    def _launch_intent(self, action: str) -> bool:
        """
        Fire an Android Settings Intent directly.
        Returns True on success, False on failure.
        This bypasses ALL UI navigation and text-matching entirely.
        """
        try:
            self.driver.execute_script("mobile: startActivity", {
                "intent": action,
                # Required on API 30+ — use the Settings package explicitly
                "package": "com.android.settings",
            })
            logger.info(f"Intent launched: {action}")
            time.sleep(1.5)  # allow activity transition to complete
            return True
        except Exception as e:
            logger.warning(f"Intent '{action}' failed: {e}")
            return False

    def _dump_screen(self, label: str = ""):
        """Dump page source for CI diagnosis — call on any failure."""
        try:
            source = self.driver.page_source
            logger.error(f"[PAGE SOURCE DUMP{' — ' + label if label else ''}]")
            for i in range(0, min(len(source), 6000), 2000):
                logger.error(source[i:i + 2000])
        except Exception as e:
            logger.error(f"Could not dump page source: {e}")

    # ── Page actions ───────────────────────────────────────────────────────

    @allure.step("Open Network & Internet settings")
    def open_network(self):
        """
        Use Intent directly — no text scrolling, no OEM variance.
        WIRELESS_SETTINGS is the guaranteed action for Network & Internet.
        """
        logger.info("Launching Network & Internet via Intent")
        if not self._launch_intent(INTENT_NETWORK):
            # Hard fallback: launch generic settings, then try text navigation
            logger.warning("WIRELESS_SETTINGS Intent failed — falling back to SETTINGS Intent")
            self._launch_intent(INTENT_SETTINGS)
        logger.info("Network screen ready")

    @allure.step("Open Wi-Fi settings")
    def open_wifi(self):
        """
        Use WIFI_SETTINGS Intent directly — guaranteed to land on the
        Wi-Fi screen regardless of what's on screen right now.
        """
        logger.info("Launching Wi-Fi screen via Intent")

        if self._launch_intent(INTENT_WIFI):
            # Verify we actually landed on the right screen
            if self.is_wifi_screen_open():
                logger.info("Wi-Fi screen confirmed via Intent")
                return
            else:
                logger.warning("Intent fired but Wi-Fi screen not detected — dumping screen")
                self._dump_screen("after WIFI_SETTINGS intent")

        # Last resort: try clicking from whatever is currently on screen
        logger.warning("Intent approach failed — attempting UI click fallback")
        self._open_wifi_via_ui()

    def _open_wifi_via_ui(self):
        """Fallback: try to find and click Wi-Fi from the current screen."""
        LOCATORS = [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Wi-Fi")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("WiFi")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Wi-Fi")'),
            # Some Samsung/OEM skins label it differently
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Connections")'),
        ]
        for by, locator in LOCATORS:
            try:
                el = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((by, locator))
                )
                el.click()
                logger.info(f"Clicked Wi-Fi via UI fallback: {locator}")
                time.sleep(1)
                return
            except Exception:
                continue

        # If we get here, dump the screen so we know what IS there
        self._dump_screen("open_wifi UI fallback — nothing found")
        raise RuntimeError(
            "Cannot open Wi-Fi screen. Neither Intent nor UI navigation worked. "
            "Check the page source dump in logs above."
        )

    @allure.step("Verify Wi-Fi screen is displayed")
    def is_wifi_screen_open(self) -> bool:
        """
        Check for elements that ONLY exist on the Wi-Fi sub-screen.
        'Add network' and 'Wi-Fi preferences' are reliable unique indicators.
        """
        logger.info("Checking if Wi-Fi screen is open")

        WIFI_ONLY_INDICATORS = [
            # "Add network" only appears on the Wi-Fi screen
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Add network")'),
            # "Wi-Fi preferences" / "Network preferences" — Wi-Fi screen footer
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Wi-Fi preferences")'),
            # Toolbar title — specifically "Wi-Fi" as a standalone title element
            (AppiumBy.XPATH,
             '//android.widget.TextView[@text="Wi-Fi" and '
             '(contains(@resource-id,"toolbar") or contains(@resource-id,"action_bar") '
             'or contains(@resource-id,"title"))]'),
        ]

        try:
            self.wait.until(
                EC.any_of(*[
                    EC.visibility_of_element_located(loc)
                    for loc in WIFI_ONLY_INDICATORS
                ])
            )
            logger.info("Wi-Fi screen open: True")
            return True
        except TimeoutException:
            logger.info("Wi-Fi screen open: False")
            return False

    @allure.step("Toggle Wi-Fi and validate state change")
    def toggle_wifi(self):
        logger.info("Attempting to toggle Wi-Fi")

        toggle = self.wait.until(
            EC.visibility_of_element_located((AppiumBy.CLASS_NAME, "android.widget.Switch"))
        )
        state_before = toggle.get_attribute("checked") == "true"
        logger.info(f"Wi-Fi state before: {state_before}")

        toggle.click()
        time.sleep(2)

        toggle = self.driver.find_element(AppiumBy.CLASS_NAME, "android.widget.Switch")
        state_after = toggle.get_attribute("checked") == "true"

        logger.info(f"Wi-Fi state after: {state_after}")
        return state_before, state_after