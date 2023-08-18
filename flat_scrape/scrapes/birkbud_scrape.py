from .scrape_functions import get_developer_info, get_investment_flats

developerName = 'Birkbud'
baseUrl = 'https://www.birkbud.pl/nieruchomosci/'

investmentsInfo = [{'name': 'Apartamenty Sienkiewicza', 'url': 'https://www.birkbud.pl/apartamentysienkiewicza/'},
                   {'name': 'Złote Kaskady', 'url': 'https://www.birkbud.pl/zlotekaskady/'},
                   {'name': 'Rzemieślnicza', 'url': 'https://www.birkbud.pl/rzemieslnicza13/'}]

flatsHtmlInfo = {'flatTag': ".tbody.find_all('tr')",
                 'floorNumber': ".find(class_='column-1').get_text()",
                 'roomsAmount': ".find(class_='column-4').get_text()",
                 'area': ".find(class_='column-3').get_text().replace('m²', '').replace(',', '.').strip()",
                 'price': '',
                 'status': ".find(class_='column-8').get_text().strip()"}

investmentsInfo_2 = [{'name': 'Inwestycja Andruszkiewicza', 'url': 'https://www.birkbud.pl/andrukiewicza/'}]

flatsHtmlInfo_2 = {'flatTag': ".tbody.find_all('tr')",
                   'floorNumber': ".find(class_='column-1').get_text()",
                   'roomsAmount': ".find(class_='column-6').get_text()",
                   'area': ".find(class_='column-4').get_text().replace('m²', '').replace(',', '.').strip()",
                   'price': '',
                   'status': ".find(class_='column-8').get_text().strip()"}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = investmentsInfo + investmentsInfo_2
    return investmentsData


def get_flats_data():
    flatsInfo = get_investment_flats(investmentsInfo, flatsHtmlInfo)
    flatsInfo2 = get_investment_flats(investmentsInfo_2, flatsHtmlInfo_2)
    flatsData = flatsInfo + flatsInfo2
    return flatsData
