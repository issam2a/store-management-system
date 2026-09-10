from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Customer


@transaction.atomic
def create_customer(
    *,
    name,
    phone="",
    contact_information="",
):
    name = name.strip()
    phone = phone.strip()
    contact_information = contact_information.strip()

    if not name:
        raise ValidationError(
            "Customer name is required."
        )

    customer = Customer.objects.create(
        name=name,
        phone=phone,
        contact_information=contact_information,
        is_active=True,
    )

    return customer


@transaction.atomic
def update_customer(
    *,
    customer_id,
    name,
    phone="",
    contact_information="",
):
    name = name.strip()
    phone = phone.strip()
    contact_information = contact_information.strip()

    if not name:
        raise ValidationError(
            "Customer name is required."
        )

    customer = Customer.objects.get(
        pk=customer_id,
    )

    customer.name = name
    customer.phone = phone
    customer.contact_information = contact_information

    customer.save(
        update_fields=[
            "name",
            "phone",
            "contact_information",
            "updated_at",
        ]
    )

    return customer


@transaction.atomic
def deactivate_customer(
    *,
    customer_id,
):
    customer = Customer.objects.get(
        pk=customer_id,
    )

    if not customer.is_active:
        raise ValidationError(
            "Customer is already inactive."
        )

    customer.is_active = False

    customer.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    return customer


@transaction.atomic
def activate_customer(
    *,
    customer_id,
):
    customer = Customer.objects.get(
        pk=customer_id,
    )

    if customer.is_active:
        raise ValidationError(
            "Customer is already active."
        )

    customer.is_active = True

    customer.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    return customer