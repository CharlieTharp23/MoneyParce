from django.shortcuts import render, redirect
from charts.models import Transaction
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm
from budgets.notifications import check_budget_and_notify

@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()

            check_budget_and_notify(
                user=request.user,
                transaction_category=transaction.category,
                transaction_amount=transaction.amount
            )

            return redirect('transaction_list')
    else:
        form = TransactionForm()
    
    return render(request, 'transaction/index.html', {'form': form})

@login_required
def transaction_list(request):
    # Get the last 20 transactions for the logged-in user, ordered by date (newest first)
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:20]
    return render(request, 'transaction/transaction_list.html', {'transactions': transactions})

