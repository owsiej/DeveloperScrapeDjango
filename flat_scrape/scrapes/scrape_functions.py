import requests
from bs4 import BeautifulSoup
from itertools import chain
from . import standardize_flat_info as std
import unicodedata
import re


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
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    data = eval(f"soup{htmlData['investmentTag']}")

    for item in data:
        developerInvestments.append({"name": eval(f"item{htmlData['investmentName']}"),
                                     "url": eval(f"item{htmlData['investmentLink']}")})

    return developerInvestments


def get_new_page_links(investInfo, htmlData, baseUrl=''):
    """
    If investment on page with flats has got button "Next Page" then this function gets all links of new pages
    to later scrape from them.
    Args:
        baseUrl: url to developer page
        investInfo: list of dicts with investments and link to them
        htmlData: dictionary with string of code for:
            nextPageTag - tag containing next Page Button
            nextPageLink - tag to link by itself

    Returns:
        final list of dict with all investments and links to them
    """
    investmentsFinalInfo = []
    for investment in investInfo:
        response = requests.get(baseUrl + investment['url'])
        soup = BeautifulSoup(response.text, "html.parser")
        while True:
            nextPage = eval(f"soup{htmlData['nextPageTag']}")

            if nextPage is not None:
                investmentsFinalInfo.append({'name': investment['name'],
                                             'url': eval(f"nextPage{htmlData['nextPageLink']}")})
                response = requests.get(baseUrl + investmentsFinalInfo[-1]['url'])
                soup = BeautifulSoup(response.text, "html.parser")
            else:
                break
    return sorted(list(chain.from_iterable(zip(investmentsFinalInfo, investInfo))), key=lambda key: key['name'])


def get_all_buildings_from_investment(investsInfo, htmlData, baseUrl=''):
    """get names of all investments with links to them

    Args:
        htmlData: dict of tags needed to scrape for buildings
        baseUrl: url of developer site
        investsInfo(list): list of dict of investments names and links to them from which we gonna get buildings
    Returns:
        list of whole need data
    """

    listOfBuildings = []

    for investment in investsInfo:
        response = requests.get(f"{baseUrl}{investment['url']}")
        soup = BeautifulSoup(response.text, "html.parser")

        buildings = eval(f"soup{htmlData['buildingTag']}")
        if buildings:
            for building in buildings:
                listOfBuildings.append({'name': eval(f"investment{htmlData['buildingName']}"),
                                        'url': eval(f"building{htmlData['buildingLink']}")})
        else:
            listOfBuildings.append(investment)
    return listOfBuildings


def get_investment_flats(investmentInfo: list, htmlData: dict, baseUrl='') -> list:
    """

    Args:
        baseUrl: if investmentInfo contain links of only query string, you need to add baseUrl
        investmentInfo: list with infos about investment (return of get_developer_investments)
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    for investment in investmentInfo:
        response = requests.get(f"{baseUrl}{investment['url']}", headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            data = eval(f"soup{htmlData['flatTag']}")
        except AttributeError:
            pass
        else:
            for flat in data:
                flats.append({
                    'invest_name': investment['name'],
                    'floor_number': std.standardize_floor_number(eval(f"flat{htmlData['floorNumber']}"))
                    if htmlData['floorNumber'] else None,
                    'rooms_number': std.standardize_rooms(eval(f"flat{htmlData['roomsAmount']}")),
                    'area': std.standardize_price_and_area(eval(f"flat{htmlData['area']}")) if htmlData[
                        'area'] else None,
                    'price': std.standardize_price_and_area(
                        unicodedata.normalize('NFKD', eval(f"flat{htmlData['price']}"))) if htmlData[
                        'price'] else 0,
                    'status': std.standardize_status(eval(f"flat{htmlData['status']}"))
                })

    return flats


def get_investment_flats_from_api(investmentInfo: list, htmlData: dict, baseUrl='') -> list:
    """

    Args:
        baseUrl: if investmentInfo contain links of only query string, you need to add baseUrl
        investmentInfo: list with infos about investment (return of get_developer_investments)
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

    for investment in investmentInfo:
        response = requests.get(f"{baseUrl}{investment['url']}")
        data = response.json()

        for flat in data:
            flats.append({
                'invest_name': investment['name'],
                'floor_number': std.standardize_floor_number(eval(f"flat{htmlData['floorNumber']}"))
                if htmlData['floorNumber'] else None,
                'rooms_number': std.standardize_rooms(eval(f"flat{htmlData['roomsAmount']}")),
                'area': std.standardize_price_and_area(eval(f"flat{htmlData['area']}")) if htmlData['area'] else None,
                'price': std.standardize_price_and_area(
                    unicodedata.normalize('NFKD', eval(f"flat{htmlData['price']}"))) if htmlData[
                    'price'] else None,
                'status': std.standardize_status(eval(f"flat{htmlData['status']}"))
            })

    return flats


def get_investment_flats_from_api_condition(investmentInfo, htmlData: dict) -> list:
    """

    Args:
        baseUrl: if investmentInfo contain links of only query string, you need to add baseUrl
        investmentInfo: list with infos about investment (return of get_developer_investments)
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
    for investment in investmentInfo:
        response = requests.get(f"{investment['url']}")
        data = response.json()

        for flat in eval(f"data{htmlData['dataLocation']}"):
            if eval(htmlData['dataCondition']):
                flats.append({
                    'invest_name': investment['name'],
                    'floor_number': std.standardize_floor_number(eval(f"flat{htmlData['floorNumber']}"))
                    if htmlData['floorNumber'] else None,
                    'rooms_number': std.standardize_rooms(eval(f"flat{htmlData['roomsAmount']}")),
                    'area': std.standardize_price_and_area(eval(f"flat{htmlData['area']}")) if htmlData[
                        'area'] else None,
                    'price': std.standardize_price_and_area(
                        unicodedata.normalize('NFKD', eval(f"flat{htmlData['price']}"))) if htmlData[
                        'price'] else None,
                    'status': std.standardize_status(eval(f"flat{htmlData['status']}"))
                })

    return flats
