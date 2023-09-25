from django.contrib import admin
from django import forms
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils.translation import gettext

from . import models

from flat_scrape.views import get_developer_info_from_scrape, get_developer_invests_info_from_scrape, \
    get_flats_from_scrape


# Register your models here.


def get_devs_to_add(dev_data):
    return [
        (x['data']['name'], x['data']['name'])
        for x in dev_data
        if x['data']['name'] not in list(models.Developer.objects.values_list('name', flat=True).all())
    ]


class DeveloperAdminAdd(forms.ModelForm):
    dev_data = get_developer_info_from_scrape()
    dev_names = get_devs_to_add(dev_data)
    name = forms.CharField(widget=forms.Select(choices=dev_names))
    url = forms.URLField(required=False, widget=forms.HiddenInput)
    scrape_attr = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput)

    class Meta:
        model = models.Developer
        fields = ['name', 'url', 'scrape_attr']

    def clean(self):
        cleaned_data = super().clean()
        chosen_dev = cleaned_data['name']
        dev_url = list(filter(lambda x: x['data']['name'] == chosen_dev, DeveloperAdminAdd.dev_data))
        cleaned_data['url'] = dev_url[0]['data']['url']
        cleaned_data['scrape_attr'] = dev_url[0]['attr']

    @staticmethod
    @receiver([post_delete, post_save], sender=models.Developer)
    def update_dev_list(sender, **kwargs):
        DeveloperAdminAdd.dev_names = get_devs_to_add(DeveloperAdminAdd.dev_data)
        DeveloperAdminAdd.base_fields['name'].widget = forms.Select(choices=DeveloperAdminAdd.dev_names)


class DeveloperAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'insertion_date', 'last_modified']
    ordering = ['name']
    actions = ['add_or_update_invests_to_dev', 'add_all_flats_to_dev']
    add_form = DeveloperAdminAdd
    search_fields = ('name__startswith',)

    @admin.action(description="Add or update developer investments")
    def add_or_update_invests_to_dev(self, request, queryset):
        for dev in queryset:
            attr = dev.scrape_attr
            invests = get_developer_invests_info_from_scrape(attr)
            invest_names = list(map(lambda x: x['name'], invests))
            invest_str_msg = '<br/>'.join([
                "&emsp; " + "- " + name
                for name in invest_names
            ])
            for invest in invests:
                obj, created = models.Investment.objects.update_or_create(**invest, developer=dev, defaults={**invest})

            self.message_user(request, mark_safe(
                "Dodano następujące inwestycje dla dewelopera {dev}:<br/>".format(dev=dev.name) + invest_str_msg),
                              messages.SUCCESS)
            # try:
            #     objs = models.Investment.objects.bulk_create(
            #         [
            #             models.Investment(**invest, developer=dev)
            #             for invest in invests
            #         ]
            #     )
            #     self.message_user(request, mark_safe(
            #         "Dodano następujące inwestycje dla dewelopera {dev}:<br/>".format(dev=dev.name) + invest_str_msg),
            #                       messages.SUCCESS)
            # except IntegrityError:
            #     self.message_user(request, "Dodawana inwestycja już istnieje", messages.ERROR)

    @admin.action(description="Add flats to developer")
    def add_all_flats_to_dev(self, request, queryset):
        for dev in queryset:
            dev_investments = {investment.name: investment
                               for investment in dev.investment_set.all()}
            flats = get_flats_from_scrape(dev.scrape_attr)
            objs = models.Flat.objects.bulk_create(
                [
                    models.Flat(floor=flat['floor_number'],
                                rooms=flat['rooms_number'],
                                area=flat['area'],
                                price=flat['price'],
                                status=flat['status'],
                                url=flat['url'],
                                developer=dev,
                                investment=dev_investments[flat['invest_name']])
                    for flat in flats
                ]
            )
            self.message_user(request, "Dodano {numb} mieszkań dla {dev}.".format(numb=len(objs), dev=dev),
                              messages.SUCCESS)

    def get_form(self, request, obj=None, change=False, **kwargs):
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(DeveloperAdmin, self).get_form(request, obj, change, **defaults)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.readonly_fields = ['name']
        else:
            self.readonly_fields = []

        return super(DeveloperAdmin, self).get_readonly_fields(request, obj)


class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'developer', 'insertion_date', 'last_modified']
    ordering = ['developer', 'name']
    search_fields = ('developer__name__startswith',)


class FlatAdmin(admin.ModelAdmin):
    list_display = ['developer', 'investment', 'insertion_date']
    ordering = ['developer', 'investment']
    search_fields = ('developer__name__startswith',)


admin.site.register(models.Developer, DeveloperAdmin)
admin.site.register(models.Investment, InvestmentAdmin)
admin.site.register(models.Flat, FlatAdmin)
