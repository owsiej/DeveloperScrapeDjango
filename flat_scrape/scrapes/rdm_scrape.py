import re
import time
import os
import asyncio
import aiohttp
from itertools import chain
import threading
from multiprocessing.pool import ThreadPool
from functools import partial
import json
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from . import standardize_flat_info as std
from .scrape_functions import get_developer_info, get_developer_investments, get_html_response, collect_investment_data


class ChromeDriver:
    def __init__(self):
        self.driverPath = os.getenv("CHROME_DRIVER_PATH")
        self.service = Service(executable_path=self.driverPath)
        self.options = Options()
        # self.options.add_experimental_option("detach", True)
        self.options.add_argument("--headless=new")
        # self.options.add_argument("--no-startup-window")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

    def __del__(self):
        self.driver.quit()

    @classmethod
    def get_driver(cls):
        the_driver = getattr(threadLocal, 'driver', None)
        if the_driver is None:
            the_driver = cls()
            setattr(threadLocal, 'driver', the_driver)
        driver = the_driver.driver
        the_driver = None
        return driver


threadLocal = threading.local()


async def get_all_floors_in_investment(investmentData, htmlData: dict, session: aiohttp.ClientSession, baseUrl) -> list:
    """

    Args:
        htmlData: dict of tags needed to scrape for buildings
        investmentData: all information about current investment
        session: session used to make async requests
        baseUrl: url of developer site
    Returns:
        Object - Investment name, link to investment
    """

    soup = await get_html_response(url=baseUrl + investmentData['url'], session=session)
    data = eval(f"soup{htmlData['floorTag']}")

    developerInvestments = {"name": investmentData['name'],
                            "investKey": re.compile(r'\w(?=pietro)').search(
                                eval(f"data[-1]{htmlData['floorLink']}")).group(),
                            "floorUrls": [eval(f"item{htmlData['floorLink']}")
                                          for item in data]}

    return developerInvestments


def get_flats_floor_number(url, htmlData: dict):
    flatsToFloors = {}

    driver = ChromeDriver.get_driver()
    driver.get(url)
    time.sleep(0.5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = soup.find_all(htmlData['flatTag'])
    floorNumber = eval(f"soup{htmlData['floorNumber']}")
    for item in data:
        flatsToFloors.update({
            item[htmlData['flatName']]: int(floorNumber)
        })

    return flatsToFloors


def get_mappers():
    investFloorsUls = asyncio.run(
        collect_investment_data(investmentsInfo=get_investments_data(), htmlData=investmentHtmlInfoFloors,
                                function=get_all_floors_in_investment))
    urls = list(chain.from_iterable(map(lambda x: x['floorUrls'], investFloorsUls)))
    investKeyMap = {
        item['investKey']: item['name']
        for item in investFloorsUls
    }
    partialFunc = partial(get_flats_floor_number, htmlData=flatsHtmlInfoFloors)
    with ThreadPool() as pool:
        mapper = pool.map(partialFunc, urls)

    flatFloorKeyMap = {
        key: value
        for item in mapper
        for key, value in item.items()}
    return investKeyMap, flatFloorKeyMap


developerName = 'RDM Inwestycje Deweloperskie'
baseUrl = 'https://rdminwestycje.pl/'

investmentHtmlInfo = {'investmentTag': ".find('ul', class_='sub-menu').find_all('li')[:3]",
                      'investmentName': ".get_text()",
                      'investmentLink': ".a['href']"}

investmentHtmlInfoFloors = {
    'floorTag': ".find_all('li', id=re.compile(r'menu-item-\\d+'), string=re.compile(r'(Parter|Piętro)'))",
    'floorLink': ".a['href']"}

flatsHtmlInfoFloors = {
    'flatTag': 'polygon',
    'flatName': 'data-shape-title',
    'floorNumber': ".find('span', class_='bt_bb_headline_content').text.split()[1]"
}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = get_developer_investments(baseUrl, investmentHtmlInfo)
    return investmentsData


def get_flats_data():
    mappers = get_mappers()
    flatToInvestName = mappers[0]
    flatToFloor = mappers[1]

    response = requests.get("https://rdminwestycje.pl/")
    soup = BeautifulSoup(response.text, 'html.parser')

    pattern = re.compile(r'var mieszkania = (.*?);')
    data = soup.find('script', string=pattern).text
    match = re.search(r'var mieszkania = (.*?);', data)

    flats = json.loads(match.group(1))
    formattedFlats = []
    for key, value in flats.items():
        if re.match("^[a-z][0-9]+$", key):
            formattedFlats.append({
                "invest_name": flatToInvestName[key[0]],
                "floor_number": std.standardize_floor_number(flatToFloor[key]),
                "rooms_number": std.standardize_rooms(value["ilosc_pokoi"]),
                "area": std.standardize_price_and_area(value["powierzchnia"]),
                "price": std.standardize_price_and_area(value["cena"].replace(" ", "")),
                "status": std.standardize_status(value["status"])
            })
    return formattedFlats
