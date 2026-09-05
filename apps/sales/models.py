from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Sale(models.Model):
    class PaymentType(models.TextChoices):
        CASH = "CASH", "Cash"
        CREDIT = "CREDIT", "Credit"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    reference = models.CharField(max_length=50, unique=True)

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="sales",
        null=True,
        blank=True,
    )

    payment_type = models.CharField(
        max_length=10,
        choices=PaymentType.choices,
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    subtotal_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )

    discount_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_sales",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="completed_sales",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="cancelled_sales",
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(subtotal_amount__gte=0),
                name="sale_subtotal_amount_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(discount_amount__gte=0),
                name="sale_discount_amount_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(total_amount__gte=0),
                name="sale_total_amount_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    discount_amount__lte=models.F("subtotal_amount")
                ),
                name="sale_discount_lte_subtotal",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    total_amount=models.F("subtotal_amount")
                    - models.F("discount_amount")
                ),
                name="sale_total_equals_subtotal_minus_discount",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.payment_type == self.PaymentType.CREDIT
            and self.customer_id is None
        ):
            raise ValidationError(
                {"customer": "A credit sale requires a customer."}
            )

    def __str__(self):
        return self.reference


class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="sale_items",
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        validators=[MinValueValidator(0)],
    )

    unit_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    line_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="sale_item_quantity_gt_0",
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="sale_item_unit_price_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(line_total__gte=0),
                name="sale_item_line_total_gte_0",
            ),
        ]

    def __str__(self):
        return f"{self.sale.reference} - {self.product.name}"