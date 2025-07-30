import logging
import os
import platform

import pytest
import selenium.common.exceptions

from selenium_wrapper import SeleniumBrowser
from selenium_wrapper.SeleniumBrowser import BrowserSwitchTabActionArgs
from selenium_wrapper.SeleniumBrowser import SeleniumBrowserActions


@pytest.fixture(scope="session")
def firefox_path(request):
    return request.config.getoption("--firefox_path")


@pytest.fixture(scope="session")
def browser():
    return SeleniumBrowser()


@pytest.fixture(scope="session")
def browser_with_chrome():
    return SeleniumBrowser(browser="chrome")


@pytest.fixture(scope="session")
def browser_with_firefox(firefox_path):
    if firefox_path is None:
        match os.name:
            case "nt":
                firefox_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
            case "posix":
                firefox_path = "/usr/bin/firefox"
            case _:
                pytest.skip(
                    "Firefox path not specified and cannot be determined for this OS"
                )

    if not os.path.isfile(firefox_path):
        pytest.skip("Firefox not found at path: " + firefox_path)

    return SeleniumBrowser(browser="firefox", browser_path=firefox_path)


def test_browser(browser):
    assert browser is not None


def test_chrome_browser(browser_with_chrome):
    assert browser_with_chrome is not None
    browser_with_chrome.close()


def test_firefox_browser(browser_with_firefox):
    assert browser_with_firefox is not None
    browser_with_firefox.close()


def test_browser_can_navigate_to_url_from_json(browser, caplog):
    caplog.set_level(logging.DEBUG, logger="SeleniumBrowser")
    json: str = """
    [
        {
            "target": "browser",
            "action": "go",
            "args": {
                "url": "https://www.google.com"
            }
        },
        {
            "target": "element",
            "action": "type",
            "args": {
                "locate_by": "xpath",
                "locate_value": "//*[local-name() = 'input' or local-name() = 'textarea'][@title='Search']",
                "text": "Hello World",
                "wait": true
            }
        },
        {
            "target": "element",
            "action": "click",
            "args": {
                "locate_value": "//input[@value='Google Search']"
            }
        }
    ]
    """
    browser.run_json(json)
    assert browser.title == "Hello World - Google Search"


def test_browser_can_navigate_to_url_from_yaml(browser, caplog):
    caplog.set_level(logging.DEBUG, logger="SeleniumBrowser")
    yaml_str: str = """
    - target: browser
      action: go
      args:
        url: https://www.google.com
    - target: element
      action: type
      args:
        locate_by: xpath
        locate_value: //*[local-name() = 'input' or local-name() = 'textarea'][@title='Search']
        text: Hello World
        wait: true
    - target: element
      action: click
      args:
        locate_value: //input[@value='Google Search']
    """
    browser.run_yaml(yaml_str)
    assert browser.title == "Hello World - Google Search"


def test_browser_can_delete_element(browser, caplog):
    caplog.set_level(logging.DEBUG, logger="SeleniumBrowser")
    yaml_str: str = """
    - target: browser
      action: go
      args:
        url: https://www.google.com
    - target: element
      action: delete
      args:
        locate_by: xpath
        locate_value: //*[local-name() = 'input' or local-name() = 'textarea'][@title='Search']
        wait: true
    """
    browser.run_yaml(yaml_str)
    with pytest.raises(selenium.common.exceptions.StaleElementReferenceException):
        browser.find_element("xpath", "//input[@title='Search']")


def test_browser_can_insert_element(browser, caplog):
    caplog.set_level(logging.DEBUG, logger="SeleniumBrowser")
    yaml_str: str = """
    - target: browser
      action: go
      args:
        url: https://www.google.com
    - target: element
      action: insert
      args:
        locate_by: xpath
        locate_value: //span[contains(text(), 'climate')]
        wait: true
        html: Testing
    """
    browser.run_yaml(yaml_str)
    assert browser.last_element.text == "Testing"


def test_browser_can_insert_trusted_element(browser, caplog):
    caplog.set_level(logging.DEBUG, logger="SeleniumBrowser")
    yaml_str: str = """
    - target: browser
      action: go
      args:
        url: https://www.google.com
    - target: element
      action: insert trusted
      args:
        locate_by: xpath
        locate_value: //span[contains(text(), 'Carbon')]
        wait: true
        html: Testing
    """
    browser.run_yaml(yaml_str)
    assert "Testing" in browser.last_element.text


def test_browser_can_modify_element_attribute(browser, caplog):
    caplog.set_level(logging.DEBUG, logger="SeleniumBrowser")
    yaml_str: str = """
    - target: browser
      action: go
      args:
        url: https://www.google.com
    - target: element
      action: set attribute
      args:
        locate_by: xpath
        locate_value: //span[contains(text(), 'climate')]
        wait: true
        attribute: style
        value: "font-size: 24px;"
    """
    browser.run_yaml(yaml_str)
    assert browser.last_element.get_attribute("style") == "font-size: 24px;"


def test_browser_can_open_new_window(browser, caplog):
    caplog.set_level(logging.DEBUG, logger="SeleniumBrowser")
    yaml_str: str = """
    - target: browser
      action: new tab
    - target: browser
      action: switch tab
      args:
        tab: next
    - target: browser
      action: go
      args:
        url: https://www.bing.com
    """
    browser.run_yaml(yaml_str)
    assert browser.title == "Bing"
    browser.close_window()


def test_browser_can_find_tab_by_title(browser, caplog):
    caplog.set_level(logging.DEBUG, logger="SeleniumBrowser")
    yaml_str: str = """
    - target: browser
      action: go
      args:
        url: https://www.google.com
    - target: browser
      action: new tab
    - target: browser
      action: switch tab
      args:
        tab: next
    - target: browser
      action: go
      args:
        url: https://www.bing.com
    """
    browser.run_yaml(yaml_str)
    assert browser.title == "Bing"
    browser.act_on_browser(
        SeleniumBrowserActions.SWITCH_TAB, args=BrowserSwitchTabActionArgs(tab="next")
    )
    assert browser.title == "Google"
    browser.close_window()


def test_browser_can_find_tab_by_url(browser, caplog):
    caplog.set_level(logging.DEBUG, logger="SeleniumBrowser")
    yaml_str: str = """
    - target: browser
      action: go
      args:
        url: https://www.google.com
    - target: browser
      action: new tab
    - target: browser
      action: switch tab
      args:
        tab: next
    - target: browser
      action: go
      args:
        url: https://www.bing.com
    """
    browser.run_yaml(yaml_str)
    assert browser.title == "Bing"
    browser.act_on_browser(
        SeleniumBrowserActions.SWITCH_TAB,
        args=BrowserSwitchTabActionArgs(tab="https://www.google.com"),
    )
    assert browser.title == "Google"
    browser.close_window()
