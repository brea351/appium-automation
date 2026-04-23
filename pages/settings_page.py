import time
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.logger import get_logger

logger = get_logger()


class SettingsPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    # ── Internal helpers ───────────────────────────────────────────────────

    def _adb_start_activity(self, action: str) -> bool:
        """
        Use ADB shell am start — bypasses the Appium Intent routing bug
        where mobile:startActivity silently falls back to the homepage.
        """
        try:
            # This is the equivalent of:
            # adb shell am start -a android.settings.WIFI_SETTINGS
            result = self.driver.execute_script(
                "mobile: shell",
                {
                    "command": "am",
                    "args": ["start", "-a", action],
                    "includeStderr": True,
                    "timeout": 10000,
                }
            )
            logger.info(f"ADB shell am start result: {result}")
            time.sleep(2.5)  # wait for activity to fully render
            return True
        except Exception as e:
            logger.error(f"ADB shell failed for action '{action}': {e}")
            return False

    def _current_package_and_activity(self) -> str:
        try:
            pkg = self.driver.current_package
            act = self.driver.current_activity
            return f"{pkg}/{act}"
        except Exception:
            return "unknown"

    def _dump_screen(self, label: str = ""):
        try:
            logger.error(f"[CURRENT SCREEN: {self._current_package_and_activity()}]")
            source = self.driver.page_source
            logger.error(f"[PAGE SOURCE DUMP — {label}]")
            for i in range(0, min(len(source), 10000), 3000):
                logger.error(source[i:i + 3000])
        except Exception as e:
            logger.error(f"Could not dump page source: {e}")

    # ── Page actions ───────────────────────────────────────────────────────

    @allure.step("Open Network & Internet settings")
    def open_network(self):
        """
        Navigate directly to Wi-Fi via ADB — skip Network entirely.
        open_network() is now just a pre-step that ensures we're in
        the right app; open_wifi() does the real navigation.
        """
        logger.info("Ensuring Settings app is in foreground")
        self._adb_start_activity("android.settings.SETTINGS")

        # Confirm we landed on the homepage
        try:
            self.wait.until(
                EC.presence_of_element_located((
                    AppiumBy.ID,
                    "com.android.settings:id/settings_homepage_container"
                ))
            )
            logger.info("Settings homepage confirmed")
        except TimeoutException:
            logger.warning("Homepage not detected — proceeding anyway")

    @allure.step("Open Wi-Fi settings")
    def open_wifi(self):
        """
        Three-strategy approach, escalating from most to least reliable.
        """
        logger.info(f"Screen before open_wifi: {self._current_package_and_activity()}")

        # ── Strategy 1: ADB am start with explicit component ──────────────
        # Targeting the component directly bypasses Intent routing issues
        logger.info("Strategy 1: ADB component launch")
        try:
            result = self.driver.execute_script(
                "mobile: shell",
                {
                    "command": "am",
                    "args": [
                        "start",
                        "-n", "com.android.settings/.wifi.WifiSettings",
                    ],
                    "includeStderr": True,
                    "timeout": 10000,
                }
            )
            logger.info(f"Component launch result: {result}")
            time.sleep(2.5)
            if self.is_wifi_screen_open():
                logger.info("Wi-Fi screen confirmed via component launch")
                return
        except Exception as e:
            logger.warning(f"Strategy 1 failed: {e}")

        # ── Strategy 2: ADB action Intent ─────────────────────────────────
        logger.info("Strategy 2: ADB WIFI_SETTINGS action")
        self._adb_start_activity("android.settings.WIFI_SETTINGS")
        if self.is_wifi_screen_open():
            logger.info("Wi-Fi screen confirmed via WIFI_SETTINGS intent")
            return

        # ── Strategy 3: Scroll the homepage RecyclerView and click ────────
        logger.info("Strategy 3: Scroll Settings homepage and click Wi-Fi entry")
        self._open_wifi_by_scrolling_homepage()

    def _open_wifi_by_scrolling_homepage(self):
        """
        The homepage is a RecyclerView. We scroll it using W3C Actions
        (finger swipe) rather than UiScrollable, since the page source
        showed scrollable=false on all containers — this is a rendering
        quirk where the RecyclerView handles its own scroll events.
        """
        screen_size = self.driver.get_window_size()
        width = screen_size["width"]
        height = screen_size["height"]

        start_x = width // 2
        start_y = int(height * 0.75)
        end_y   = int(height * 0.25)

        WIFI_LOCATORS = [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Wi-Fi")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Network & internet")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Wi-Fi")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Network")'),
        ]

        for attempt in range(5):  # scroll up to 5 times looking for the entry
            # Check if any Wi-Fi locator is visible right now
            for by, locator in WIFI_LOCATORS:
                try:
                    el = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((by, locator))
                    )
                    el.click()
                    logger.info(f"Clicked '{locator}' on scroll attempt {attempt + 1}")
                    time.sleep(1.5)

                    # If we clicked "Network & internet", we need one more click for Wi-Fi
                    if self.is_wifi_screen_open():
                        return
                    else:
                        # Might have landed on Network sub-menu — look for Wi-Fi there
                        try:
                            wifi_sub = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((
                                    AppiumBy.ANDROID_UIAUTOMATOR,
                                    'new UiSelector().text("Wi-Fi")'
                                ))
                            )
                            wifi_sub.click()
                            time.sleep(1.5)
                            if self.is_wifi_screen_open():
                                return
                        except Exception:
                            pass
                except Exception:
                    continue

            # Nothing found yet — perform a swipe scroll
            logger.info(f"Scrolling homepage (attempt {attempt + 1})")
            self.driver.execute_script("mobile: swipeGesture", {
                "left": start_x - 50, "top": start_y,
                "width": 100, "height": abs(start_y - end_y),
                "direction": "up",
                "percent": 0.75
            })
            time.sleep(0.5)

        # Everything failed — dump and raise
        self._dump_screen("all strategies exhausted")
        raise RuntimeError(
            "Cannot open Wi-Fi screen after 3 strategies and 5 scroll attempts. "
            "See page source dump in logs. "
            f"Last known screen: {self._current_package_and_activity()}"
        )

    @allure.step("Verify Wi-Fi screen is displayed")
    def is_wifi_screen_open(self) -> bool:
        logger.info("Checking if Wi-Fi screen is open")
        WIFI_ONLY_INDICATORS = [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Add network")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Wi-Fi preferences")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Saved networks")'),
            (AppiumBy.XPATH,
             '//android.widget.TextView[@text="Wi-Fi" and '
             '(contains(@resource-id,"toolbar") or contains(@resource-id,"action_bar") '
             'or contains(@resource-id,"title"))]'),
        ]
        try:
            WebDriverWait(self.driver, 8).until(
                EC.any_of(*[EC.visibility_of_element_located(l) for l in WIFI_ONLY_INDICATORS])
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