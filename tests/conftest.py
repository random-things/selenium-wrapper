def pytest_addoption(parser):
    parser.addoption(
        "--browser_name",
        action="store",
        default="chrome",
        help="Browser to use for testing",
    )
    parser.addoption(
        "--firefox_path",
        action="store",
        default=None,
        help="Path to Firefox executable",
    )
