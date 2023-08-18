from .scrape_functions import get_developer_info, get_investment_flats

developerName = 'Kamienica Butikowa'
baseUrl = 'https://www.butikowa-kamienica.pl/apartamenty.html'

investmentsInfo = [{'name': 'Kamienica Butikowa', 'url': 'https://www.butikowa-kamienica.pl/apartamenty.html'}]

flatsHtmlInfo = {'flatTag': ".find(class_='ps550 v37 s495 z472').find_all('div', {'data-popup-group': '0'})",
                 'floorNumber': "",
                 'roomsAmount': ".p.find_next_sibling().get_text().split()[2]",
                 'area': ".p.find_next_sibling().find_next_sibling().get_text().split()[1]"
                         ".replace('m2', '').replace(',','.').strip()",
                 'price': "",
                 'status': ".p.find_next_sibling().find_next_sibling().find_next_sibling().get_text().split()[1]"}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = investmentsInfo
    return investmentsData


def get_flats_data():
    flatsData = get_investment_flats(investmentsInfo, flatsHtmlInfo)
    return flatsData
