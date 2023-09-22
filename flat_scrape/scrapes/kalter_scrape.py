from itertools import chain
import asyncio

from .scrape_functions import get_developer_info, get_investment_flats, collect_flats_data, get_developer_investments

developerName = 'Kalter Nieruchomości'
baseUrl = 'https://www.kalternieruchomosci.pl/pl/oferta-mieszkan'

investmentHtmlInfo = {'investmentTag': ".find_all('span', text='Białystok')",
                      'investmentName': ".parent.next_sibling.next_sibling.h2.get_text().title()",
                      'investmentLink': ".parent.parent.get('href')"}

flatsHtmlInfo = {
    'flatTag': ".find('div', id='offerList').find_all('div', class_=re.compile('col-12 col-list'), attrs={'data-url':re.compile('M\d+$')})",
    'floorNumber': ".find('li', class_='li-inwest-rwd').span.get_text()",
    'roomsAmount': ".li.span.get_text()",
    'area': ".find('li', class_='li-inwest-rwd').find_previous_sibling().span.get_text().replace('m2', '').strip().replace(',', '.')",
    'price': "",
    'status': ".find('div', class_='col text-center').get_text().strip()"}


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
