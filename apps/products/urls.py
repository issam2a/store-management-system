from django.urls import path

from .views import (
    category_activate,
    category_create,
    category_deactivate,
    category_edit,
    category_list,
    product_create,
    product_list,
)

urlpatterns = [
    path("", product_list, name="product_list"),
    path("create/", product_create, name="product_create"),

    path(
        "categories/",
        category_list,
        name="category_list",
    ),
    path(
        "categories/create/",
        category_create,
        name="category_create",
    ),
    path(
        "categories/<int:category_id>/edit/",
        category_edit,
        name="category_edit",
    ),
    path(
        "categories/<int:category_id>/activate/",
        category_activate,
        name="category_activate",
    ),
    path(
        "categories/<int:category_id>/deactivate/",
        category_deactivate,
        name="category_deactivate",
    ),
]