from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config


def turn_off_notification_option():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    return chrome_options


def login(driver, password, username):
    driver.get("https://www.instagram.com/accounts/login/?source=auth_switcher")
    assert "Instagram" in driver.title
    login_element = driver.find_element_by_name("username")
    login_element.send_keys(username)
    password_element = driver.find_element_by_name("password")
    password_element.send_keys(password)
    password_element.send_keys(Keys.ENTER)
    # WebDriverWait(driver, 5).until(EC.url_changes(driver.current_url))


def main(driver):
    login(driver, config.password, config.username)


if __name__ == '__main__':
    driver = webdriver.Chrome(chrome_options=turn_off_notification_option())
    driver.maximize_window()
    main(driver)
