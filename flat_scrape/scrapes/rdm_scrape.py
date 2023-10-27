import re
import asyncio
import aiohttp
import json
import requests
from bs4 import BeautifulSoup
from itertools import chain

from . import standardize_flat_info as std
from .scrape_functions import get_developer_info, get_developer_investments, get_html_response, collect_investment_data, \
    collect_flats_with_floors

developerName = 'RDM Inwestycje Deweloperskie'
baseUrl = 'https://rdminwestycje.pl/'

investmentHtmlInfo = {'investmentTag': ".find('ul', class_='sub-menu').find_all('li')[:4]",
                      'investmentName': ".get_text()",
                      'investmentLink': ".a['href']"}

investmentHtmlInfoFloors = {
    'floorTag': ".find_all('li', id=re.compile(r'menu-item-\\d+'), string=re.compile(r'(Parter|Piętro)'))",
    'floorLink': ".a['href']"}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = get_developer_investments(baseUrl, investmentHtmlInfo)
    return investmentsData


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
    data = eval(f"soup[0]{htmlData['floorTag']}")

    developerInvestments = {"name": investmentData['name'],
                            "investKey": re.compile(r'\w(?=pietro)').search(
                                eval(f"data[-1]{htmlData['floorLink']}")).group(),
                            "floorUrls": [eval(f"item{htmlData['floorLink']}")
                                          for item in data]}
    return developerInvestments


async def get_all_flats_on_floor(url, session):
    soup = await get_html_response(url=url, session=session)
    pattern = re.compile(r'var settings = (.*?);')
    data = soup[0].find('script', string=pattern).text
    match = re.search(r'var settings = (.*?);', data)
    flats = json.loads(match.group(1))
    floorValue = flats['general']['name'][-1]
    try:
        floorValue = int(floorValue)
    except ValueError:
        floorValue = 0
    flatsWithFloor = dict.fromkeys([item['title'] for item in flats['spots']], floorValue)
    return flatsWithFloor


def get_mappers():
    investData = get_investments_data()
    investFloorsUrls = asyncio.run(
        collect_investment_data(investmentsInfo=investData, htmlData=investmentHtmlInfoFloors,
                                function=get_all_floors_in_investment))
    investKeyMap = {
        item['investKey']: item['name']
        for item in investFloorsUrls
    }
    urls = list(chain.from_iterable([item['floorUrls']
                                     for item in investFloorsUrls]))
    flatFloorKeyMap = asyncio.run(collect_flats_with_floors(urls=urls, function=get_all_flats_on_floor))
    flatFloorKeyMap = {
        key: value
        for item in flatFloorKeyMap
        for key, value in item.items()}
    return investKeyMap, flatFloorKeyMap


def get_flats_data():
    mappers = get_mappers()
    flatToInvestName = mappers[0]
    flatToFloor = mappers[1]
    flatToFloor.update({"c25": 2})

    response = requests.get(baseUrl)
    soup = BeautifulSoup(response.text, 'html.parser')

    pattern = re.compile(r'var mieszkania = (.*?);')
    data = soup.find('script', string=pattern).text
    match = re.search(r'var mieszkania = (.*?);', data)

    flats = json.loads(match.group(1))
    formattedFlats = []
    for key, value in flats.items():
        if re.match("^[wgmc][0-9]+$", key):
            formattedFlats.append({
                "invest_name": flatToInvestName[key[0]],
                "floor_number": std.standardize_floor_number(flatToFloor[key]),
                "rooms_number": std.standardize_rooms(value["ilosc_pokoi"]),
                "area": std.standardize_price_and_area(value["powierzchnia"]),
                "price": std.standardize_price_and_area(value["cena"].replace(" ", "")),
                "status": std.standardize_status(value["status"]),
                "url": "https://rdminwestycje.pl/mieszkania/" + key
            })
    return formattedFlats
