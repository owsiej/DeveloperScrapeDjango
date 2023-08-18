from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from django.http import HttpResponse
from django.db.models import Q
import pandas as pd
import io
from UliPlot.XLSX import auto_adjust_xlsx_column_width
from itertools import groupby

from .models import Developer, Investment, Flat
from .forms import FlatForm


# Create your views here.

class DeveloperList(ListView):
    model = Developer
    context_object_name = "developer_list"


class InvestmentList(ListView):
    model = Investment
    context_object_name = "investment_list"
    template_name = "flat_browser/find_flat.html"

    def get_queryset(self):
        if FlatFormView.was_dev_chosen is True:
            return Investment.objects.filter(developer__in=dict(self.request.GET)['dev'])
        if FlatFormView.was_dev_chosen is False:
            return Investment.objects.all()


class FlatList(ListView):
    model = Flat
    context_object_name = "flat_list"
    flat_list = []

    def get_queryset(self):
        investments = self.request.session['invest']
        flats = self.request.session['flat_filter']
        result_query = Flat.objects.filter(
            Q(floor__range=(flats['floor_gte'], flats['floor_lte'])) | Q(floor__isnull=True),
            Q(rooms__range=(flats['rooms_gte'], flats['rooms_lte'])) | Q(rooms__isnull=True),
            Q(price__range=(flats['price_gte'], flats['price_lte'])) | Q(price__isnull=True),
            Q(area__range=(flats['area_gte'], flats['area_lte'])) | Q(area__isnull=True),
            status__in=flats['status'],
            investment__in=investments).order_by("developer__name", "investment__name", "status", "area")
        FlatList.flat_list = result_query
        return result_query


class FlatFormView(FormView):
    template_name = "flat_browser/find_flat.html"
    form_class = FlatForm
    success_url = reverse_lazy("flat_browser:flat")
    was_dev_chosen = None

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('dev'):
            FlatFormView.was_dev_chosen = True
        else:
            FlatFormView.was_dev_chosen = False
        if request.GET and not request.GET.get('dev'):
            form = FlatForm(request.GET)
            if form.is_valid():
                form_data = form.cleaned_data
                if request.GET.get('invest'):
                    request.session['invest'] = dict(request.GET)['invest']
                request.session['flat_filter'] = form_data
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:

            return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['investment_list'] = InvestmentList.get_queryset(self)
        invest_ids = list(map(lambda x: x.id, context['investment_list']))
        self.request.session['invest'] = invest_ids
        return context


def export_excel_file(request):
    query_flats = list(FlatList.flat_list.values("investment__name",
                                                 "developer__name",
                                                 "floor",
                                                 "rooms",
                                                 "area",
                                                 "price",
                                                 "status",
                                                 "url",
                                                 "insertion_date").order_by("developer__name"))
    sorted_flats = [{x: list(y)}
                    for x, y in groupby(query_flats, lambda z: z['developer__name'])]

    dev_names = list(map(lambda x: str(*x.keys()), sorted_flats))
    dataframes = [pd.DataFrame(items[1])
                  for flat in sorted_flats
                  for items in flat.items()
                  ]
    memory_file = io.BytesIO()
    with pd.ExcelWriter(memory_file, engine="openpyxl") as writer:
        for name, df in zip(dev_names, dataframes):
            df.to_excel(writer, name)
            auto_adjust_xlsx_column_width(df, writer, sheet_name=name, margin=1)
    memory_file.seek(0)

    response = HttpResponse(memory_file,
                            headers={
                                "Content_Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                "Content-Disposition": 'attachment; filename="foo.xls"'
                            })
    return response
