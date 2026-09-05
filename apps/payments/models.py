from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class CustomerPayment(models.Model):
    reference = models.CharField(max_length=50, unique=True)

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    payment_method = models.CharField(max_length=50)

    payment_date = models.DateField()

    note = models.TextField(blank=True)

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_customer_payments",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="customer_payment_amount_gt_0",
            ),
        ]

    def __str__(self):
        return self.reference


class SupplierPayment(models.Model):
    reference = models.CharField(max_length=50, unique=True)

    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    payment_method = models.CharField(max_length=50)

    payment_date = models.DateField()

    note = models.TextField(blank=True)

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_supplier_payments",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="supplier_payment_amount_gt_0",
            ),
        ]

    def __str__(self):
        return self.reference