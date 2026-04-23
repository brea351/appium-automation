import pytest
import requests
from pages.settings_page import SettingsPage
from utils.logger import get_logger

logger = get_logger()



@pytest.mark.mobile
def test_api_ui_wifi_toggle(driver):
    page = SettingsPage(driver)

    # 🔹 STEP 1: Get API data (simulate backend)
    url = "https://jsonplaceholder.typicode.com/posts/1"
    response = requests.get(url)

    assert response.status_code == 200
    data = response.json()

    logger.info(f"API Data: {data}")

    # 🔹 Fake logic: if ID is 1 → Wi-Fi should be ON
    expected_state = "true" if data["id"] == 1 else "false"

    # 🔹 STEP 2: Navigate UI
    page.open_network()
    page.open_wifi()
    time.sleep(2)

    assert page.is_wifi_screen_open()

    # 🔹 STEP 3: Get UI state
    toggle = page.wait.until(
        lambda d: d.find_element(
            "-android uiautomator",
            'new UiSelector().className("android.widget.Switch")'
        )
    )

    actual_state = toggle.get_attribute("checked")

    logger.info(f"Expected (API): {expected_state}")
    logger.info(f"Actual (UI): {actual_state}")

    # 🔹 STEP 4: Validate API vs UI
    assert actual_state == expected_state