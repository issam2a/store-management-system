from django.urls import path

from .views import (
    supplier_activate,
    supplier_create,
    supplier_deactivate,
    supplier_edit,
    supplier_list,
)


urlpatterns = [
    path("", supplier_list, name="supplier_list"),
    path("create/", supplier_create, name="supplier_create"),
    path(
        "<int:supplier_id>/edit/",
        supplier_edit,
        name="supplier_edit",
    ),
    path(
        "<int:supplier_id>/activate/",
        supplier_activate,
        name="supplier_activate",
    ),
    path(
        "<int:supplier_id>/deactivate/",
        supplier_deactivate,
        name="supplier_deactivate",
    ),
]