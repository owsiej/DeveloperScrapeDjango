from django.urls import path

from . import views

app_name = "flat_browser"

urlpatterns = [
    path("", views.DeveloperList.as_view(), name="developer"),
    path("flat/", views.FlatList.as_view(), name="flat"),
    path("find_flat/", views.FlatFormView.as_view(), name="find_flat"),
    path("excel_file/", views.export_excel_file, name="excel_file")
]
