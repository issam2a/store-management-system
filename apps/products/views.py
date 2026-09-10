from django.shortcuts import render ,redirect
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product ,Category ,Unit
from django.contrib import messages
from .forms import ProductForm ,CategoryForm ,UnitForm

from .services import (
    activate_category,
    activate_unit,
    create_category,
    create_product,
    create_unit,
    deactivate_category,
    deactivate_unit,
    update_category,
    update_unit,
)

def product_list(request):
    products = (
        Product.objects
        .select_related("category", "unit")
        .all()
    )

    return render(
        request,
        "products/product_list.html",
        {
            "products": products,
        },
    )

def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = create_product(
                name=form.cleaned_data["name"],
                category_id=form.cleaned_data["category"].id,
                unit_id=form.cleaned_data["unit"].id,
                current_purchase_cost=form.cleaned_data[
                    "current_purchase_cost"
                ],
                current_sell_price=form.cleaned_data[
                    "current_sell_price"
                ],
                minimum_stock=form.cleaned_data["minimum_stock"],
            )
            messages.success(
                request,
                "Product created successfully.",
            )

            return redirect("product_list")

    else:
        form = ProductForm()

    return render(
        request,
        "products/product_create.html",
        {
            "form": form,
        },
    )

# -------------------------------------------------------------------
# Category CRUD
# -------------------------------------------------------------------


def category_list(request):
    categories = Category.objects.all()

    return render(
        request,
        "products/category_list.html",
        {
            "categories": categories,
        },
    )


def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            try:
                create_category(
                    name=form.cleaned_data["name"],
                )
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    "Category created successfully.",
                )

                return redirect("category_list")

    else:
        form = CategoryForm()

    return render(
        request,
        "products/category_form.html",
        {
            "form": form,
            "page_title": "Create Category",
            "submit_label": "Create Category",
        },
    )


def category_edit(request, category_id):
    category = get_object_or_404(
        Category,
        pk=category_id,
    )

    if request.method == "POST":
        form = CategoryForm(
            request.POST,
            instance=category,
        )

        if form.is_valid():
            try:
                update_category(
                    category_id=category.id,
                    name=form.cleaned_data["name"],
                )
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    "Category updated successfully.",
                )

                return redirect("category_list")

    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        "products/category_form.html",
        {
            "form": form,
            "page_title": "Edit Category",
            "submit_label": "Save Changes",
            "category": category,
        },
    )


def category_deactivate(request, category_id):
    if request.method != "POST":
        return redirect("category_list")

    category = get_object_or_404(
        Category,
        pk=category_id,
    )

    deactivate_category(
        category_id=category.id,
    )

    messages.success(
        request,
        "Category deactivated successfully.",
    )

    return redirect("category_list")


def category_activate(request, category_id):
    if request.method != "POST":
        return redirect("category_list")

    category = get_object_or_404(
        Category,
        pk=category_id,
    )

    activate_category(
        category_id=category.id,
    )

    messages.success(
        request,
        "Category activated successfully.",
    )

    return redirect("category_list")

def unit_list(request):
    units = Unit.objects.all()

    return render(
        request,
        "products/unit_list.html",
        {"units": units},
    )


def unit_create(request):
    if request.method == "POST":
        form = UnitForm(request.POST)

        if form.is_valid():
            try:
                create_unit(
                    name=form.cleaned_data["name"],
                    symbol=form.cleaned_data["symbol"],
                )
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    "Unit created successfully.",
                )
                return redirect("unit_list")
    else:
        form = UnitForm()

    return render(
        request,
        "products/unit_form.html",
        {
            "form": form,
            "page_title": "Create Unit",
            "submit_label": "Create Unit",
        },
    )


def unit_edit(request, unit_id):
    unit = get_object_or_404(Unit, pk=unit_id)

    if request.method == "POST":
        form = UnitForm(request.POST, instance=unit)

        if form.is_valid():
            try:
                update_unit(
                    unit_id=unit.id,
                    name=form.cleaned_data["name"],
                    symbol=form.cleaned_data["symbol"],
                )
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    "Unit updated successfully.",
                )
                return redirect("unit_list")
    else:
        form = UnitForm(instance=unit)

    return render(
        request,
        "products/unit_form.html",
        {
            "form": form,
            "page_title": "Edit Unit",
            "submit_label": "Save Changes",
            "unit": unit,
        },
    )


def unit_deactivate(request, unit_id):
    if request.method != "POST":
        return redirect("unit_list")

    unit = get_object_or_404(Unit, pk=unit_id)

    deactivate_unit(unit_id=unit.id)

    messages.success(
        request,
        "Unit deactivated successfully.",
    )

    return redirect("unit_list")


def unit_activate(request, unit_id):
    if request.method != "POST":
        return redirect("unit_list")

    unit = get_object_or_404(Unit, pk=unit_id)

    activate_unit(unit_id=unit.id)

    messages.success(
        request,
        "Unit activated successfully.",
    )

    return redirect("unit_list")