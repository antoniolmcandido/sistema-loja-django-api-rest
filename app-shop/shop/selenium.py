from django.test import TestCase
from selenium import webdriver

class SeleniumTestCase(TestCase):
    def selenium_test(self):
        """Teste simples para verificar se o Selenium está configurado corretamente"""
        driver = webdriver.Chrome()
        driver.get("http://selenium.dev")
        driver.quit()