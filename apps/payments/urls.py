from django.urls import path

from . import views


urlpatterns = [
    path(
        "customers/<int:customer_id>/create/",
        views.customer_payment_create,
        name="customer_payment_create",
    ),
]