from django.db import models


# Create your models here.
class Developer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    insertion_date = models.DateTimeField(auto_now_add=True, editable=False, blank=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False, blank=True)

    def __str__(self):
        return f"Developer: {self.name}"

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
        return f"Investment: {self.name}, {self.developer}"

    class Meta:
        order_with_respect_to = 'developer'
        select_on_save = True


class Flat(models.Model):
    investment = models.ForeignKey("Investment", on_delete=models.CASCADE)
    floor = models.IntegerField()
    rooms = models.IntegerField()
    area = models.FloatField()
    price = models.FloatField()
    status = models.CharField(max_length=50)
    url = models.URLField()
    insertion_date = models.DateField(auto_now_add=True, editable=False, blank=True)

    def __str__(self):
        return f"Flat: {self.investment}"
