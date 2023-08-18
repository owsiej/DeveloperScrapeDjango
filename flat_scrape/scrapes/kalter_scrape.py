from .scrape_functions import get_developer_info, get_investment_flats

developerName = 'Kalter Nieruchomości'
baseUrl = 'https://www.kalternieruchomosci.pl/pl/oferta-mieszkan'

investmentsInfo = [{'name': 'Słonimska Residence', 'url': "https://www.kalternieruchomosci.pl/pl/wyniki-wyszukiwania"
                                                          "?s_city=1&s_inwest=&s_typ=&s_status=&s_pokoje=&s_metry="
                                                          "&s_aneks=&s_garden=0&s_deck=0&a=szukaj"}]

flatsHtmlInfo = {'flatTag': ".find('div', id='offerList').find_all('div', class_='col-12 col-list dostepny-list')",
                 'floorNumber': ".find('li', class_='li-inwest-rwd').span.get_text()",
                 'roomsAmount': ".li.span.get_text()",
                 'area': ".li.span.find_next('span').get_text().replace('m2', '').strip().replace(',', '.')",
                 'price': "",
                 'status': ".find('div', class_='col text-center').get_text().strip()"}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = investmentsInfo
    return investmentsData


def get_flats_data():
    flatsData = get_investment_flats(investmentsInfo, flatsHtmlInfo)
    return flatsData
