from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from datetime import datetime
from .models import Budget
from .forms import BillForm
from charts.models import Transaction
from django.db.models import Sum
from django import forms
from .notifications import check_bills_and_notify

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year', 'alert_percentage']
        widgets = {
            'month': forms.Select(choices=[(i, i) for i in range(1, 13)]),
            'year': forms.Select(choices=[(i, i) for i in range(2024, 2031)]),
            'alert_percentage': forms.NumberInput(attrs={'min': 1, 'max': 100})
        }

@login_required
def budget_list(request):
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # get budgets for cur month/year
    budgets = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year
    )
    
    budget_progress = []
    
    # get transactions for category in the cur month
    for budget in budgets:
        start_date = f"{budget.year}-{budget.month:02d}-01"
        if budget.month == 12:
            end_date = f"{budget.year + 1}-01-01"
        else:
            end_date = f"{budget.year}-{budget.month + 1:02d}-01"
            
        spending = Transaction.objects.filter(
            user=request.user,
            category__iexact=budget.category,
            date__gte=start_date,
            date__lt=end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # calc percentage
        percentage = int((float(spending) / float(budget.amount)) * 100) if budget.amount > 0 else 0
        
        if percentage >= 100:
            status = 'danger'
        elif percentage >= budget.alert_percentage:
            status = 'warning'
        else:
            status = 'success'
            
        budget_progress.append({
            'budget': budget,
            'spending': spending,
            'percentage': percentage,
            'status': status,
            'remaining': float(budget.amount) - float(spending)
        })
        
    check_bills_and_notify(request.user)
    
    return render(request, 'budgets/budget_list.html', {
        'budget_progress': budget_progress,
        'current_month': current_month,
        'current_year': current_year
    })

@login_required
def budget_sliders(request):
    """View for the slider-based budget adjustment interface"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    if request.method == 'POST':
        categories = []
        
        # find all category fields in the form
        for key, value in request.POST.items():
            if key.startswith('category_'):
                category_name = value
                amount_key = f'amount_{category_name}'
                percentage_key = f'percentage_{category_name}'
                
                if amount_key in request.POST and percentage_key in request.POST:
                    amount = float(request.POST[amount_key])
                    percentage = int(request.POST[percentage_key])
                    budget, created = Budget.objects.update_or_create(
                        user=request.user,
                        category=category_name,
                        month=current_month,
                        year=current_year,
                        defaults={
                            'amount': amount,
                            'alert_percentage': 80  # default alert percentage
                        }
                    )
                    
        messages.success(request, "Budget settings saved successfully.")
        return redirect('budget_list')
    
    budgets = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year
    )
    
    # get unique categories from transactions
    transaction_categories = Transaction.objects.filter(user=request.user).values_list('category', flat=True).distinct()
    
    categories = []
    total_budget = 0
    original_total = 0
    

    for budget in budgets:
        # calc the original amount (100%)
        original_amount = float(budget.amount) * (100 / 100)  # Assuming current amount is at 100%
        
        categories.append({
            'name': budget.category,
            'amount': float(budget.amount),
            'percentage': 100,
            'savings': 0,
            'original_amount': original_amount
        })
        
        total_budget += float(budget.amount)
        original_total += original_amount
    
    # add any transaction categories that don't have budgets yet
    for category in transaction_categories:
        if not any(c['name'] == category for c in categories):
            # for new categories, set a default amount based on recent transactions
            start_date = f"{current_year}-{current_month:02d}-01"
            if current_month == 12:
                end_date = f"{current_year + 1}-01-01"
            else:
                end_date = f"{current_year}-{current_month + 1:02d}-01"
                
            avg_spending = Transaction.objects.filter(
                user=request.user,
                category__iexact=category,
                date__gte=start_date,
                date__lt=end_date
            ).aggregate(avg=Sum('amount'))['avg'] or 0
            
            # If no transactions in current month, then use a default amount
            if avg_spending == 0:
                avg_spending = 100  
            
            categories.append({
                'name': category,
                'amount': avg_spending,
                'percentage': 100,
                'savings': 0, 
                'original_amount': avg_spending
            })
            
            total_budget += avg_spending
            original_total += avg_spending
    
    # THESE ARE THE DEFAULT CATEGORIES, NOT SURE ABOUT THIS
    if not categories:
        default_categories = ['Food', 'Transportation', 'Entertainment', 'Housing']
        for category in default_categories:
            categories.append({
                'name': category,
                'amount': 100, 
                'percentage': 100, 
                'savings': 0, 
                'original_amount': 100
            })
            total_budget += 100
            original_total += 100
    
    return render(request, 'budgets/budget_sliders.html', {
        'categories': categories,
        'total_budget': total_budget,
        'original_total': original_total,
        'per_week': total_budget / 4,  # approx. weekly amount
        'current_month': current_month,
        'current_year': current_year
    })

@login_required
def add_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            
            # check if budget for this category / month / year already exists
            exists = Budget.objects.filter(
                user=request.user, 
                category=budget.category,
                month=budget.month,
                year=budget.year
            ).exists()
            
            if exists:
                messages.error(request, "A budget for this category and month already exists.")
            else:
                budget.save()
                messages.success(request, "Budget created successfully.")
                return redirect('budget_list')
    else:
        # Default to current month/year
        current_date = datetime.now()
        form = BudgetForm(initial={
            'month': current_date.month,
            'year': current_date.year,
            'alert_percentage': 80
        })
    
    # get categories from existing transactions
    categories = Transaction.objects.filter(user=request.user).values_list('category', flat=True).distinct()
    
    return render(request, 'budgets/budget_form.html', {
        'form': form,
        'categories': categories,
        'title': 'Add Budget'
    })

@login_required
def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, "Budget updated successfully.")
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget)
    
    # get categories from existing transactions
    categories = Transaction.objects.filter(user=request.user).values_list('category', flat=True).distinct()
    
    return render(request, 'budgets/budget_form.html', {
        'form': form,
        'categories': categories,
        'title': 'Edit Budget'
    })

@login_required
def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, "Budget deleted successfully.")
        return redirect('budget_list')
    
    return render(request, 'budgets/budget_confirm_delete.html', {'budget': budget})

@login_required
def create_bill(request):
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.user = request.user
            bill.save()
            return redirect('budget_list')  # We’ll create this page next
    else:
        form = BillForm()
    
    return render(request, 'budgets/create_bill.html', {'form': form})