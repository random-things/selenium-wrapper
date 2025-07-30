# selenium-wrapper

A basic wrapper for Selenium WebDriver that provides a few methods to make it easier to use.

## Convenience methods

### `SeleniumBrowser.run_json(json: str)`
Runs a series of actions based on a JSON string.

### `SeleniumBrowser.run_yaml(yaml_str: str)`
Runs a series of actions based on a YAML string.

### `SeleniumBrowser.wait_for_download(filename_glob: str = "*", duration: int = 120)`
Waits for a file to be downloaded.

## Data Format
A list of `SeleniumAction`s:

### SeleniumAction
`target: str`: browser | element

`action: str` with `target = browser`: `go | new_tab | switch_tab`

`action: str` with `target = element`: `change | click | delete | insert | insert_trusted | move_to | set_attribute | type | wait`

`args: dict`: Arguments for the action

#### SeleniumBrowserGoActionArgs

`url: str`: URL to navigate to

#### SeleniumBrowserSwitchTabActionArgs

`tab: str`: Title or URL of the tab to switch to

#### SeleniumElementActionArgs

`locate_by: str`: How to locate the element. One of `css_selector | id | link_text | name | partial_link_text | tag_name | xpath`

`locate_value: str`: The value to use to locate the element

`inject: bool`: Whether to inject the action into the browser as JavaScript to execute on the page instead of trying to apply it externally. This prevents "the element is not clickable" errors.

`wait`: Whether to wait for some condition to be met before performing the action. Defaults to `false`.

`wait_for`: The condition to wait for. Defaults to `presence_of_element_located`.

`duration`: The number of seconds to wait for the condition to be met. Defaults to `10`.

#### SeleniumElementChangeActionArgs

`value: str`: The value to change the element to

#### SeleniumElementInsertActionArgs

`html: str`: The HTML to insert into the element

#### SeleniumElementSetAttributeActionArgs

`attribute: str`: The attribute to set

`value: str`: The value to set the attribute to

#### SeleniumElementTypeActionArgs

`text: str`: The string to type into the element



## Examples

The following two examples are equivalent, showing the JSON and YAML representations of the same actions.

```python
from selenium_wrapper import SeleniumBrowser


browser = SeleniumBrowser()

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
            "locate_value": "//input[@title='Search']"
            "text": "Hello World",
            "wait": true
        }
    },
    {
        "action": "click",
        "args": {
            "locate_value": "//input[@type='submit']"
        }
    }
]
"""

browser.run_json(json)

yaml_str: str = """
- target: browser
  action: go
  args:
    url: https://www.google.com
- target: element
  action: type
  args:
    locate_by: xpath
    locate_value: //input[@title='Search']
    text: Hello World
    wait: true
- target: element
  action: click
  args:
    locate_value: //input[@type='submit']
"""

browser.run_yaml(yaml_str)
```
