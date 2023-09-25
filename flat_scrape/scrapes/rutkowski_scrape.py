from itertools import chain
import asyncio

from .scrape_functions import get_developer_info, get_developer_investments, \
    get_investment_flats_from_api_condition, collect_flats_data

developerName = 'Rutkowski Development'
baseUrl = 'https://rutkowskidevelopment.pl/oferta/'
apiUrls = ['https://rutkowskidevelopment.pl/wp-content/themes/hubdab_starter/api.json']

investmentHtmlInfo = {
    'investmentTag': ".find('li', id='menu-item-12').find_all('a', class_='dropdown-item')",
    'investmentName': "['title']",
    'investmentLink': "['href']"}

flatsHtmlInfo = {'dataLocation': "['lokale']",
                 'dataCondition': "flat['osiedle'] == investName and flat['typ'] == 'Mieszkanie'",
                 'floorNumber': "['pietro']",
                 'roomsAmount': "['liczba_pokoi']",
                 'area': "['powierzchnia']",
                 'price': "",
                 'status': "['status']",
                 'url': "['FullNumber'].replace('Duo Apartamenty', '').strip().replace(' ', '-').lower()",
                 'baseUrl': "https://rutkowskidevelopment.pl/oferty/duo-apartamenty-"}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = get_developer_investments(baseUrl, investmentHtmlInfo)
    return investmentsData


def get_flats_data():
    investmentsData = get_investments_data()
    investmentsApiInfo = [{
        'name': name['name'],
        'url': link}
        for name, link in zip(investmentsData, apiUrls)]

    flatsData = list(chain.from_iterable(
        asyncio.run(collect_flats_data(investmentsInfo=investmentsApiInfo, htmlDataFlat=flatsHtmlInfo,
                                       function=get_investment_flats_from_api_condition))))
    return flatsData
