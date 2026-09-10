from django.urls import path

from .views import (
    category_activate,
    category_create,
    category_deactivate,
    category_edit,
    category_list,
    product_create,
    product_edit,
    product_list,
    unit_activate,
    unit_create,
    unit_deactivate,
    unit_edit,
    unit_list,
    product_activate,
    product_deactivate,
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
    path("units/", unit_list, name="unit_list"),
    path("units/create/", unit_create, name="unit_create"),
    path("units/<int:unit_id>/edit/", unit_edit, name="unit_edit"),
    path(
        "units/<int:unit_id>/activate/",
        unit_activate,
        name="unit_activate",
    ),
    path(
        "units/<int:unit_id>/deactivate/",
        unit_deactivate,
        name="unit_deactivate",
    ),

    path(
        "<int:product_id>/edit/",
        product_edit,
        name="product_edit",
    ),
    path(
        "<int:product_id>/activate/",
        product_activate,
        name="product_activate",
    ),
    path(
        "<int:product_id>/deactivate/",
        product_deactivate,
        name="product_deactivate",
    ),
]