import re


def standardize_status(status):
    statusNamesSold = ['sprzedane', 'sold', 3]
    statusNamesFree = ['dostępne', 'free', 'wolne', 'available', 1]
    statusNamesReserved = ['rezerwacja', 'reserved',
                           'mieszkanie jest zarezerwowane. prosimy o kontakt z działem sprzedaży.', 2, "zarezerwowane"]

    try:
        if status.lower() in statusNamesSold:
            return 'sprzedane'
        if status.lower() in statusNamesFree:
            return 'wolne'
        if status.lower() in statusNamesReserved:
            return 'zarezerwowane'
    except TypeError:
        return 'wolne'
    except AttributeError:
        if status in statusNamesSold:
            return 'sprzedane'
        if status in statusNamesFree:
            return 'wolne'
        if status in statusNamesReserved:
            return 'zarezerwowane'
    return 'wolne'


def standardize_floor_number(number):
    try:
        if number:
            return int(number)
        else:
            return None
    except (ValueError, TypeError):
        if re.fullmatch(r"^<span>\d{1,}</span>?", str(number)):
            return int(re.search(r"\d{1,2}", str(number)).group())
        if number.lower() == 'parter':
            return 0
        if 'i' in number.lower().strip(' '):
            return 1
        if 'ii' in number.lower().strip(' '):
            return 2
        if 'iii' in number.lower().strip(' '):
            return 3
        if 'iv' in number.lower().strip(' '):
            return 4
        if 'v' in number.lower().strip(' '):
            return 5
        if 'vi' in number.lower().strip(' '):
            return 6


def standardize_price_and_area(key):
    if key == '0':
        return 0
    if isinstance(key, (float, int)):
        return float(key)
    try:
        return float(key.replace(" ", ''))
    except (ValueError, TypeError):
        return None


def standardize_rooms(key):
    try:
        return int(key)
    except ValueError:
        return None
