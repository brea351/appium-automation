from appium.webdriver.common.appiumby import AppiumBy


def scroll_to_text(driver, text):
    """
    Scrolls until element with text is visible
    """
    return driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR,
        f'new UiScrollable(new UiSelector().scrollable(true))'
        f'.scrollIntoView(new UiSelector().textContains("{text}"))'
    )


def swipe_up(driver):
    """
    Simple swipe up gesture
    """
    size = driver.get_window_size()

    start_x = size["width"] // 2
    start_y = int(size["height"] * 0.8)
    end_y = int(size["height"] * 0.2)

    driver.swipe(start_x, start_y, start_x, end_y, 800)