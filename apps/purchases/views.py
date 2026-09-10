from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from .models import Purchase

from django.contrib import messages
from django.shortcuts import redirect

from .forms import PurchaseForm
from .services import create_purchase


@login_required
def purchase_list(request):
    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "")

    purchases = (
        Purchase.objects
        .select_related(
            "supplier",
            "created_by",
        )
        .order_by("-created_at")
    )

    if query:
        purchases = purchases.filter(
            Q(reference__icontains=query)
            | Q(supplier__name__icontains=query)
        )

    if selected_status:
        purchases = purchases.filter(
            status=selected_status
        )

    paginator = Paginator(
        purchases,
        20,
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    context = {
        "page_obj": page_obj,
        "paginator": paginator,
        "purchases": page_obj.object_list,
        "query": query,
        "selected_status": selected_status,
    }

    return render(
        request,
        "purchases/purchase_list.html",
        context,
    )

@login_required
def purchase_create(request):

    if request.method == "POST":

        form = PurchaseForm(
            request.POST
        )

        if form.is_valid():

            purchase = create_purchase(
                supplier=form.cleaned_data["supplier"],
                payment_type=form.cleaned_data["payment_type"],
                user=request.user,
            )

            messages.success(
                request,
                "Purchase draft created successfully."
            )

            return redirect(
                "purchase_detail",
                purchase.id,
            )

    else:
        form = PurchaseForm()

    context = {
        "form": form,
        "page_title": "Create Purchase",
        "submit_label": "Create Draft",
    }

    return render(
        request,
        "purchases/purchase_form.html",
        context,
    )

def purchase_detail(request, purchase_id):
    purchase = get_object_or_404(
        Purchase.objects.select_related(
            "supplier",
            "created_by",
            "completed_by",
            "cancelled_by",
        ).prefetch_related(
            "items__product",
        ),
        pk=purchase_id,
    )

    context = {
        "purchase": purchase,
        "items": purchase.items.all(),
    }

    return render(
        request,
        "purchases/purchase_detail.html",
        context,
    )