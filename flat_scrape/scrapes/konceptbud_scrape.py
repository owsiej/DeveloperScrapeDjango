from itertools import chain
import asyncio

from .scrape_functions import get_developer_info, get_investment_flats, collect_flats_data, get_developer_investments

developerName = 'Konceptbud Development'
baseUrl = 'https://konceptbuddevelopment.pl/'

investmentHtmlInfo = {'investmentTag': ".nav.ul.find_all('li', class_='menu-item-object-property-item')",
                      'investmentName': ".span.get_text()",
                      'investmentLink': ".a['href']"}

flatsHtmlInfo = {
    'flatTag': ".find_all('article')",
    'floorNumber': "",
    'roomsAmount': ".find_all('td')[3].get_text()",
    'area': ".find_all('td')[1].get_text().replace('m2', '').strip()",
    'price': ".find_all('td')[2].get_text().replace('zł', '').strip()",
    'status': ".find_all('td')[4].get_text()",
    'url': ".find_all('td')[5].a['href']",
    'baseUrl': ""}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = get_developer_investments(url=baseUrl, htmlData=investmentHtmlInfo)
    return investmentsData


def get_flats_data():
    flatsData = list(chain.from_iterable(asyncio.run(
        collect_flats_data(investmentsInfo=get_investments_data(), htmlDataFlat=flatsHtmlInfo,
                           function=get_investment_flats))))
    return flatsData
