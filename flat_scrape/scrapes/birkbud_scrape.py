import asyncio
import re
from itertools import chain
import unicodedata

from .scrape_functions import get_developer_info, get_investment_flats, collect_flats_data, get_developer_investments

developerName = 'Birkbud'
baseUrl = 'https://www.birkbud.pl/nieruchomosci/'

investmentsInfoHtml = {'investmentTag': ".find_all('section', {'data-id': '4aba14b'})",
                       'investmentName': """.find_all("span", style=re.compile(r"^(color: #1a1a1a; font-family: 'Source Serif Pro', serif; font-size: 2em; font-style: normal; font-weight: 600;).*"))""",
                       'investmentLink': '.find_all("a", {"target": "_blank"}, href=re.compile(r"^(?!.*\\b(garaze|lokale)\\b)(https:\/\/www.birkbud.pl\/).*$"))'}

flatsHtmlInfo = {'flatTag': ".tbody.find_all('tr')",
                 'floorNumber': ".find(class_='column-1').get_text()",
                 'roomsAmount': ".find('td', string=re.compile(r'^\d\s*$')).get_text()",
                 'area': ".find(class_='column-3').get_text().replace('m²', '').replace(',', '.').strip() if len(flat.find(class_='column-3').get_text())>1 else flat.find(class_='column-4').get_text().replace('m²', '').replace(',', '.').strip()",
                 'price': '',
                 'status': ".find(class_='column-8').get_text().strip()",
                 'url': ".find(class_='column-7').a['href']",
                 'baseUrl': ""}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = get_developer_investments(baseUrl, investmentsInfoHtml)
    newNames = list(dict.fromkeys(
        map(lambda x: x.get_text(strip=True).replace("Białystok", "").replace("”", " ").replace("„", "").replace(",",
                                                                                                                 "").replace(
            "  ", " ").strip(),
            investmentsData[0]['name'])))
    newUrls = list(map(lambda x: x['href'], investmentsData[0]['url']))
    formattedNames = newNames.copy()
    for i in range(0, len(newNames)):
        if re.search(r"^(?!ul.)([a-z])", newNames[i]):
            formattedNames[i - 1] += formattedNames[i]
            formattedNames.pop(i)
    formattedInvestmentsData = [{"name": unicodedata.normalize("NFKD", name),
                                 "url": url}
                                for name, url in zip(formattedNames, newUrls)]
    return formattedInvestmentsData


def get_flats_data():
    investmentsData = get_investments_data()
    flatsInfo = list(chain.from_iterable(asyncio.run(
        collect_flats_data(investmentsInfo=investmentsData, htmlDataFlat=flatsHtmlInfo,
                           function=get_investment_flats))))
    flatsData = flatsInfo
    return flatsData
