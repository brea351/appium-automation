from appium import webdriver
from appium.options.android import UiAutomator2Options

def create_driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "emulator-5554"
    options.automation_name = "UiAutomator2"
    options.app_package = "com.android.settings"
    options.app_activity = ".Settings"
    options.no_reset = True

    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    return driver