from .scrape_functions import get_developer_info, get_developer_investments, get_new_page_links, \
    get_investment_flats

developerName = 'Jaz-Bud'

baseUrl = 'https://www.jaz-bud.pl'
cityTag = '/bialystok'

investmentHtmlInfo = {'investmentTag': ".find('ul', class_='uk-nav uk-navbar-dropdown-nav').find_all('li')",
                      'investmentName': ".get_text()",
                      'investmentLink': ".a['href']"}

newPageHtmlPage = {'nextPageTag': ".find('a', title='następna')",
                   'nextPageLink': "['href']"}

flatsHtmlInfo = {'flatTag': ".tbody.find_all('tr')",
                 'floorNumber': ".find_all('td')[3].span",
                 'roomsAmount': ".find_all('td')[4].span.get_text()",
                 'area': ".find_all('td')[2].span.get_text().replace('m2','')",
                 'price': ".find_all('td')[5].div.get_text().strip().replace('zł','')",
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
    investmentsFinalInfo = get_new_page_links(investmentsInfo, newPageHtmlPage, baseUrl)
    flatsData = get_investment_flats(investmentsFinalInfo, flatsHtmlInfo, baseUrl)
    return flatsData
