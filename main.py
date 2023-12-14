import urllib.parse
from random import choice
from time import sleep
from typing import List
from dotenv import load_dotenv
import os
from selenium.webdriver import FirefoxOptions, Firefox, Keys
from dataclasses import dataclass, field
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()

@dataclass
class AutomateHDFC:
    base_url: str = 'https://netportal.hdfcbank.com'
    uas: List[str] = field(
        default_factory=lambda: ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
                                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.8',
                                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0 Herring/97.1.1600.1'])

    def webdriversetup(self):
        ua = choice(self.uas)
        opt = FirefoxOptions()
        opt.add_argument("--start-maximized")
        # opt.add_argument("--headless")
        opt.add_argument("--no-sandbox")
        # opt.add_argument("-profile")
        # opt.add_argument(profile_path)
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.set_preference("general.useragent.override", ua)
        opt.set_preference('dom.webdriver.enable', False)
        opt.set_preference('useAutomationExtension', False)
        opt.set_preference("browser.cache.disk.enable", False)
        opt.set_preference("browser.cache.memory.enable", False)
        opt.set_preference("browser.cache.offline.enable", False)
        opt.set_preference("network.http.use-cache", False)
        opt.set_preference("browser.privatebrowsing.autostart", True)

        driver = Firefox(options=opt)
        # print(ua)

        return driver

    def login(self):
        driver = self.webdriversetup()
        driver.maximize_window()
        login_url = urllib.parse.urljoin(self.base_url, '/login')
        driver.get(login_url)
        wait = WebDriverWait(driver, 20)
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input#liabiltyLoginCustId')))
        driver.find_element(By.CSS_SELECTOR, 'input#liabiltyLoginCustId').click()
        driver.find_element(By.CSS_SELECTOR, 'input#liabiltyLoginCustId').send_keys(os.getenv('HDFC_LOGIN_ID') + Keys.RETURN)
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input#keyboard')))
        driver.find_element(By.CSS_SELECTOR, 'input#keyboard').send_keys(os.getenv('HDFC_PASSWORD'))
        driver.find_element(By.CSS_SELECTOR, 'input#secureAccessID').click()
        driver.find_element(By.CSS_SELECTOR, 'a#loginBtn').click()
        elements = wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.f6 > li')))
        for element in elements:
            # print(element.text)
            if 'Money Transfer' in element.text:
                element.find_element(By.CSS_SELECTOR, 'a').click()
                break
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input#mtPayeeSearch')))
        sleep(10)
        driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary.login-btn').click()
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn.btn-primary.nb-logout.yes-btn'))).click()
        # input('Please Enter')
        sleep(10)
        driver.close()

if __name__ == '__main__':
    scraper = AutomateHDFC()
    scraper.login()
