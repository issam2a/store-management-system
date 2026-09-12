from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class InventoryAdjustment(models.Model):
    class AdjustmentType(models.TextChoices):
        INCREASE = "INCREASE", _("Increase")
        DECREASE = "DECREASE", _("Decrease")

    reference = models.CharField(
        max_length=50,
        unique=True,
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="inventory_adjustments",
    )

    adjustment_type = models.CharField(
        max_length=10,
        choices=AdjustmentType.choices,
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        validators=[MinValueValidator(0)],
    )

    reason = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inventory_adjustments",
    )

    applied_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="applied_inventory_adjustments",
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="inventory_adjustment_quantity_gt_0",
            ),
        ]

    def __str__(self):
        return self.reference