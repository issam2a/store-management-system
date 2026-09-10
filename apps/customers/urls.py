from django.urls import path

from .views import (
    customer_activate,
    customer_create,
    customer_deactivate,
    customer_edit,
    customer_list,
)


urlpatterns = [
    path(
        "",
        customer_list,
        name="customer_list",
    ),
    path(
        "create/",
        customer_create,
        name="customer_create",
    ),
    path(
        "<int:customer_id>/edit/",
        customer_edit,
        name="customer_edit",
    ),
    path(
        "<int:customer_id>/activate/",
        customer_activate,
        name="customer_activate",
    ),
    path(
        "<int:customer_id>/deactivate/",
        customer_deactivate,
        name="customer_deactivate",
    ),
]