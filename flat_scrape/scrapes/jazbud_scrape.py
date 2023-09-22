from itertools import chain
import asyncio

from .scrape_functions import get_developer_info, get_developer_investments, get_new_page_links, \
    get_investment_flats, collect_flats_data, collect_investment_data

developerName = 'Jaz-Bud'

baseUrl = 'https://www.jaz-bud.pl'
cityTag = '/bialystok'

investmentHtmlInfo = {'investmentTag': ".find('ul', class_='uk-nav uk-navbar-dropdown-nav').find_all('li')",
                      'investmentName': ".get_text()",
                      'investmentLink': ".a['href']"}

newPageHtmlPage = {'nextPageTag': ".find('a', title='następna')",
                   'nextPageLink': "['href']"}

flatsHtmlInfo = {'flatTag': ".tbody.find_all('tr')",
                 'floorNumber': ".find('td', {'data-order':re.compile('^piętro')}).span.get_text(strip=True) if flat.find('td', {'data-order':re.compile('^piętro')}) else None",
                 'roomsAmount': ".find('td', {'data-order':re.compile('^pokoje')}).span.get_text(strip=True)  if flat.find('td', {'data-order':re.compile('^pokoje')}) else None",
                 'area': ".find('td', {'data-order':re.compile('^powierzchnia')}).span.get_text(strip=True).replace('m2','')  if flat.find('td', {'data-order':re.compile('^powierzchnia')}) else None",
                 'price': ".find('td', {'data-order':re.compile('^[0-9]')}).div.get_text(strip=True).replace('zł', '') if flat.find('td', {'data-order':re.compile('^[0-9]')}) else None",
                 'status': ""}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsInfo = get_developer_investments(baseUrl, investmentHtmlInfo)
    investmentsData = list(map(lambda item: {
        'name': item['name'],
        'url': baseUrl + item['url']
    }, investmentsInfo))
    return investmentsData


def get_flats_data():
    investmentsInfo = get_investments_data()

    investmentsFinalInfo = list(chain.from_iterable(asyncio.run(
        collect_investment_data(investmentsInfo=investmentsInfo, htmlData=newPageHtmlPage, baseUrl=baseUrl,
                                function=get_new_page_links))))
    flatsData = list(chain.from_iterable(asyncio.run(
        collect_flats_data(investmentsInfo=investmentsFinalInfo, htmlDataFlat=flatsHtmlInfo,
                           function=get_investment_flats))))
    return flatsData
