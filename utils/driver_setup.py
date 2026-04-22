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

    # 🚀 CI OPTIMIZATIONS: Giving the slow emulator more time to breathe
    # Total time to wait for the internal Appium server to start (60 seconds)
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", 60000)
    
    # Time to wait for the APK to install on a slow disk (90 seconds)
    options.set_capability("appium:uiautomator2ServerInstallTimeout", 90000)
    
    # Timeout for all ADB commands (sending clicks, finding elements)
    options.set_capability("appium:adbExecTimeout", 60000)
    
    # Suppress unnecessary waits for animations to finish
    options.set_capability("appium:waitForIdleTimeout", 0)

    # Ensure the app is actually brought to the foreground
    options.set_capability("appium:forceAppLaunch", True)

    # Connection to the Appium Server
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    
    # 🔹 Global Implicit Wait
    # This helps find_element commands wait a bit for the UI to render
    driver.implicitly_wait(10) 
    
    return driver