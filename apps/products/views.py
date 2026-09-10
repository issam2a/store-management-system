from django.shortcuts import render ,redirect
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product ,Category 
from django.contrib import messages
from .forms import ProductForm ,CategoryForm
from .services import (
    activate_category,
    create_category,
    create_product,
    deactivate_category,
    update_category,
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