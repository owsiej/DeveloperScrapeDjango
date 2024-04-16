import asyncio
from itertools import chain

from .scrape_functions import get_developer_info, get_investment_flats_xpath, collect_flats_data

developerName = 'Kamienica Butikowa'
baseUrl = 'https://www.butikowa-kamienica.pl/apartamenty.html'

investmentsInfo = [{'name': 'Kamienica Butikowa Kijowska', 'url': 'https://www.butikowa-kamienica.pl/apartamenty.html'}]

flatsHtmlInfo = {
    'flatTag': """.xpath("//div[(@class='v1 ps7 s141') or (@class='v1 ps15 s210')]//div[contains(@id,'popup')]")""",
    'floorNumber': ".xpath('./div/p[5]/a/@href')[0].split('_')[-1][1]",
    'roomsAmount': ".xpath('./div/p[2]/text()')[0].strip().split()[-1]",
    'area': ".xpath('./div/p[3]/text()')[0].split()[1].replace(',', '.').replace('.m','')",
    'price': "",
    'status': ".xpath('./div/p[4]/text()')[0].split()[-1]",
    'url': ".xpath('./div/p[6]/a/@href')[0]",
    'baseUrl': "https://www.butikowa-kamienica.pl/"}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = investmentsInfo
    return investmentsData


def get_flats_data():
    flatsData = list(chain.from_iterable(asyncio.run(
        collect_flats_data(investmentsInfo=investmentsInfo, htmlDataFlat=flatsHtmlInfo,
                           function=get_investment_flats_xpath))))

    return flatsData
