from .scrape_functions import get_developer_info, get_developer_investments, \
    get_investment_flats_from_api_condition

developerName = 'Rutkowski Development'
baseUrl = 'https://rutkowskidevelopment.pl/oferta/'
apiUrls = ['https://rutkowskidevelopment.pl/wp-content/themes/hubdab_starter/api.json']

investmentHtmlInfo = {
    'investmentTag': ".find('li', id='menu-item-12').find_all('a', class_='dropdown-item')",
    'investmentName': "['title']",
    'investmentLink': "['href']"}

flatsHtmlInfo = {'dataLocation': "['lokale']",
                 'dataCondition': "flat['osiedle'] == investment['name'] and flat['typ'] == 'Mieszkanie'",
                 'floorNumber': "['pietro']",
                 'roomsAmount': "['liczba_pokoi']",
                 'area': "['powierzchnia']",
                 'price': "",
                 'status': "['status']"}


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
    flatsData = get_investment_flats_from_api_condition(investmentsApiInfo, flatsHtmlInfo)
    return flatsData
