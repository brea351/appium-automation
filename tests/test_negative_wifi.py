import pytest
import allure
from pages.settings_page import SettingsPage
from utils.logger import get_logger
from utils.gestures import scroll_to_text
from selenium.common.exceptions import NoSuchElementException

logger = get_logger()


@allure.step("Validate scrolling to invalid element fails")
def test_scroll_to_invalid_element(driver):
    page = SettingsPage(driver)

    logger.info("Opening Network & Internet")
    page.open_network()

    logger.info("Trying to scroll to NON-EXISTENT element")

    with pytest.raises(NoSuchElementException):
        scroll_to_text(driver, "InvalidOption123")

    logger.info("Test passed: Invalid element not found as expected")