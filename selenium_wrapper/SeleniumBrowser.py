import dataclasses
import logging
import os
import time
from enum import StrEnum
from enum import auto
from pathlib import Path
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union
from typing import cast

import jsons
import selenium
import selenium.common.exceptions
import yaml
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver import ChromeOptions
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import IeOptions
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.events import AbstractEventListener
from selenium.webdriver.support.events import EventFiringWebDriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

Locator = Tuple[By, str]


class CaseInsensitiveSpaceStrEnum(StrEnum):
    @classmethod
    def has_member(cls, value: str) -> bool:
        """Check if the value is a member of the enumeration."""
        return (
            value.upper() in cls.__members__
            or value.upper().replace(" ", "_") in cls.__members__
        )

    @classmethod
    def _missing_(cls, value: str) -> "CaseInsensitiveSpaceStrEnum":
        """Allow the user to specify the action using the name of the action, or the value of the action."""
        if cls.has_member(value):
            return cls.__members__[value.upper().replace(" ", "_")]


class SeleniumTargets(StrEnum):
    """An enumeration describing the targets available to the Browser object."""

    # The browser itself
    BROWSER = auto()
    # An element on the page
    ELEMENT = auto()


class SeleniumBrowserActions(CaseInsensitiveSpaceStrEnum):
    """An enumeration describing actions available to the Browser object."""

    # Tell the browser to go to a URL
    GO = auto()

    # Tell the browser to open a new tab
    NEW_TAB = auto()

    # Tell the browser to switch to a tab
    SWITCH_TAB = auto()

    # Tell the browser to pause for the specified duration
    WAIT = auto()


class SeleniumElementActions(CaseInsensitiveSpaceStrEnum):
    """An enumeration describing actions available to the Element object."""

    # Tell the browser to change an element
    CHANGE = auto()
    # Tell the browser to click on an element
    CLICK = auto()
    # Tell the browser to remove the element from the page
    DELETE = auto()
    # Tell the browser to insert an element into the page as a child of the specified element
    INSERT = auto()
    # Tell the browser to insert an element into the page using a TrustedType
    INSERT_TRUSTED = auto()
    # Tell the browser to hover over an element (typically for things like dropdowns)
    MOVE_TO = auto()
    # Tell the browser to set an attribute on an element
    SET_ATTRIBUTE = auto()
    # Tell the browser to type into an element
    TYPE = auto()
    # Tell the browser to wait for an element (typically wait for it to appear)
    WAIT = auto()


@dataclasses.dataclass
class ElementActionArgs:
    element: Optional[WebElement] = None
    locate_by: Optional[By | str] = None
    locate_value: Optional[str] = None
    wait: Optional[bool] = None
    wait_for: Optional[str] = None
    duration: Optional[int] = None
    inject: Optional[bool] = None


@dataclasses.dataclass
class ElementChangeActionArgs(ElementActionArgs):
    value: str = ""


@dataclasses.dataclass
class ElementInsertActionArgs(ElementActionArgs):
    html: str = ""


@dataclasses.dataclass
class ElementSetAttributeActionArgs(ElementActionArgs):
    attribute: str = ""
    value: str = ""


@dataclasses.dataclass
class ElementTypeActionArgs(ElementActionArgs):
    text: str = ""


@dataclasses.dataclass
class ElementWaitActionArgs(ElementActionArgs):
    pass


@dataclasses.dataclass
class BrowserActionArgs:
    pass


@dataclasses.dataclass
class BrowserGoActionArgs(BrowserActionArgs):
    url: str


@dataclasses.dataclass
class BrowserSwitchTabActionArgs(BrowserActionArgs):
    tab: str


@dataclasses.dataclass
class BrowserWaitActionArgs(BrowserActionArgs):
    duration: int


# A convenience type containing the union of all possible action argument classes
ActionArgs = Union[
    BrowserGoActionArgs,
    BrowserSwitchTabActionArgs,
    BrowserWaitActionArgs,
    ElementChangeActionArgs,
    ElementInsertActionArgs,
    ElementSetAttributeActionArgs,
    ElementWaitActionArgs,
    ElementTypeActionArgs,
    BrowserActionArgs,
    ElementActionArgs,
]

ActionTypes = Union[
    SeleniumBrowserActions,
    SeleniumElementActions,
]


@dataclasses.dataclass
class SeleniumAction:
    target: SeleniumTargets
    action: ActionTypes
    args: Optional[ActionArgs]

    def __post_init__(self):
        """Convert the args dictionary into the appropriate ActionArgs class, mainly necessary for the YAML parser."""
        if isinstance(self.action, str):
            if SeleniumBrowserActions.has_member(self.action):
                self.action = SeleniumBrowserActions(self.action)
            elif SeleniumElementActions.has_member(self.action):
                self.action = SeleniumElementActions(self.action)
            else:
                raise ValueError(f"Unknown SeleniumAction: {self.action}")

        if isinstance(self.args, dict):
            action_args: ActionArgs = ActionNameToArgumentClass[self.action](**self.args)  # type: ignore
            self.args = action_args


# A mapping of actions to their associated argument classes
ActionNameToArgumentClass = {
    SeleniumBrowserActions.GO: BrowserGoActionArgs,
    SeleniumBrowserActions.NEW_TAB: BrowserActionArgs,
    SeleniumBrowserActions.SWITCH_TAB: BrowserSwitchTabActionArgs,
    SeleniumBrowserActions.WAIT: BrowserWaitActionArgs,
    SeleniumElementActions.MOVE_TO: ElementActionArgs,
    SeleniumElementActions.CHANGE: ElementChangeActionArgs,
    SeleniumElementActions.CLICK: ElementActionArgs,
    SeleniumElementActions.DELETE: ElementActionArgs,
    SeleniumElementActions.INSERT: ElementInsertActionArgs,
    SeleniumElementActions.INSERT_TRUSTED: ElementInsertActionArgs,
    SeleniumElementActions.SET_ATTRIBUTE: ElementSetAttributeActionArgs,
    SeleniumElementActions.TYPE: ElementTypeActionArgs,
    SeleniumElementActions.WAIT: ElementWaitActionArgs,
}


class ExpectedConditions(CaseInsensitiveSpaceStrEnum):
    TITLE_IS = auto()
    TITLE_CONTAINS = auto()
    PRESENCE_OF_ELEMENT_LOCATED = auto()
    VISIBILITY_OF_ELEMENT_LOCATED = auto()
    VISIBILITY_OF = auto()
    PRESENCE_OF_ALL_ELEMENTS_LOCATED = auto()
    TEXT_TO_BE_PRESENT_IN_ELEMENT = auto()
    TEXT_TO_BE_PRESENT_IN_ELEMENT_VALUE = auto()
    FRAME_TO_BE_AVAILABLE_AND_SWITCH_TO_IT = auto()
    INVISIBILITY_OF_ELEMENT_LOCATED = auto()
    ELEMENT_TO_BE_CLICKABLE = auto()
    STALENESS_OF = auto()
    ELEMENT_TO_BE_SELECTED = auto()
    ELEMENT_LOCATED_TO_BE_SELECTED = auto()
    ELEMENT_SELECTION_STATE_TO_BE = auto()
    ELEMENT_LOCATED_SELECTION_STATE_TO_BE = auto()
    ALERT_IS_PRESENT = auto()
    URL_MATCHES = auto()
    URL_CONTAINS = auto()
    URL_CHANGES = auto()
    NEW_WINDOW_IS_OPENED = auto()
    NUMBER_OF_WINDOWS_TO_BE = auto()
    VISIBILITY_OF_ANY_ELEMENTS_LOCATED = auto()
    VISIBILITY_OF_ALL_ELEMENTS_LOCATED = auto()


ExpectedConditionsNameToFunction = {
    ExpectedConditions.TITLE_IS: expected_conditions.title_is,
    ExpectedConditions.TITLE_CONTAINS: expected_conditions.title_contains,
    ExpectedConditions.PRESENCE_OF_ELEMENT_LOCATED: expected_conditions.presence_of_element_located,
    ExpectedConditions.VISIBILITY_OF_ELEMENT_LOCATED: expected_conditions.visibility_of_element_located,
    ExpectedConditions.VISIBILITY_OF: expected_conditions.visibility_of,
    ExpectedConditions.PRESENCE_OF_ALL_ELEMENTS_LOCATED: expected_conditions.presence_of_all_elements_located,
    ExpectedConditions.TEXT_TO_BE_PRESENT_IN_ELEMENT: expected_conditions.text_to_be_present_in_element,
    ExpectedConditions.TEXT_TO_BE_PRESENT_IN_ELEMENT_VALUE: expected_conditions.text_to_be_present_in_element_value,
    ExpectedConditions.FRAME_TO_BE_AVAILABLE_AND_SWITCH_TO_IT: expected_conditions.frame_to_be_available_and_switch_to_it,
    ExpectedConditions.INVISIBILITY_OF_ELEMENT_LOCATED: expected_conditions.invisibility_of_element_located,
    ExpectedConditions.ELEMENT_TO_BE_CLICKABLE: expected_conditions.element_to_be_clickable,
    ExpectedConditions.STALENESS_OF: expected_conditions.staleness_of,
    ExpectedConditions.ELEMENT_TO_BE_SELECTED: expected_conditions.element_to_be_selected,
    ExpectedConditions.ELEMENT_LOCATED_TO_BE_SELECTED: expected_conditions.element_located_to_be_selected,
    ExpectedConditions.ELEMENT_SELECTION_STATE_TO_BE: expected_conditions.element_selection_state_to_be,
    ExpectedConditions.ELEMENT_LOCATED_SELECTION_STATE_TO_BE: expected_conditions.element_located_selection_state_to_be,
    ExpectedConditions.ALERT_IS_PRESENT: expected_conditions.alert_is_present,
    ExpectedConditions.URL_MATCHES: expected_conditions.url_matches,
    ExpectedConditions.URL_CONTAINS: expected_conditions.url_contains,
    ExpectedConditions.URL_CHANGES: expected_conditions.url_changes,
    ExpectedConditions.NEW_WINDOW_IS_OPENED: expected_conditions.new_window_is_opened,
    ExpectedConditions.NUMBER_OF_WINDOWS_TO_BE: expected_conditions.number_of_windows_to_be,
    ExpectedConditions.VISIBILITY_OF_ANY_ELEMENTS_LOCATED: expected_conditions.visibility_of_any_elements_located,
    ExpectedConditions.VISIBILITY_OF_ALL_ELEMENTS_LOCATED: expected_conditions.visibility_of_all_elements_located,
}


def is_docker() -> bool:
    """Determine if the current environment is running in a Docker container."""
    cgroup: Path = Path("/proc/self/cgroup")
    return (
        Path("/.dockerenv").is_file()
        or cgroup.is_file()
        and "docker" in cgroup.read_text()
    )


class SeleniumEventListener(AbstractEventListener):
    def after_change_value_of(self, element, driver) -> None:
        print(f"Changed value of element {element}")

    def after_click(self, element, driver) -> None:
        print(f"Clicked element {element}")

    def after_close(self, driver) -> None:
        print("Closed browser")

    def after_execute_script(self, script, driver) -> None:
        print(f"Executed script {script}")

    def after_find(self, by, value, driver) -> None:
        print(f"Found element {by} {value}")

    def after_navigate_back(self, driver) -> None:
        print("Navigated back")

    def after_navigate_forward(self, driver) -> None:
        print("Navigated forward")

    def after_navigate_to(self, url, driver) -> None:
        print(f"Navigated to {url}")

    def after_quit(self, driver) -> None:
        print("Quit browser")

    def after_switch_to_window(self, window_name, driver) -> None:
        print(f"Switched to window {window_name}")

    def before_change_value_of(self, element, driver) -> None:
        print(f"Before changing value of element {element}")

    def before_click(self, element, driver) -> None:
        print(f"Before clicking element {element}")

    def before_close(self, driver) -> None:
        print("Before closing browser")

    def before_execute_script(self, script, driver) -> None:
        print(f"Before executing script {script}")

    def before_find(self, by, value, driver) -> None:
        print(f"Before finding element {by} {value}")

    def before_navigate_back(self, driver) -> None:
        print("Before navigating back")

    def before_navigate_forward(self, driver) -> None:
        print("Before navigating forward")

    def before_navigate_to(self, url, driver) -> None:
        print(f"Before navigating to {url}")

    def before_quit(self, driver) -> None:
        print("Before quitting browser")

    def before_switch_to_window(self, window_name, driver) -> None:
        print(f"Before switching to window {window_name}")

    def on_exception(self, exception, driver) -> None:
        print(f"Exception {exception} occurred")


class SeleniumBrowser:
    """An instance of a Selenium WebDriver with associated options and convenience methods.

    Attributes:

    """

    browser: Optional[str] = None
    debug: bool = True
    default_wait: int = 10
    download_path: Optional[Path] = None
    driver: WebDriver | EventFiringWebDriver
    ignore_extensions: List[str] = ["crdownload", "tmp", "part"]
    last_element: Optional[WebElement] = None
    last_locator: Optional[Locator] = None
    last_method: Optional[By | str] = None
    last_window: Optional[str] = None
    listener: Optional[SeleniumEventListener] = None
    logger: logging.Logger = logging.getLogger("SeleniumBrowser")
    pause_on_exception: Optional[int] = 10

    def __init__(
        self,
        browser: Optional[str] = "chrome",
        browser_path: Optional[str] = None,
        download_path: Optional[Path] = None,
    ):
        """Initialize the SeleniumBrowser."""
        args: dict = {}
        driver_class: Type[WebDriver]
        options: ChromeOptions | FirefoxOptions | IeOptions | None = None

        if browser is not None:
            self.browser = browser.lower()

        match self.browser:
            case "chrome":
                driver_class = webdriver.Chrome
            case "firefox":
                driver_class = webdriver.Firefox
            case "edge":
                driver_class = webdriver.Edge
            case "ie":
                driver_class = webdriver.Ie
            case "safari":
                driver_class = webdriver.Safari
            case "remote":
                driver_class = webdriver.Remote
            case _:
                raise ValueError(f"Unsupported browser: {self.browser}")

        if is_docker():
            logging.warning("Running in Docker, using headless mode.")

        if driver_class is webdriver.Chrome:
            options = webdriver.ChromeOptions()
            if not self.debug or is_docker():
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
            else:
                options.add_argument("--window-size=1080,720")

            if download_path is not None:
                self.download_path = download_path
                data_path_str: str = f"{str(download_path.resolve())}{os.sep}"
                preferences = {
                    "download.default_directory": data_path_str,
                    "download.prompt_for_download": False,
                }
                options.add_experimental_option("prefs", preferences)
        elif driver_class is webdriver.Firefox:
            options = webdriver.FirefoxOptions()
            options.binary_location = browser_path

        args["options"] = options

        if driver_class is not None and options is not None:
            self.driver = driver_class(**args)
            self.listener = SeleniumEventListener()
            self.driver = EventFiringWebDriver(self.driver, self.listener)
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")

    def __getattr__(self, item):
        """Allows the SeleniumBrowser to proxy calls to the underlying WebDriver."""
        if hasattr(self.driver, item):
            return getattr(self.driver, item)

    @staticmethod
    def _element_is_probably_a_password(element: WebElement) -> bool:
        return element.get_attribute("type") == "password" or any(
            map(
                SeleniumBrowser._get_element_name(element).__contains__,
                ["password", "pwd", "passwd"],
            )
        )

    @staticmethod
    def _get_element_name(element: WebElement):
        """Turns a WebElement into a (hopefully) unique and human-readable identifier

        Args:
             element: The WebElement for which to get the name

        Returns:
            A string with the element's name

        Examples:
            >>> SeleniumBrowser._get_element_name(element)
            "div#some-id"
        """
        element_name: str = ""
        if element.get_attribute("id"):
            element_name = "#" + element.get_attribute("id")
        elif element.get_attribute("name"):
            element_name = f"[name={element.get_attribute('name')}]"
        elif element.get_attribute("class"):
            element_name = "." + element.get_attribute("class")

        return f"{element.tag_name}{element_name}"

    def _reset_state(self):
        """Utility method for resetting the state when a new page loads."""
        if self.download_path is not None:
            self.download_count = len(
                [
                    file
                    for file in self.download_path.rglob("*")
                    if not any(
                        file.suffix == f".{ext}" for ext in self.ignore_extensions
                    )
                ]
            )
        self.last_locator = None
        self.last_element = None

    def _set_last_element(self, element: WebElement):
        if self.debug:
            self.logger.debug(
                f"Setting last_element to {self._get_element_name(element)}"
            )
        self.last_element = element

    def close_window(self):
        """Closes the current window."""
        self.driver.close()
        if self.last_window is not None:
            self.driver.switch_to.window(self.last_window)

    @staticmethod
    def create_locator(
        search_method: By | str, search_value: str, element_type: str = "*"
    ) -> Locator:
        """Creates a locator tuple for use with Selenium's WebDriverWait

        Args:
            search_method: An instance of a Selenium By or a string containing a convenience method
                Convenience methods:
                    exact_text: Searches for an element with the exact text
                    stripped_exact_text: Searches for an element with the exact text, ignoring whitespace
                    text: Searches for an element containing the text
            search_value: The value to search for
            element_type: (When searching with XPath) The type of element to search for

        Returns:
            A tuple containing the search method and the search value

        Examples:
            >>> SeleniumBrowser.create_locator(search_method=By.XPATH,
            ...                                search_value="//div[@class='foo']",
            ...                                element_type="*")
            (By.XPATH, "//div[@class='foo']")

        """
        match search_method:
            case "exact_text":
                search_method = By.XPATH
                search_value = f"//{element_type}[text() = '{search_value}']"
            case "stripped_exact_text":
                search_method = By.XPATH
                search_value = (
                    f"//{element_type}[normalize-space(text()) = '{search_value}']"
                )
            case "text":
                search_method = By.XPATH
                search_value = f"//{element_type}[contains(text(), '{search_value}')]"

        locator: Locator = (search_method, search_value)
        return locator

    def act_on_browser(
        self,
        action: Optional[SeleniumBrowserActions],
        args: Optional[BrowserActionArgs],
    ):
        """Generic function to perform actions on the browser

        Args:
            action: An instance of a BrowserAction
            args: The arguments to the action

        Examples:
            >>> self.act_on_browser(action=SeleniumBrowserActions.GO,
            ...                     args=BrowserGoActionArgs(url="https://www.google.com"))
        """
        match action:
            case SeleniumBrowserActions.GO:
                if isinstance(args, BrowserGoActionArgs):
                    self.go(args.url)
            case SeleniumBrowserActions.NEW_TAB:
                self.driver.execute_script("window.open();")
            case SeleniumBrowserActions.SWITCH_TAB:
                if isinstance(args, BrowserSwitchTabActionArgs):
                    self.last_window = self.driver.current_window_handle
                    match args.tab:
                        case "next":
                            for handle in self.driver.window_handles:
                                if handle != self.last_window:
                                    self.logger.debug(f"Switching to: {handle}")
                                    self.driver.switch_to.window(handle)
                                    break
                        case other:
                            # Assume the tab is a window title or URL
                            found_tab: bool = False
                            for handle in self.driver.window_handles:
                                self.driver.switch_to.window(handle)
                                if (
                                    other in self.driver.title
                                    or other in self.driver.current_url
                                ):
                                    found_tab = True
                                    self.logger.debug(f"Switching to: {handle}")
                                    break

                            if not found_tab:
                                self.driver.switch_to.window(self.last_window)
            case SeleniumBrowserActions.WAIT:
                args = cast(BrowserWaitActionArgs, args)
                self.wait_for_user(args)

    def act_on_element(
        self,
        element: Optional[WebElement] = None,
        xpath_selector: Optional[str] = None,
        action: Optional[SeleniumElementActions] = SeleniumElementActions.CLICK,
        args: Optional[ElementActionArgs] = None,
    ) -> None:
        """Generic function to perform actions on elements

        Args:
            element: An instance of WebElement on which to perform the action
            xpath_selector: If element is not specified and xpath_selector is, the xpath_selector will be used to find the element
            action: The action to perform on the element (default: CLICK)
            args: An instance of ElementActionArgs containing the arguments to the action

        Examples:
            >>> self.act_on_element(xpath_selector="//input[name='username']",
            ...                     action=SeleniumElementActions.TYPE,
            ...                     args=ElementTypeActionArgs(text="username"))

        """
        if args is not None:
            if (
                action == SeleniumElementActions.WAIT
                and isinstance(args, ElementWaitActionArgs)
                or args.wait is not None
            ):
                wait_fn: Callable = ExpectedConditionsNameToFunction[
                    ExpectedConditions("presence_of_element_located")
                ]
                if isinstance(args.wait_for, str):
                    wait_fn = ExpectedConditionsNameToFunction[
                        ExpectedConditions(args.wait_for)
                    ]
                self.logger.debug(f"Waiting for {args.wait_for} on {args.locate_value}")
                element = self.wait_for_element(
                    duration=args.duration or self.default_wait,
                    condition=wait_fn,
                    search_method=args.locate_by,
                    search_value=args.locate_value,
                )
                self.logger.debug(
                    f"Waited on {element} {self._get_element_name(element)}"
                )

            if (
                element is None
                and args.locate_value is not None
                and (args.locate_by is not None or self.last_method is not None)
            ):
                element = self.find_element(
                    search_method=args.locate_by or self.last_method,
                    search_value=args.locate_value,
                )

        if element is None:
            if xpath_selector is None:
                element = self.last_element
            else:
                element = self.find_element(By.XPATH, xpath_selector)
        else:
            self.last_element = element

        if element is None:
            raise selenium.common.exceptions.NoSuchElementException

        if self.debug:
            self.logger.debug(f"{action} on {self._get_element_name(element)}")
        if (
            self.debug
            and action == SeleniumElementActions.TYPE
            and isinstance(args, ElementTypeActionArgs)
        ):
            if self._element_is_probably_a_password(element):
                self.logger.debug("Typed: " + "*" * len(args.text))
            else:
                self.logger.debug(f"Typed: {args.text}")

        try:
            match action:
                case SeleniumElementActions.CHANGE:
                    if element.tag_name == "select" and isinstance(
                        args, ElementChangeActionArgs
                    ):
                        Select(element).select_by_value(args.value)
                case SeleniumElementActions.CLICK:
                    self.wait_for_element(
                        condition=ExpectedConditionsNameToFunction[
                            "element_to_be_clickable"
                        ],
                        duration=1,
                        search_method=args.locate_by,
                        search_value=args.locate_value,
                    )
                    if args.inject:
                        self.driver.execute_script("arguments[0].click();", element)
                    else:
                        element.click()
                case SeleniumElementActions.DELETE:
                    self.driver.execute_script(
                        "arguments[0].parentNode.removeChild(arguments[0]);", element
                    )
                case SeleniumElementActions.INSERT:
                    if isinstance(args, ElementInsertActionArgs):
                        self.driver.execute_script(
                            'arguments[0].innerHTML = "%s";' % args.html, element
                        )
                case SeleniumElementActions.INSERT_TRUSTED:
                    if isinstance(args, ElementInsertActionArgs):
                        self.driver.execute_script(
                            """
                        const policy = trustedTypes.createPolicy('insert', {
                            createHTML: (s) => s,
                        });
                        const element = document.createElement('div');
                        element.innerHTML = policy.createHTML("%s");
                        arguments[0].appendChild(element);
                        """
                            % args.html,
                            element,
                        )
                case SeleniumElementActions.MOVE_TO:
                    if args.inject:
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView(); arguments[0].focus();",
                            element,
                        )
                    else:
                        ActionChains(self.driver).move_to_element(element).perform()
                case SeleniumElementActions.SET_ATTRIBUTE:
                    if isinstance(args, ElementSetAttributeActionArgs):
                        self.driver.execute_script(
                            f"arguments[0].setAttribute('{args.attribute}', '{args.value}');",
                            element,
                        )
                case SeleniumElementActions.TYPE:
                    if isinstance(args, ElementTypeActionArgs):
                        if args.inject:
                            self.driver.execute_script(
                                f"arguments[0].value = '{args.text}';", element
                            )
                        else:
                            send_enter: bool = False

                            if args.text.endswith("\\n"):
                                send_enter = True
                                args.text = args.text[:-2]
                            element.send_keys(args.text)

                            if send_enter:
                                element.send_keys(Keys.RETURN)

        except Exception as exception:
            self.exception_wait(exception)

    def find_element(
        self,
        search_method: Optional[By | str] = None,
        search_value: Optional[str] = None,
        element_type: Optional[str] = "*",
    ) -> Optional[WebElement]:
        """Generic function wrapping the Selenium find_element() method

        Args:
            search_method: An instance of a Selenium By or a string containing the name of a By method
            search_value: The value to search for
            element_type: (When searching with XPath) The type of element to search for

        Returns:
            An instance of a Selenium WebElement or None if the element was not found

        Examples:
            >>> self.find_element(By.ID, "my_id")
            >>> self.find_element("text", "Some text")

        """
        if search_value is None:
            self.logger.warning("No search value provided")
            return None

        if search_method is None:
            if self.last_method is None:
                search_method = By.ID
            else:
                search_method = self.last_method

        self.last_method = search_method
        self.last_locator = SeleniumBrowser.create_locator(
            search_method, search_value, element_type
        )

        try:
            element: WebElement = self.driver.find_element(*self.last_locator)
            self._set_last_element(element)
            return self.last_element
        except (
            selenium.common.exceptions.NoSuchElementException
        ) as no_such_element_exception:
            self.logger.warning(f"{no_such_element_exception}")
            self.logger.warning(f"Element not found: {search_method}={search_value}")
            self.exception_wait(no_such_element_exception)
            return None

    def find_elements(
        self,
        search_method: Optional[By | str] = None,
        search_value: Optional[str] = None,
        element_type: Optional[str] = "*",
    ) -> List[WebElement]:
        """Generic function wrapping the Selenium find_elements() method

        Args:
            search_method: An instance of a Selenium By or a string containing the name of a By method
            search_value: The value to search for
            element_type: (When searching with XPath) The type of element to search for

        Returns:
            A list of Selenium WebElements

        Examples:
            >>> self.find_elements(By.ID, "my_id")
            >>> self.find_elements("text", "Some text")

        """
        if search_value is None:
            self.logger.warning("No search value provided")
            return []

        if search_method is None:
            if self.last_method is None:
                search_method = By.ID
            else:
                search_method = self.last_method

        self.last_method = search_method
        self.last_locator = SeleniumBrowser.create_locator(
            search_method, search_value, element_type
        )

        try:
            elements: List[WebElement] = self.driver.find_elements(*self.last_locator)
            if len(elements) > 0:
                self._set_last_element(elements[0])
                return elements
            else:
                return []
        except (
            selenium.common.exceptions.NoSuchElementException
        ) as no_such_element_exception:
            self.logger.warning(f"{no_such_element_exception}")
            self.logger.warning(f"Element not found: {search_method}={search_value}")
            self.exception_wait(no_such_element_exception)
            return []

    def go(self, url: str):
        """Browses to a new URL

        Args:
            url: The URL to browse to

        Examples:
            >>> self.go('https://google.com')
        """
        self._reset_state()
        return self.driver.get(url)

    def run_actions(self, actions: List[SeleniumAction], delay: Optional[int] = 0):
        """Runs a list of SeleniumActions

        Args:
            actions: A list of SeleniumActions
            delay: The number of seconds to wait between each step
        """
        for action in actions:
            args: Type = ActionNameToArgumentClass[action.action]
            if action.args is not None:
                action.args = cast(args, action.args)
            if action.target == SeleniumTargets.BROWSER:
                self.act_on_browser(action=action.action, args=action.args)
            elif action.target == SeleniumTargets.ELEMENT:
                self.act_on_element(action=action.action, args=action.args)
            else:
                self.logger.warning("Unknown target: " + action.target)

            # When delaying, we don't need to pause between a wait condition and the next action
            if delay > 0 and args != ElementWaitActionArgs:
                time.sleep(delay)

    def run_json(self, json: str, delay: Optional[int] = 0):
        """Runs a JSON string containing a list of SeleniumActions

        Args:
            json: A JSON string containing a list of SeleniumActions
            delay: The number of seconds to wait between each step
        """
        json_to_run = jsons.loads(json, List[SeleniumAction], strict=True)

        self.run_actions(json_to_run, delay)

    def run_yaml(self, yaml_str: str, delay: Optional[int] = 0):
        """Runs a YAML string containing a list of SeleniumActions

        Args:
            yaml_str: A YAML string containing a list of SeleniumActions
            delay: The number of seconds to wait between each step
        """
        yaml_to_run = yaml.safe_load(yaml_str)

        actions: List[SeleniumAction] = []
        for action in yaml_to_run:
            if "args" not in action:
                action["args"] = None
            actions.append(SeleniumAction(**action))

        self.run_actions(actions, delay)

    def wait_for_element(
        self,
        duration: Optional[int] = 60,
        condition: Callable = ExpectedConditionsNameToFunction[
            "presence_of_element_located"
        ],
        search_method: Optional[By | str] = None,
        search_value: Optional[str] = None,
    ) -> Optional[WebElement]:
        """Generic function waiting for an element to be in some condition on the page

        Args:
            duration: The number of seconds to wait for the element
            condition: The condition to wait for
            search_method: An instance of a Selenium By or a string containing the name of a convenience method
            search_value: The value to search for

        Returns:
            True if the element meets the condition within the duration, False otherwise

        Examples:
            >>> self.wait_for_element(60, ExpectedConditionsNameToFunction["presence_of_element_located"], By.ID, "my_id")
            True
        """
        if search_method is not None and search_value is not None:
            self.last_method = search_method
            self.last_locator = SeleniumBrowser.create_locator(
                search_method, search_value
            )
        elif search_method is None and self.last_method is not None:
            self.last_locator = SeleniumBrowser.create_locator(
                self.last_method, search_value
            )
        else:
            self.logger.warning("No locator provided")
            return None

        try:
            self._set_last_element(
                WebDriverWait(self.driver, duration).until(
                    condition(self.last_locator)  # noqa
                )
            )
            return self.last_element
        except selenium.common.exceptions.TimeoutException as timeout_exception:
            self.logger.warning(f"{timeout_exception}")
            self.logger.warning(
                f"Element {self.last_locator} did not meet condition: {condition.__name__}"
            )
            self.exception_wait(timeout_exception)
            return None

    def wait_for_download(
        self, filename_glob: Optional[str] = "*", duration: Optional[int] = 120
    ) -> Path | None:
        """Waits for a file to be downloaded

        Args:
            filename_glob: A glob pattern to match the filename
            duration: The number of seconds to wait for the file to download

        Returns:
            The path to the downloaded file or None if the file was not downloaded

        Examples:
            >>> self.wait_for_download(filename_glob="*", duration=120)
            True
        """
        count: int = 0
        while count < duration:
            count += 1
            time.sleep(1)
            if (
                len(
                    [
                        file
                        for file in self.download_path.rglob(filename_glob)
                        if not any(
                            file.suffix == f".{ext}" for ext in self.ignore_extensions
                        )
                    ]
                )
                > self.download_count
            ):
                # Find the name of the new file
                new_file: Path = max(
                    self.download_path.rglob(filename_glob), key=os.path.getctime
                )
                return new_file
            elif count >= duration:
                return None

    def wait_for_user(self, args: BrowserWaitActionArgs):
        if hasattr(args, "duration"):
            self.logger.debug(f"Sleeping for {args.duration} seconds...")
            if args.duration == 0:
                while True:
                    time.sleep(1)
            else:
                for i in range(0, args.duration):
                    time.sleep(1)

    def exception_wait(self, exception: Exception):
        """Pauses execution on an exception

        Args:
            exception: The exception to pause on
        """
        if self.pause_on_exception is not None:
            self.logger.warning(
                f"There was an exception, pausing for {self.pause_on_exception} seconds"
            )
            self.logger.warning(f"Exception: {exception}")
            self.logger.warning(
                f"Last element: {self._get_element_name(self.last_element)} {self.last_locator}"
            )
            time.sleep(self.pause_on_exception)
            raise exception
