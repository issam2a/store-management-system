from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.sale_list,
        name="sale_list",
    ),

    path(
        "create/",
        views.sale_create,
        name="sale_create",
    ),

    path(
        "products/search/",
        views.product_search,
        name="sale_product_search",
    ),

    path(
        "<int:sale_id>/",
        views.sale_detail,
        name="sale_detail",
    ),

    path(
        "<int:sale_id>/items/create/",
        views.sale_item_create,
        name="sale_item_create",
    ),

    path(
        "items/<int:item_id>/edit/",
        views.sale_item_edit,
        name="sale_item_edit",
    ),

    path(
        "items/<int:item_id>/remove/",
        views.sale_item_remove,
        name="sale_item_remove",
    ),

    path(
        "<int:sale_id>/discount/",
        views.sale_discount_update,
        name="sale_discount_update",
    ),

    path(
        "<int:sale_id>/complete/",
        views.sale_complete,
        name="sale_complete",
    ),

    path(
        "<int:sale_id>/cancel/",
        views.sale_cancel,
        name="sale_cancel",
    ),
]