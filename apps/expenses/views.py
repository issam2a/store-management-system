from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.urls import reverse 

from .forms import ExpenseForm
from .models import Expense
from .services import record_expense


@login_required
def expense_list(request):
    """
    Display all expenses and provide
    the expense creation form.
    """

    expenses = Expense.objects.select_related(
        "created_by"
    )

    form = ExpenseForm()

    context = {
        "expenses": expenses,
        "form": form,
    }

    return render(
        request,
        "expenses/expense_list.html",
        context,
    )


@login_required
def expense_create(request):
    """
    Create a new expense.
    """

    if request.method != "POST":
        return redirect("expense_list")

    form = ExpenseForm(request.POST)

    is_ajax = (
        request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest"
    )

    if form.is_valid():

        try:

            expense = record_expense(
                category=form.cleaned_data["category"],
                amount=form.cleaned_data["amount"],
                payment_method=form.cleaned_data["payment_method"],
                expense_date=form.cleaned_data["expense_date"],
                created_by=request.user,
                description=form.cleaned_data["description"],
            )
            
        except ValidationError as exc:

            if is_ajax:
                return JsonResponse(
                    {
                        "success": False,
                        "error": _("Please correct the errors below."),
                        "errors": {
                            field: [
                                str(error)
                                for error in errors
                            ]
                            for field, errors in form.errors.items()
                        },
                    },
                    status=400,
                )
            form.add_error(
                None,
                exc,
            )

        else:

            if is_ajax:

                return JsonResponse(
                    {
                        "success": True,
                        "expense": {
                            "id": expense.id,
                            "reference": expense.reference,
                            "category": expense.category,
                            "amount": str(expense.amount),
                            "payment_method": expense.payment_method,
                            "expense_date": str(
                                expense.expense_date
                            ),
                            "delete_url": reverse(
                                "expense_delete",
                                args=[expense.id],
                            ),
                        },
                    }
                )

            return redirect(
                "expense_list"
            )

    expenses = Expense.objects.select_related(
        "created_by"
    )

    context = {
        "expenses": expenses,
        "form": form,
    }

    if is_ajax:

        return JsonResponse(
            {
                "success": False,
                "error": form.errors.as_text(),
            },
            status=400,
        )

    return render(
        request,
        "expenses/expense_list.html",
        context,
    )

@login_required
@require_POST
def expense_delete(request, expense_id):

    expense = get_object_or_404(
        Expense,
        pk=expense_id,
    )

    expense.delete()

    is_ajax = (
        request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest"
    )

    if is_ajax:

        return JsonResponse(
            {
                "success": True,
                "expense_id": expense_id,
            }
        )

    return redirect(
        "expense_list"
    )