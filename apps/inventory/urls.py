from django.urls import include, path

from . import views


urlpatterns = [
    path("", views.inventory_list, name="inventory_list"),
    path(
        "adjustments/create/",
        views.inventory_adjustment_create,
        name="inventory_adjustment_create",
    ),
    path(
        "adjustments/history/",
        views.inventory_adjustment_history,
        name="inventory_adjustment_history",
    ),
]