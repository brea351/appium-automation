import pytest
import allure
from utils.driver_setup import create_driver


@pytest.fixture
def driver():
    driver = create_driver()
    yield driver
    driver.quit()


# 🔥 Screenshot on failure hook
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")

        if driver:
            screenshot = driver.get_screenshot_as_png()

            allure.attach(
                screenshot,
                name="Failure Screenshot",
                attachment_type=allure.attachment_type.PNG
            )