from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.expense_list,
        name="expense_list",
    ),
    path(
        "create/",
        views.expense_create,
        name="expense_create",
    ),
     path(
        "<int:expense_id>/delete/",
        views.expense_delete,
        name="expense_delete",
    ),
]