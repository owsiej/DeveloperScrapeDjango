from itertools import chain
import asyncio

from .scrape_functions import get_developer_info, get_developer_investments, collect_flats_data, get_investment_flats

developerName = 'Rogowski Development'
baseUrl = 'https://www.rogowskidevelopment.pl'

investmentHtmlInfo = {
    'investmentTag': """.find_all('div', class_='offer-box-location', string='Białystok')""",
    'investmentName': ".find_parent('a')['href'].replace('/Oferta/', '').replace('#szczegoly', '').replace('_', ' ').title()",
    'investmentLink': ".find_parent('a')['href']"}

flatsHtmlInfo = {
    'flatTag': ".find('tbody').find_all('tr')",
    'floorNumber': ".td.get_text().strip().split('\\n')[1].replace('Piętro: ', '')",
    'roomsAmount': ".td.get_text().strip().split('\\n')[2].replace('Pokoje: ', '') if len(flat.td.get_text().strip().split('\\n')) == 3 else ''",
    'area': ".td.find_next_sibling().get_text().replace('m²', '').replace(',','.')",
    'price': ".td.find_next_sibling().find_next_sibling().get_text().strip().split('\\n')[0].replace('PLN', '').replace(' ', '')",
    'status': ".td.find_next_sibling().find_next_sibling().get_text().strip().split('\\n')[-1].strip()",
    'url': "",
    "baseUrl": ""}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsLinks = list(map(lambda item: {
        'name': item['name'],
        'url': baseUrl + item['url']
    }, list(filter(lambda x: x['name'] not in ['Gotowe Lokale Uslugowe', 'Hbh Apartamenty'],
                   get_developer_investments(baseUrl, investmentHtmlInfo)))))

    return investmentsLinks


def get_flats_data():
    investmentsData = get_investments_data()
    flatsInfo = list(chain.from_iterable(asyncio.run(
        collect_flats_data(investmentsInfo=investmentsData, htmlDataFlat=flatsHtmlInfo,
                           function=get_investment_flats))))
    flatsData = flatsInfo
    return flatsData
