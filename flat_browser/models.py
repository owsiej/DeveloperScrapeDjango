from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.

class Developer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    insertion_date = models.DateTimeField(auto_now_add=True, editable=False, blank=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False, blank=True)
    scrape_attr = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        select_on_save = True


class Investment(models.Model):
    name = models.CharField(max_length=300, unique=True)
    url = models.URLField()
    developer = models.ForeignKey("Developer", on_delete=models.RESTRICT)
    insertion_date = models.DateTimeField(auto_now_add=True, editable=False, blank=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['developer', 'name']
        select_on_save = True


class Flat(models.Model):
    FLAT_STATUS = [('wolne', 'wolne'),
                   ('sprzedane', 'sprzedane'),
                   ('zarezerwowane', 'zarezerwowane')]

    investment = models.ForeignKey("Investment", on_delete=models.CASCADE)
    developer = models.ForeignKey("Developer", on_delete=models.CASCADE)
    floor = models.PositiveIntegerField(null=True)
    rooms = models.PositiveIntegerField(validators=[MaxValueValidator(10)], null=True)
    area = models.FloatField(validators=[MinValueValidator(0.00)], null=True)
    price = models.FloatField(validators=[MinValueValidator(0.00)], null=True)
    status = models.CharField(max_length=50, choices=FLAT_STATUS, null=True)
    url = models.URLField(blank=True)
    insertion_date = models.DateField(auto_now_add=True, editable=False, blank=True)

    def __str__(self):
        return f"Flat: {self.investment}"

    def clean(self):
        if self.investment.developer.id != self.developer.id:
            raise ValidationError({
                "developer": "Developer should be same as in investment."
            })
