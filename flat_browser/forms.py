from django import forms
from django.db.models import Max

from .models import Flat


class FlatForm(forms.Form):
    FLAT_STATUS = [
        ('wolne', 'wolne'),
        ('sprzedane', 'sprzedane'),
        ('zarezerwowane', 'zarezerwowane')]
    floor_gte = forms.IntegerField(label="Piętro od:", min_value=0, initial=0)
    floor_lte = forms.IntegerField(label="Piętro do:", min_value=0)
    rooms_gte = forms.IntegerField(label="Pokoje od:", min_value=0, initial=0)
    rooms_lte = forms.IntegerField(label="Pokoje do:", min_value=0)
    area_gte = forms.FloatField(label="Powierzchnia od:", min_value=0, initial=0)
    area_lte = forms.FloatField(label="Powierzchnia do:", min_value=0)
    price_gte = forms.FloatField(label="Cena od:", min_value=0, initial=0)
    price_lte = forms.FloatField(label="Cena do:", min_value=0)
    status = forms.MultipleChoiceField(label="Dostępność", widget=forms.CheckboxSelectMultiple, choices=FLAT_STATUS,
                                       required=True, initial="wolne", error_messages={"required": "Zaznacz status."})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        max_values = Flat.objects.aggregate(Max('floor'), Max('rooms'), Max('area'), Max('price'))
        self.fields['floor_lte'].initial = max_values['floor__max']
        self.fields['rooms_lte'].initial = max_values['rooms__max']
        self.fields['area_lte'].initial = max_values['area__max']
        self.fields['price_lte'].initial = max_values['price__max']

    def clean(self):
        cleaned_data = super().clean()
        floorlte = cleaned_data.get("floor_lte")
        floorgte = cleaned_data.get("floor_gte")
        roomslte = cleaned_data.get("rooms_lte")
        roomsgte = cleaned_data.get("rooms_gte")
        arealte = cleaned_data.get("area_lte")
        areagte = cleaned_data.get("area_gte")
        pricelte = cleaned_data.get("price_lte")
        pricegte = cleaned_data.get("price_gte")

        if floorlte < floorgte:
            self.add_error("floor_gte", "Podałeś zły zakres pięter")
        if roomslte < roomsgte:
            self.add_error("rooms_gte", "Podałeś zły zakres pokoi")
        if arealte < areagte:
            self.add_error("area_gte", "Podałeś zły zakres powierzchni")
        if pricelte < pricegte:
            self.add_error("price_gte", "Podałeś zły zakres cen")
