from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from utils.logger import get_logger

logger = get_logger()

def scroll_to_text(driver, text):
    """
    Scrolls until element with text is visible.
    If the screen is not scrollable, it falls back to a normal search.
    """
    try:
        logger.info(f"Scrolling to find text: {text}")
        return driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiScrollable(new UiSelector().scrollable(true))'
            f'.scrollIntoView(new UiSelector().textContains("{text}"))'
        )
    except Exception as e:
        logger.warning(f"Scrollable container not found or scroll failed, searching normally for '{text}'")
        # Fallback: If UI isn't scrollable, the element might already be on screen
        try:
            return driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")')
        except NoSuchElementException:
            logger.error(f"Element with text '{text}' not found after scroll attempt and fallback.")
            raise

def swipe_up(driver, duration=800):
    """
    Performs a standard swipe up gesture from bottom to top.
    """
    try:
        size = driver.get_window_size()
        
        # Define coordinates
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.8)  # 80% down (bottom)
        end_y = int(size["height"] * 0.2)    # 20% down (top)

        logger.info(f"Performing swipe up: ({start_x}, {start_y}) to ({start_x}, {end_y})")
        driver.swipe(start_x, start_y, start_x, end_y, duration)
        
    except Exception as e:
        logger.error(f"Swipe gesture failed: {e}")
        raise