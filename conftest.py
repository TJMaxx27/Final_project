import logging
from functools import wraps
import allure
import pytest
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FireFoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from jsonschema import validate, ValidationError


logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def allure_attach_screenshot_on_failed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            allure.attach(
                self.browser.get_screenshot_as_png(),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            raise e

    return wrapper


# API тесты


@pytest.fixture(scope="session")
def project_schema():
    with open("tests/api/project_schema.json", "r") as schema_file:
        schema = json.load(schema_file)
    return schema


@pytest.fixture(scope="session")
def api_schemas(project_schema):
    return project_schema


@pytest.fixture()
def validate_project_response(api_schemas):
    def _validate(response_data, schema_name):
        schema = api_schemas.get(schema_name)
        if not schema:
            raise ValueError(f"Schema '{schema_name}' not found")

        try:
            validate(instance=response_data, schema=schema)
            print(f"Response data is valid for schema '{schema_name}'.")
        except ValidationError as e:
            print(f"Response data is invalid: {e}")
            raise

    return _validate


@pytest.fixture(scope="session")
def project_id_store():
    return {"project_id": None}


# UI Блок


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--executor", action="store", default="local")
    parser.addoption("--vnc", action="store_true")
    parser.addoption("--logs", action="store_true")
    parser.addoption("--video", action="store_true")
    parser.addoption("--bv", action="store", default="latest")


@pytest.fixture()
def browser(request):
    browser = request.config.getoption("--browser")
    executor = request.config.getoption("--executor")
    vnc = request.config.getoption("--vnc")
    version = request.config.getoption("--bv")
    logs = request.config.getoption("--logs")
    video = request.config.getoption("--video")

    options = None
    driver = None

    if executor == "local":
        if browser == "chrome":
            options = ChromeOptions()
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        elif browser == "firefox":
            options = FireFoxOptions()
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
    else:
        executor_url = f"http://{executor}:4444/wd/hub"
        if browser == "chrome":
            options = ChromeOptions()
        elif browser == "firefox":
            options = FireFoxOptions()

        capabilities = {
            "browserName": browser,
            "browserVersion": version if version != "latest" else "",
            "selenoid:options": {
                "enableVNC": vnc,
                "name": request.node.name,
                "screenResolution": "1920x1080x24",
                "enableVideo": video,
                "enableLog": logs,
            },
        }

        for k, v in capabilities.items():
            if v:
                options.set_capability(k, v)

        driver = webdriver.Remote(command_executor=executor_url, options=options)

    driver.maximize_window()
    yield driver
    if driver is not None:
        driver.quit()
