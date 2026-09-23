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
]