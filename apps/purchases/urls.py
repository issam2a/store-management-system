from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.purchase_list,
        name="purchase_list",
    ),
    path(
        "create/",
        views.purchase_create,
        name="purchase_create",
    ),
    path(
        "<int:purchase_id>/items/create/",
        views.purchase_item_create,
        name="purchase_item_create",
    ),
    path(
        "<int:purchase_id>/",
        views.purchase_detail,
        name="purchase_detail",
    ),
    path(
    "items/<int:item_id>/edit/",
    views.purchase_item_edit,
    name="purchase_item_edit",
    ),
    path(
        "items/<int:item_id>/delete/",
        views.purchase_item_delete,
        name="purchase_item_delete",
    ),
    path(
    "<int:purchase_id>/complete/",
    views.purchase_complete,
    name="purchase_complete",
    ),
]