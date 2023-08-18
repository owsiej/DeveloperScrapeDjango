from django.shortcuts import render

from . import scrapes


# Create your views here.


def get_developer_info_from_scrape():
    attrs = list(filter(lambda x: not x.startswith("__") and x.endswith("_scrape"), dir(scrapes)))
    return [{"attr": attr,
             "data": getattr(scrapes, attr).get_developer_data()}
            for attr in attrs]


def get_developer_invests_info_from_scrape(attr):
    return getattr(scrapes, attr).get_investments_data()


def get_flats_from_scrape(attr):
    return getattr(scrapes, attr).get_flats_data()
