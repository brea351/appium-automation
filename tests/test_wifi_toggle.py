import pytest
from utils.driver_setup import create_driver
from pages.settings_page import SettingsPage
from utils.logger import get_logger

logger = get_logger()

@pytest.mark.mobile 
def test_wifi_toggle(driver):
    page = SettingsPage(driver)

    logger.info("Opening Network & Internet")
    page.open_network()

    logger.info("Opening Wi-Fi")
    page.open_wifi()

    logger.info("Validating Wi-Fi screen")
    assert page.is_wifi_screen_open()

    logger.info("Toggling Wi-Fi")
    before, after = page.toggle_wifi()

    logger.info(f"State before: {before}, State after: {after}")
    assert before != after