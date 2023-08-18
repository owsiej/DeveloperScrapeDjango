from .scrape_functions import get_developer_info, get_investment_flats_from_api

developerName = 'Panorama Park'
baseUrl = 'http://panoramabialystok.pl/'
apiUrl = 'http://panoramabialystok.pl/wp-admin/admin-ajax.php' \
         '?action=wp_ajax_ninja_tables_public_action&table_id=912&target_action=get-all-data' \
         '&default_sorting=manual_sort'

investmentsInfo = [{
    'name': 'Panorama Park',
    'url': f"{baseUrl}"
}]

investmentsApiInfo = [{
    'name': 'Panorama Park',
    'url': f"{apiUrl}"
}]

flatsHtmlInfo = {'floorNumber': "['value']['545']",
                 'roomsAmount': "['value']['pokoje']",
                 'area': "['value']['powierzchnia'].replace('mkw.', '').strip().replace(',', '.')",
                 'price': "['value']['cena']",
                 'status': "['value']['status']"}


def get_developer_data():
    developerData = get_developer_info(developerName, baseUrl)
    return developerData


def get_investments_data():
    investmentsData = investmentsInfo
    return investmentsData


def get_flats_data():
    flatsData = get_investment_flats_from_api(investmentsApiInfo, flatsHtmlInfo)
    return flatsData