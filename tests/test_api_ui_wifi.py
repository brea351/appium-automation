import pytest
import requests
import allure
from pages.settings_page import SettingsPage
from utils.logger import get_logger

logger = get_logger()


@allure.title("API + UI Validation: Wi-Fi Toggle")
@allure.description("Validate UI toggle behavior with API response")
def test_api_ui_wifi_toggle(driver):

    page = SettingsPage(driver)

    # 🔥 STEP 1: Call API (simulate backend state)
    logger.info("Calling API to get expected state")

    response = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    assert response.status_code == 200

    api_data = response.json()
    expected_state = str(api_data["completed"]).lower()

    logger.info(f"API returned expected state: {expected_state}")
    allure.attach(expected_state, name="API Expected State", attachment_type=allure.attachment_type.TEXT)

    # 🔥 STEP 2: UI actions
    logger.info("Opening Network & Internet")
    page.open_network()

    logger.info("Opening Wi-Fi")
    page.open_wifi()

    logger.info("Validating Wi-Fi screen")
    assert page.is_wifi_screen_open()

    # 🔥 STEP 3: Get UI state
    before, after = page.toggle_wifi()

    logger.info(f"UI state before: {before}")
    logger.info(f"UI state after: {after}")

    allure.attach(before, name="UI Before", attachment_type=allure.attachment_type.TEXT)
    allure.attach(after, name="UI After", attachment_type=allure.attachment_type.TEXT)

    # 🔥 STEP 4: Validate logic (example validation)
    assert before != after