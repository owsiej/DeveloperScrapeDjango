import json
import re
import time
import os

import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from . import standardize_flat_info as std


class Locators:
    HOME_PAGE_INVESTMENTS_MENU_BUTTON = (By.XPATH, "//*[@id='menu-item-4185']/a")

    INVESTMENTS_DATA = (By.XPATH, "//ul[@class='sub-menu']/li/a")

    USER_CHOICE_FROM_INVESTMENTS_LIST = (By.XPATH, "//ul[@class='sub-menu']/li[*]/a")

    INVESTMENT_NAME = (By.XPATH, "//div[@class='menuPort']//li[1]/a")

    FLOOR_BUTTONS = (By.XPATH, "//p[@class='zmien_pietro']//a")

    USER_CHOICE_FROM_FLOOR_BUTTONS = (By.XPATH, "//p[@class='zmien_pietro']//a[*]")

    FLOOR_NUMBER = (By.XPATH, "//span[@class='bt_bb_headline_content']")

    FLATS_NAME_TAG = (
        By.XPATH, '//h3[starts-with(@id, "tooltip-") and translate(substring(@id,10), "0123456789", "")=""]')

    RETURN_TO_MAIN_PAGE_BUTTON = (By.XPATH, '//*[@id="top"]/header/div/div/div/div[2]/span/a/img')

    FLATS_DATA = (By.XPATH, '/html/body/script[19]')

    COOKIE = {
        "name": "cookie_notice_accepted",
        "value": "false"
    }

    FLAT_NAME_TO_INVESTMENT_NAME_MAPPER = dict()

    FLOOR_VALUE_MAPPER = dict()


class ChromeDriver(webdriver.Chrome):
    def __init__(self):
        self.website = "https://rdminwestycje.pl/"
        self.driverPath = os.getenv("CHROME_DRIVER_PATH")
        self.service = Service(ChromeDriverManager(driver_version="114.0.5735.90").install())
        self.options = Options()
        # self.options.add_experimental_option("detach", True)
        self.options.add_argument("--headless=new")
        # self.options.add_argument("--no-startup-window")

        super().__init__(service=self.service, options=self.options)

    def add_new_cookie(self, cookie):
        self.add_cookie(cookie)

    def load_page(self):
        self.get(self.website)


class BaseActions:
    def __init__(self, driver):
        self.driver = driver

    def click(self, locator):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(locator)).click()

    def is_element_present(self, locator):
        return WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(locator))

    def are_elements_present(self, locator):
        try:
            elements = WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located(locator))
            return elements
        except selenium.common.exceptions.TimeoutException:
            return None


class HomePage(BaseActions):
    def __init__(self, driver):
        super().__init__(driver)

    def click_main_page_button(self):
        self.click(Locators.RETURN_TO_MAIN_PAGE_BUTTON)

    def click_investment_menu_button(self):
        self.click(Locators.HOME_PAGE_INVESTMENTS_MENU_BUTTON)

    def click_investment_of_user_choice_and_save_investment_name(self, choice):
        userChoice = Locators.USER_CHOICE_FROM_INVESTMENTS_LIST[1].replace("*", str(choice))
        self.click((Locators.USER_CHOICE_FROM_INVESTMENTS_LIST[0], userChoice))
        return self.is_element_present(Locators.INVESTMENT_NAME).text


class ScrapePages(HomePage):
    def __init__(self, driver: ChromeDriver):
        super().__init__(driver)
        driver.load_page()
        driver.add_new_cookie(Locators.COOKIE)

    def get_developer_data(self):
        developer = {"name": self.driver.execute_script("return document.title"),
                     "url": self.driver.website}
        return developer

    def get_investments_data(self):
        investments = [{
            "name": invest.get_attribute("innerHTML"),
            "url": invest.get_attribute('href')
        }
            for invest in self.driver.find_elements(*Locators.INVESTMENTS_DATA)[:-3]]
        return investments

    def click_floor_button_and_save_number(self, floorButton):
        userChoice = Locators.USER_CHOICE_FROM_FLOOR_BUTTONS[1].replace("*", str(floorButton))
        self.click((Locators.USER_CHOICE_FROM_FLOOR_BUTTONS[0], userChoice))
        return self.driver.find_element(*Locators.FLOOR_NUMBER).text.split(" ")[1]

    def get_all_flats_on_chosen_floor(self, floorNumber):
        flatsNameTags = self.are_elements_present(Locators.FLATS_NAME_TAG)
        allFlatsOnFloor = {"floorNumber": floorNumber,
                           "flats": []}
        if not flatsNameTags:
            return allFlatsOnFloor
        for tag in flatsNameTags:
            allFlatsOnFloor["flats"].append(int(re.search(r"\d+", tag.get_attribute("id").split("-")[1]).group()))

        return allFlatsOnFloor

    def get_investment_with_all_flats_on_floors(self, investmentChoice):

        self.click_investment_menu_button()
        investmentName = self.click_investment_of_user_choice_and_save_investment_name(investmentChoice).title()

        allFloorsInInvestment = self.are_elements_present(Locators.FLOOR_BUTTONS)
        floorToFlatsList = []

        flatKeyMap = self.is_element_present(Locators.FLATS_NAME_TAG)
        Locators.FLAT_NAME_TO_INVESTMENT_NAME_MAPPER.update(
            {flatKeyMap.get_attribute("id").split("-")[1][0]: investmentName})

        for i in range(1, len(allFloorsInInvestment) + 1):
            number = self.click_floor_button_and_save_number(i)
            flatsOnFloor = self.get_all_flats_on_chosen_floor(number)
            floorToFlatsList.append(flatsOnFloor)
        result = {investmentName: floorToFlatsList}
        Locators.FLOOR_VALUE_MAPPER.update(result)
        self.click_main_page_button()

    def get_flats_data(self):
        htmlData = self.is_element_present(Locators.FLATS_DATA).get_attribute("innerHTML")
        startIndex = htmlData.find("var mieszkania")
        endIndex = htmlData.find("var mieszkaniaSegment")
        scrapedFlatsData = json.loads(htmlData[startIndex:endIndex].replace(";", "").replace("var mieszkania = ", ""))
        formattedFlatsData = []
        for key, value in scrapedFlatsData.items():
            if not re.match("^[a-z][0-9]+$", key):
                continue
            investName = Locators.FLAT_NAME_TO_INVESTMENT_NAME_MAPPER[key[0]]
            formattedFlatsData.append({
                "invest_name": investName,
                "floor_number": std.standardize_floor_number(self.map_floor_number(key, investName)),
                "rooms_number": std.standardize_rooms(value["ilosc_pokoi"]),
                "area": std.standardize_price_and_area(value["powierzchnia"]),
                "price": std.standardize_price_and_area(value["cena"].replace(" ", "")),
                "status": std.standardize_status(value["status"])
            })
        return formattedFlatsData

    @staticmethod
    def map_floor_number(flatKey, investName):
        flatNumber = int(re.search(r"\d+", flatKey).group())
        investmentFloorToFlat = Locators.FLOOR_VALUE_MAPPER[investName]
        count = 0
        while count != 3:
            for flatsOnFloor in investmentFloorToFlat:
                if flatNumber in flatsOnFloor["flats"]:
                    return flatsOnFloor['floorNumber']
            flatNumber -= 1
            count += 1
        return "coś poszło nie tak"


def run_page():
    driverTest = ChromeDriver()
    scrape = ScrapePages(driverTest)
    return scrape


def get_developer_data():
    scrape = run_page()
    developerData = scrape.get_developer_data()
    return developerData


def get_investments_data():
    scrape = run_page()
    investmentsData = scrape.get_investments_data()
    return investmentsData


def get_flats_data():
    investmentsData = get_investments_data()
    scrape = run_page()
    for x in range(1, len(investmentsData) + 1):
        scrape.get_investment_with_all_flats_on_floors(x)

    flatsData = scrape.get_flats_data()
    return flatsData
