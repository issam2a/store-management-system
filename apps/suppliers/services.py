from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Supplier


@transaction.atomic
def create_supplier(
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
            "Supplier name is required."
        )

    supplier = Supplier.objects.create(
        name=name,
        phone=phone,
        contact_information=contact_information,
        is_active=True,
    )

    return supplier


@transaction.atomic
def update_supplier(
    *,
    supplier_id,
    name,
    phone="",
    contact_information="",
):
    name = name.strip()
    phone = phone.strip()
    contact_information = contact_information.strip()

    if not name:
        raise ValidationError(
            "Supplier name is required."
        )

    try:
        supplier = Supplier.objects.get(
            pk=supplier_id,
        )
    except Supplier.DoesNotExist:
        raise ValidationError(
            "Supplier does not exist."
        )

    supplier.name = name
    supplier.phone = phone
    supplier.contact_information = contact_information

    supplier.save(
        update_fields=[
            "name",
            "phone",
            "contact_information",
            "updated_at",
        ]
    )

    return supplier


@transaction.atomic
def deactivate_supplier(
    *,
    supplier_id,
):
    try:
        supplier = Supplier.objects.get(
            pk=supplier_id,
        )
    except Supplier.DoesNotExist:
        raise ValidationError(
            "Supplier does not exist."
        )

    if not supplier.is_active:
        raise ValidationError(
            "Supplier is already inactive."
        )

    supplier.is_active = False

    supplier.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    return supplier


@transaction.atomic
def activate_supplier(
    *,
    supplier_id,
):
    try:
        supplier = Supplier.objects.get(
            pk=supplier_id,
        )
    except Supplier.DoesNotExist:
        raise ValidationError(
            "Supplier does not exist."
        )

    if supplier.is_active:
        raise ValidationError(
            "Supplier is already active."
        )

    supplier.is_active = True

    supplier.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    return supplier