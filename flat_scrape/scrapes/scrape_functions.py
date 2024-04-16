import requests
from bs4 import BeautifulSoup
import unicodedata
import re
import asyncio
import aiohttp
from lxml import etree
from . import standardize_flat_info as std


async def get_json_response(url, session):
    async with session.get(url) as response:
        data = await response.json()
        return data


async def get_html_response(url, session):
    async with session.get(url) as response:
        url = str(response.url)
        pageText = await response.text()
        data = BeautifulSoup(pageText, "html.parser")
        return [data, url]


async def post_html_request(url, session):
    async with session.post(url) as response:
        urlText = await response.text()
        data = BeautifulSoup(urlText, "html.parser")
        return data


def get_developer_info(name: str, url: str) -> dict:
    """

    Args:
        name: Name of developer
        url: Take link to developer page

    Returns:
        Object - developer name, url

    """
    developer = {"name": name,
                 "url": url}
    return developer


def get_developer_investments(url, htmlData: dict) -> list:
    """

    Args:
        url: link to developer page
        htmlData: dictionary with strings of code for:
         investmentTag - tag in html where new investment is added
         investmentName - tag containing investment name
         investmentLink - tag containing link to investment
    Returns:
        Object - Investment name, link to investment
    """
    developerInvestments = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    data = eval(f"soup{htmlData['investmentTag']}")
    for item in data:
        investName = eval(f"item{htmlData['investmentName']}")
        developerInvestments.append(
            {"name": unicodedata.normalize('NFKD', investName) if not isinstance(investName, list) else investName,
             "url": eval(f"item{htmlData['investmentLink']}")})

    return developerInvestments


async def get_new_page_links(investmentData: dict, htmlData: dict,
                             session: aiohttp.ClientSession, baseUrl) -> list:
    """
    If investment on page with flats has got button "Next Page" then this function gets all links of new pages
    to later scrape from them.
    Args:
        baseUrl: url to developer page
        investmentData: all information about current investment
        session: session used to make async requests
        htmlData: dictionary with string of code for:
            nextPageTag - tag containing next Page Button
            nextPageLink - tag to link by itself

    Returns:
        final list of dict with all investments and links to them
    """
    investmentsFinalInfo = []

    soup = await get_html_response(url=investmentData['url'], session=session)
    while True:
        nextPage = eval(f"soup[0]{htmlData['nextPageTag']}")

        if nextPage is not None:
            investmentsFinalInfo.append({'name': investmentData['name'],
                                         'url': baseUrl + eval(f"nextPage{htmlData['nextPageLink']}")})
            response = requests.get(investmentsFinalInfo[-1]['url'])
            soup = [BeautifulSoup(response.text, "html.parser")]
        else:
            break

    return investmentsFinalInfo + [investmentData]


async def get_all_buildings_from_investment(investmentData: dict, htmlData: dict,
                                            session: aiohttp.ClientSession, baseUrl) -> list:
    """get names of all investments with links to them

    Args:
        htmlData: dict of tags needed to scrape for buildings
        baseUrl: url of developer site
        investmentData: all information about current investment
        session: session used to make async requests
    Returns:
        list of whole need data
    """

    listOfBuildings = []

    soup = await get_html_response(url=baseUrl + investmentData['url'], session=session)
    buildings = eval(f"soup[0]{htmlData['buildingTag']}")
    if buildings:
        for building in buildings:
            listOfBuildings.append({'name': eval(f"investmentData{htmlData['buildingName']}"),
                                    'url': baseUrl + eval(f"building{htmlData['buildingLink']}")})
    else:
        investmentData['url'] = soup[1]
        listOfBuildings.append(investmentData)
    return listOfBuildings


async def get_investment_flats(investLink: str, investName: str, htmlData: dict,
                               session: aiohttp.ClientSession, baseUrl) -> list:
    """

    Args:
        baseUrl: if investmentInfo contain links of only query string, you need to add baseUrl
        investName: name of investment
        investLink: link to investment
        session: session used to make async requests
        htmlData: dictionary with strings of code for:
         flatTag - tag in html where new flat is added
         floorNumber - tag containing floor number of flat,
         roomsAmount - tag containing rooms number of flat,
         area - tag containing area of flat,
         price - tag containing price of flat,
         status - tag containing status of flat
    Returns:
        list of dictionaries containing all info about flat
    """
    flats = []

    soup = await get_html_response(url=baseUrl + investLink, session=session)
    try:
        data = eval(f"soup[0]{htmlData['flatTag']}")
    except AttributeError:
        pass
    else:
        for flat in data:
            flats.append({
                'invest_name': investName,
                'floor_number': std.standardize_floor_number(eval(f"flat{htmlData['floorNumber']}"))
                if htmlData['floorNumber'] else None,
                'rooms_number': std.standardize_rooms(eval(f"flat{htmlData['roomsAmount']}")) if htmlData[
                    'roomsAmount'] else None,
                'area': std.standardize_price_and_area(eval(f"flat{htmlData['area']}")) if htmlData[
                    'area'] else None,
                'price': std.standardize_price_and_area(
                    unicodedata.normalize('NFKD', eval(f"flat{htmlData['price']}"))) if htmlData[
                    'price'] else 0,
                'status': std.standardize_status(eval(f"flat{htmlData['status']}")),
                'url': htmlData['baseUrl'] + eval(f"flat{htmlData['url']}") if htmlData[
                    'url'] else investLink
            })

    return flats


async def get_investment_flats_post(investLink: str, investName: str, htmlData: dict,
                                    session: aiohttp.ClientSession, baseUrl) -> list:
    """

    Args:
        baseUrl: if investmentInfo contain links of only query string, you need to add baseUrl
        investName: name of investment
        investLink: link to investment
        session: session used to make async requests
        htmlData: dictionary with strings of code for:
         flatTag - tag in html where new flat is added
         floorNumber - tag containing floor number of flat,
         roomsAmount - tag containing rooms number of flat,
         area - tag containing area of flat,
         price - tag containing price of flat,
         status - tag containing status of flat
    Returns:
        list of dictionaries containing all info about flat
    """
    flats = []

    soup = await post_html_request(url=baseUrl + investLink, session=session)
    try:
        data = eval(f"soup{htmlData['flatTag']}")
    except AttributeError:
        pass
    else:
        for flat in data:
            flats.append({
                'invest_name': investName,
                'floor_number': std.standardize_floor_number(eval(f"flat{htmlData['floorNumber']}"))
                if htmlData['floorNumber'] else None,
                'rooms_number': std.standardize_rooms(eval(f"flat{htmlData['roomsAmount']}")) if htmlData[
                    'roomsAmount'] else None,
                'area': std.standardize_price_and_area(eval(f"flat{htmlData['area']}")) if htmlData[
                    'area'] else None,
                'price': std.standardize_price_and_area(
                    unicodedata.normalize('NFKD', eval(f"flat{htmlData['price']}"))) if htmlData[
                    'price'] else 0,
                'status': std.standardize_status(eval(f"flat{htmlData['status']}")),
                'url': htmlData['baseUrl'] + eval(f"flat{htmlData['url']}")
            })

    return flats


async def get_investment_flats_xpath(investLink: str, investName: str, htmlData: dict,
                                     session: aiohttp.ClientSession, baseUrl) -> list:
    """

    Args:
        baseUrl: if investmentInfo contain links of only query string, you need to add baseUrl
        investName: name of investment
        investLink: link to investment
        session: session used to make async requests
        htmlData: dictionary with strings of code for:
         flatTag - tag in html where new flat is added
         floorNumber - tag containing floor number of flat,
         roomsAmount - tag containing rooms number of flat,
         area - tag containing area of flat,
         price - tag containing price of flat,
         status - tag containing status of flat
    Returns:
        list of dictionaries containing all info about flat
    """
    flats = []

    soup = await get_html_response(url=baseUrl + investLink, session=session)
    soupX = etree.HTML(str(soup[0]))
    try:
        data = eval(f"soupX{htmlData['flatTag']}")
    except AttributeError:
        pass
    else:
        for flat in data:
            flats.append({
                'invest_name': investName,
                'floor_number': std.standardize_floor_number(eval(f"flat{htmlData['floorNumber']}"))
                if htmlData['floorNumber'] else None,
                'rooms_number': std.standardize_rooms(eval(f"flat{htmlData['roomsAmount']}")) if htmlData[
                    'roomsAmount'] else None,
                'area': std.standardize_price_and_area(eval(f"flat{htmlData['area']}")) if htmlData[
                    'area'] else None,
                'price': std.standardize_price_and_area(
                    unicodedata.normalize('NFKD', eval(f"flat{htmlData['price']}"))) if htmlData[
                    'price'] else 0,
                'status': std.standardize_status(eval(f"flat{htmlData['status']}")),
                'url': htmlData['baseUrl'] + eval(f"flat{htmlData['url']}")
            })

    return flats


async def get_investment_flats_from_api(investLink: str, investName: str, htmlData: dict,
                                        session: aiohttp.ClientSession, baseUrl) -> list:
    """

    Args:
        baseUrl: if investmentInfo contain links of only query string, you need to add baseUrl
        investName: name of investment
        investLink: link to investment
        session: session used to make async requests
        htmlData: dictionary with strings of code for:
         flatTag - tag in html where new flat is added
         floorNumber - tag containing floor number of flat,
         roomsAmount - tag containing rooms number of flat,
         area - tag containing area of flat,
         price - tag containing price of flat,
         status - tag containing status of flat
    Returns:
        list of dictionaries containing all info about flat
    """
    flats = []

    data = await get_json_response(url=baseUrl + investLink, session=session)

    for flat in data:
        flats.append({
            'invest_name': investName,
            'floor_number': std.standardize_floor_number(eval(f"flat{htmlData['floorNumber']}"))
            if htmlData['floorNumber'] else None,
            'rooms_number': std.standardize_rooms(eval(f"flat{htmlData['roomsAmount']}")),
            'area': std.standardize_price_and_area(eval(f"flat{htmlData['area']}")) if htmlData['area'] else None,
            'price': std.standardize_price_and_area(
                unicodedata.normalize('NFKD', eval(f"flat{htmlData['price']}"))) if htmlData[
                'price'] else None,
            'status': std.standardize_status(eval(f"flat{htmlData['status']}")),
            'url': htmlData['baseUrl'] + eval(f"flat{htmlData['url']}")
        })

    return flats


async def get_investment_flats_from_api_condition(investLink: str, investName: str, htmlData: dict,
                                                  session: aiohttp.ClientSession, baseUrl) -> list:
    """

    Args:
        baseUrl: if investmentInfo contain links of only query string, you need to add baseUrl
        investName: name of investment
        investLink: link to investment
        session: session used to make async requests
        htmlData: dictionary with strings of code for:
         flatTag - tag in html where new flat is added
         floorNumber - tag containing floor number of flat,
         roomsAmount - tag containing rooms number of flat,
         area - tag containing area of flat,
         price - tag containing price of flat,
         status - tag containing status of flat
    Returns:
        list of dictionaries containing all info about flat
    """
    flats = []
    data = await get_json_response(url=baseUrl + investLink, session=session)

    for flat in eval(f"data{htmlData['dataLocation']}"):
        if eval(htmlData['dataCondition']):
            flats.append({
                'invest_name': investName,
                'floor_number': std.standardize_floor_number(eval(f"flat{htmlData['floorNumber']}"))
                if htmlData['floorNumber'] else None,
                'rooms_number': std.standardize_rooms(eval(f"flat{htmlData['roomsAmount']}")),
                'area': std.standardize_price_and_area(eval(f"flat{htmlData['area']}")) if htmlData[
                    'area'] else None,
                'price': std.standardize_price_and_area(
                    unicodedata.normalize('NFKD', eval(f"flat{htmlData['price']}"))) if htmlData[
                    'price'] else None,
                'status': std.standardize_status(eval(f"flat{htmlData['status']}")),
                'url': htmlData['baseUrl'] + eval(f"flat{htmlData['url']}")
            })

    return flats


async def collect_flats_data(investmentsInfo, htmlDataFlat, function, baseUrl=""):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for investment in investmentsInfo:
            task = asyncio.create_task(
                function(investLink=investment['url'], investName=investment['name'], htmlData=htmlDataFlat,
                         session=session, baseUrl=baseUrl))
            tasks.append(task)
        flats = await asyncio.gather(*tasks)
    return flats


async def collect_investment_data(investmentsInfo, htmlData, function, baseUrl=""):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for investment in investmentsInfo:
            task = asyncio.create_task(
                function(investmentData=investment, htmlData=htmlData, session=session, baseUrl=baseUrl))
            tasks.append(task)
        flats = await asyncio.gather(*tasks)
    return flats


async def collect_flats_with_floors(urls, function):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(
                function(url=url, session=session))
            tasks.append(task)
        flats = await asyncio.gather(*tasks)
    return flats
