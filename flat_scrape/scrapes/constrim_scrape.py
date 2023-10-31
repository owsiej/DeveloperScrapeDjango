import asyncio
from itertools import chain

from .scrape_functions import get_developer_info, get_developer_investments, \
    get_investment_flats_from_api_condition, collect_flats_data

developerName = 'Constrim'
baseUrl = 'https://conhouse.com.pl/'
apiUrls = [
    'https://smart-makieta-3destate-embed.azureedge.net/assets/5b306c4f-895e-434b-9913-c70550fc4f73/app.config.json',
    'https://smart-makieta-3destate-embed.azureedge.net/assets/6a56c6d7-ba7f-4348-a4c9-951768b7ef72/app.config.json']

investmentHtmlInfo = {
    'investmentTag': ".find('ul', class_='sub-menu').find_all('a')",
    'investmentName': ".get_text(strip=True)",
    'investmentLink': "['href']"}

flatsHtmlInfo = {'dataLocation': "['flats']",
                 'dataCondition': "flat['custom']['type']=='apartment'",
                 'floorNumber': "['floor']",
                 'roomsAmount': "['rooms']",
                 'area': "['area']",
                 'price': "",
                 'status': "['availability']",
                 'url': "['flatFile']",
                 'baseUrl': ""}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = get_developer_investments(baseUrl, investmentHtmlInfo)
    return investmentsData


def get_flats_data():
    investmentsInfo = get_investments_data()
    investmentsApiInfo = [{
        'name': name['name'],
        'url': link}
        for name, link in zip(investmentsInfo, apiUrls)]
    flatsData = list(chain.from_iterable(
        asyncio.run(collect_flats_data(investmentsInfo=investmentsApiInfo, htmlDataFlat=flatsHtmlInfo,
                                       function=get_investment_flats_from_api_condition))))
    for flat in flatsData:
        for invest in investmentsApiInfo:
            if flat['invest_name'] == invest['name']:
                flat['url'] = invest['url'][:-16] + flat['url']

    return flatsData
