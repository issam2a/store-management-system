from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.shortcuts import render

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

    if form.is_valid():

        try:

            record_expense(
                category=form.cleaned_data["category"],
                amount=form.cleaned_data["amount"],
                payment_method=form.cleaned_data["payment_method"],
                expense_date=form.cleaned_data["expense_date"],
                created_by=request.user,
                reference=form.cleaned_data["reference"],
                description=form.cleaned_data["description"],
            )

        except ValidationError as exc:

            form.add_error(
                None,
                exc,
            )

        else:

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

    return render(
        request,
        "expenses/expense_list.html",
        context,
    )