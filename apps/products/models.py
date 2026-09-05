from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    symbol = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Product(models.Model):
    name = models.CharField(max_length=200)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="products",
    )

    current_purchase_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    current_sell_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    minimum_stock = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        validators=[MinValueValidator(0)],
    )

    current_stock = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        default=0,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(current_purchase_cost__gte=0),
                name="product_purchase_cost_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(current_sell_price__gte=0),
                name="product_sell_price_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(minimum_stock__gte=0),
                name="product_minimum_stock_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(current_stock__gte=0),
                name="product_current_stock_gte_0",
            ),
        ]

    def __str__(self):
        return self.name