import requests
import asyncio
from itertools import chain
from bs4 import BeautifulSoup

from .scrape_functions import get_developer_info, get_investment_flats_post, collect_flats_data

developerName = 'Asko S.A.'
baseUrl = 'https://askosa.pl/'

investmentsInfo = [{'name': 'Apartamenty Ciepła 38', 'url': 'https://askosa.pl/inwestycje/apartamenty-ciepla-38/'}]

flatsHtmlInfo = {'flatTag': ".tbody.find_all('tr')",
                 'floorNumber': ".find_all('td')[4].get_text(strip=True)",
                 'roomsAmount': ".find_all('td')[5].get_text(strip=True)",
                 'area': ".find_all('td')[3].get_text(strip=True)",
                 'price': ".find_all('td')[7].get_text().replace(' zł', '')",
                 'status': ".find_all('td')[-4].get_text(strip=True)",
                 'url': ".find_all('td')[-1].a['href']",
                 'baseUrl': ''}


def get_all_pages_with_flats(investsData):
    urls = []

    for investment in investsData:
        response = requests.get(investment['url'])
        soup = BeautifulSoup(response.text, "html.parser")

        data = soup.find("div", class_="pagination").find_all("a", class_="page-numbers")
        basePaginationUrl = data[-2]['href'][:-3]
        lastPageNumber = data[-2]['href'][-3:-1]

        for i in range(1, int(lastPageNumber) + 1):
            urls.append({'name': investment['name'],
                         'url': basePaginationUrl + str(i)})
    return urls


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = investmentsInfo
    return investmentsData


def get_flats_data():
    investmentsData = get_all_pages_with_flats(investmentsInfo)
    flatsData = list(chain.from_iterable(asyncio.run(
        collect_flats_data(investmentsInfo=investmentsData, htmlDataFlat=flatsHtmlInfo,
                           function=get_investment_flats_post))))
    return flatsData
