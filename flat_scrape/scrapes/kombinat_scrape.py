import asyncio
from itertools import chain

from .scrape_functions import get_developer_info, get_developer_investments, \
    get_all_buildings_from_investment, \
    get_investment_flats, collect_investment_data, collect_flats_data

developerName = 'Kombinat Budowlany'
baseUrl = 'https://www.kombinatbud.com.pl'
baseTag = '/Oferta/Inwestycje'

investmentsHtmlInfo = {'investmentTag': ".find(class_='covers').find_all('a')",
                       'investmentName': ".find('h3').get_text()",
                       'investmentLink': "['href']"}

investmentBuildingsHtmlInfo = {'buildingTag': ".find_all(class_='button w-100', attrs={'href': re.compile(r'\B/.*')})",
                               'buildingName': "['name'] + ' ' + building.get_text().strip()",
                               'buildingLink': "['href']"}

flatsRestHtmlInfo = {'flatTag': ".tbody.select('tr')",
                     'floorNumber': ".find(class_='desktop').get_text()",
                     'roomsAmount': ".find(class_='desktop').find_next_sibling().get_text()",
                     'area': ".find(class_='desktop').find_next_sibling().find_next_sibling().get_text()"
                             ".replace('m²','').replace(',','.')",
                     'price': ".find(class_='text-danger').find_next_sibling('b').get_text()"
                              ".replace('PLN', '').replace(' ', '').strip() if flat.find(class_='text-danger') else "
                              "flat.find(class_='desktop').find_next_sibling().find_next_sibling().find_next_sibling()"
                              ".get_text().replace('PLN', '').strip()",
                     'status': ".get('title')",
                     'url': ".td.text.split()[-1]",
                     'baseUrl': "/M/"
                     }


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsInfo = get_developer_investments(baseUrl + baseTag, investmentsHtmlInfo)
    buildingsInfo = list(chain.from_iterable(asyncio.run(
        collect_investment_data(investmentsInfo=investmentsInfo, htmlData=investmentBuildingsHtmlInfo, baseUrl=baseUrl,
                                function=get_all_buildings_from_investment))))
    return buildingsInfo


def get_flats_data():
    investmentsData = get_investments_data()

    flatsRestInfo = list(chain.from_iterable(
        asyncio.run(collect_flats_data(investmentsInfo=investmentsData, htmlDataFlat=flatsRestHtmlInfo,
                                       function=get_investment_flats))))
    flatsData = flatsRestInfo

    for flat in flatsData:
        for invest in investmentsData:
            if flat['invest_name'] == invest['name']:
                flat['url'] = invest['url'].replace("/L/", "/") + flat['url']

    return flatsData
