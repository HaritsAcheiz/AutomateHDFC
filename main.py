from urllib.parse import urljoin
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
from httpx import Client


load_dotenv()

@dataclass
class AutomateHDFC:
    bank_base_url: str = 'https://netportal.hdfcbank.com'
    uas: List[str] = field(
        default_factory=lambda: ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
                                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.8',
                                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0 Herring/97.1.1600.1'])
    server_base_url: str = 'https://wat2xkrydv.ap-south-1.awsapprunner.com'

    def get_login_info(self):
        print('Getting_login_info...')
        login_info_url = urljoin(self.server_base_url, '/api/v1/logininfo/get-login-info')
        with Client() as client:
            response = client.post(login_info_url)
            if response != 200:
                response.raise_for_status()
        json_response = response.json()
        result = json_response['resData']['data'][0]
        print(result)
        print('Login info collected!')
        return result

    def update_login_status(self):
        print('Update_login_info...')
        end_point = urljoin(self.server_base_url, '/api/v1/logininfo/update-login-status')
        with Client() as client:
            response = client.post(end_point)
            if response != 200:
                response.raise_for_status()
        json_response = response.json()
        print(json_response)

    def get_payee_info(self):
        print('Getting_payee_info...')
        end_point = urljoin(self.server_base_url, '/api/v1/payee/get-payee')
        with Client() as client:
            response = client.get(end_point)
            if response != 200:
                response.raise_for_status()
        json_response = response.json()
        print(json_response)
        result = json_response['resData']['data']
        print('Payee info collected!')
        return result

    def update_payee_info(self):
        print('Update payee info...')
        end_point = urljoin(self.server_base_url, '/api/v1/payee/update-payee-status')
        with Client() as client:
            response = client.get(end_point)
            if response != 200:
                response.raise_for_status()
        json_response = response.json()
        print(json_response)
        # result = json_response['resData']['data'][0]
        # print('Payee info collected!')

    def get_otp(self):
        print('Getting_otp...')
        end_point = urljoin(self.server_base_url, '/api/v1/payeeotp/add-payee-otp')
        with Client() as client:
            trials = 0
            while trials < 3:
                response = client.post(end_point)
                if response.status_code == 200:
                    break
                else:
                    print(response.status_code)
                    trials += 1
                    continue
        json_response = response.json()
        print(json_response)
        result = json_response['resData']['data']['otp']
        print('OTP collected!')
        return result

    def update_otp_status(self):
        print('Updating OTP status...')
        end_point = urljoin(self.server_base_url, '/api/v1/payee/update-payee-otp-status ')
        with Client() as client:
            response = client.post(end_point)
            if response != 200:
                response.raise_for_status()
        json_response = response.json()
        print(json_response)
        result = json_response['resData']['data']['otp']
        print('OTP collected!')
        return result

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

    def add_payee_account(self, driver, payee_account):
        wait = WebDriverWait(driver, 15)
        driver.find_element(By.CSS_SELECTOR, 'input#payeeNicknameControl').send_keys(payee_account['nickname'])
        elements = driver.find_elements(By.CSS_SELECTOR, 'div.col-md-12.margin-top10.radio-input.ng-scope > div')
        for element in elements:
            if 'non-hdfc bank account in india' in element.text.lower():
                element.find_element(By.CSS_SELECTOR, 'input').click()
                break
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input#nameOnAccount'))).click()
        driver.find_element(By.CSS_SELECTOR, 'input#nameOnAccount').send_keys(
            payee_account['account_holder_name'] + Keys.TAB + payee_account['bank_account_number'] + Keys.TAB + payee_account[
                'bank_account_number'])
        driver.find_element(By.CSS_SELECTOR, 'div[placeholder="Please Choose One"] > span').click()
        driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Please Choose One"]').send_keys(
            payee_account['account_type'] + Keys.RETURN)
        driver.find_element(By.CSS_SELECTOR, 'a[ng-click="addPayeeNonHDFCCtrl.findIFSC()"]').click()
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input#ifscCodeControl'))).click()
        driver.find_element(By.CSS_SELECTOR, 'input#ifscCodeControl').send_keys(payee_account['ifsc_code'])
        wait.until(expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, 'a[control="findIFSCCtrl.ifscContinueControl"]'))).click()
        wait.until(expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, 'a[ng-click="findIFSCCtrl.selectedBank(Details)"]'))).click()
        wait.until(expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, 'a[control="addPayeeCtrl.continueControlToConfirmPage"]'))).click()
        wait.until(expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, 'input[ng-click="nonHDFCPayeeConfirmCtrl.checkValidation()"]'))).click()
        driver.find_element(By.CSS_SELECTOR, 'a[ng-click="nonHDFCPayeeConfirmCtrl.confirmNonHdfcPayee()"]').click()
        OTP = self.get_otp()
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input#mobileOtp'))).click()
        driver.find_element(By.CSS_SELECTOR, 'input#mobileOtp').send_keys(OTP)
        driver.find_element(By.CSS_SELECTOR, 'a[control="continueOtpControl"]').click()

    def main(self):
        print('Setting Webdriver...')
        driver = self.webdriversetup()
        driver.maximize_window()
        print('Webdriver is ready!')

        print('Login...')
        login_url = urljoin(self.bank_base_url, '/login')
        driver.get(login_url)
        wait = WebDriverWait(driver, 25)
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input#liabiltyLoginCustId')))
        driver.find_element(By.CSS_SELECTOR, 'input#liabiltyLoginCustId').click()
        login_info = self.get_login_info()
        driver.find_element(By.CSS_SELECTOR, 'input#liabiltyLoginCustId').send_keys(login_info['customer_id'] + Keys.RETURN)
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input#keyboard')))
        driver.find_element(By.CSS_SELECTOR, 'input#keyboard').send_keys(login_info['password'])

        # opt2
        # wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input#fldPasswordDispId')))
        # driver.find_element(By.CSS_SELECTOR, 'input#fldPasswordDispId').send_keys(login_info['password'])

        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input#secureAccessID'))).click()

        # opt2
        # driver.find_element(By.CSS_SELECTOR, 'a.login-btn').click()

        driver.find_element(By.CSS_SELECTOR, 'a.loginBtn').click()
        elements = wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.f6 > li')))
        print('Login successfully!')

        print('Adding Payee account...')
        for element in elements:
            if 'add payee' in element.text.lower():
                element.find_element(By.CSS_SELECTOR, 'a').click()
                break
        payee_account = self.get_payee_info()
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input#payeeNicknameControl'))).click()
        self.add_payee_account(driver=driver, payee_account=payee_account)
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn.btn-primary.login-btn'))).click()
        wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn.btn-primary.nb-logout.yes-btn'))).click()
        # input('Please Enter')
        driver.close()

if __name__ == '__main__':
    scraper = AutomateHDFC()
    # scraper.get_otp()
    scraper.main ()
    # scraper.get_payee_info()
    # scraper.update_login_status()