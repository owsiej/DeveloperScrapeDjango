import asyncio
from itertools import chain

from .scrape_functions import get_developer_info, get_investment_flats, collect_flats_data

developerName = 'Birkbud'
baseUrl = 'https://www.birkbud.pl/nieruchomosci/'

investmentsInfo = [{'name': 'Apartamenty Sienkiewicza', 'url': 'https://www.birkbud.pl/apartamentysienkiewicza/'},
                   {'name': 'Złote Kaskady', 'url': 'https://www.birkbud.pl/zlotekaskady/'},
                   {'name': 'Rzemieślnicza', 'url': 'https://www.birkbud.pl/rzemieslnicza13/'},
                   {'name': 'Złote Kaskady Etap II', 'url': 'https://www.birkbud.pl/zlote-kaskady3/'}]

flatsHtmlInfo = {'flatTag': ".tbody.find_all('tr')",
                 'floorNumber': ".find(class_='column-1').get_text()",
                 'roomsAmount': ".find(class_='column-4').get_text()",
                 'area': ".find(class_='column-3').get_text().replace('m²', '').replace(',', '.').strip()",
                 'price': '',
                 'status': ".find(class_='column-8').get_text().strip()",
                 'url': ".find(class_='column-7').a['href']",
                 'baseUrl': ""}

investmentsInfo_2 = [{'name': 'Inwestycja Andruszkiewicza', 'url': 'https://www.birkbud.pl/andrukiewicza/'}]

flatsHtmlInfo_2 = {'flatTag': ".tbody.find_all('tr')",
                   'floorNumber': ".find(class_='column-1').get_text()",
                   'roomsAmount': ".find(class_='column-6').get_text()",
                   'area': ".find(class_='column-4').get_text().replace('m²', '').replace(',', '.').strip()",
                   'price': '',
                   'status': ".find(class_='column-8').get_text().strip()",
                   'url': ".find(class_='column-7').a['href']",
                   'baseUrl': ""}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = investmentsInfo + investmentsInfo_2
    return investmentsData


def get_flats_data():
    flatsInfo = list(chain.from_iterable(asyncio.run(
        collect_flats_data(investmentsInfo=investmentsInfo, htmlDataFlat=flatsHtmlInfo,
                           function=get_investment_flats))))
    flatsInfo2 = list(chain.from_iterable(asyncio.run(
        collect_flats_data(investmentsInfo=investmentsInfo_2, htmlDataFlat=flatsHtmlInfo_2,
                           function=get_investment_flats))))
    flatsData = flatsInfo + flatsInfo2
    return flatsData
