from django.conf import settings
from django.db import models
from django.db.models import Q


class TransactionCancellation(models.Model):
    sale = models.ForeignKey(
        "sales.Sale",
        on_delete=models.PROTECT,
        related_name="cancellation",
        null=True,
        blank=True,
    )

    purchase = models.ForeignKey(
        "purchases.Purchase",
        on_delete=models.PROTECT,
        related_name="cancellation",
        null=True,
        blank=True,
    )

    reason = models.TextField()

    cancelled_at = models.DateTimeField(auto_now_add=True)

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="transaction_cancellations",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(sale__isnull=False, purchase__isnull=True)
                    | Q(sale__isnull=True, purchase__isnull=False)
                ),
                name="exactly_one_of_sale_or_purchase",
            ),
            models.UniqueConstraint(
                fields=["sale"],
                condition=Q(sale__isnull=False),
                name="unique_sale_cancellation",
            ),
            models.UniqueConstraint(
                fields=["purchase"],
                condition=Q(purchase__isnull=False),
                name="unique_purchase_cancellation",
            ),
        ]

    def __str__(self):
        if self.sale_id:
            return f"Cancellation - Sale {self.sale.reference}"

        return f"Cancellation - Purchase {self.purchase.reference}"