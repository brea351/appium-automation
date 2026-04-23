import pytest
import requests
import allure


@allure.feature("API Testing")
@allure.story("Wi-Fi API Validation")
@pytest.mark.api
def test_api_wifi_status():
    """
    Simple API test (mock/public API)
    Replace this later with real backend API
    """

    url = "https://jsonplaceholder.typicode.com/posts/1"

    response = requests.get(url)

    # Assertions
    assert response.status_code == 200
    assert "userId" in response.json()

    # Allure attach
    allure.attach(
        str(response.json()),
        name="API Response",
        attachment_type=allure.attachment_type.JSON
    )