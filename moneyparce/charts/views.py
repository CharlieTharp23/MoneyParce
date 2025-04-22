from django.shortcuts import render
from .charts import SpendingOverTimeChart, CategoryBreakdownChart, IncomeVsExpenseChart
from .models import Transaction  # Assuming your Transaction model exists
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
from django.db.models import Sum

def chart_view(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)

    # Prepare data for Spending Over Time
    monthly_totals = {}
    for txn in transactions:
        month = txn.date.strftime("%b %Y")  # e.g., "Jan 2025"
        monthly_totals[month] = monthly_totals.get(month, 0) + txn.amount

    line_chart = SpendingOverTimeChart("Month", "Amount ($)", "Spending Over Time")
    line_chart.add_data(list(monthly_totals.keys()), list(monthly_totals.values()))

    # Prepare data for Category Breakdown
    category_totals = {}
    for txn in transactions:
        category_totals[txn.category] = category_totals.get(txn.category, 0) + txn.amount

    pie_chart = CategoryBreakdownChart("", "", "Spending by Category")
    pie_chart.add_data(category_totals)

    # Prepare data for Income vs Expense
    income = sum(txn.amount for txn in transactions if txn.amount > 0)
    expense = sum(-txn.amount for txn in transactions if txn.amount < 0)

    bar_chart = IncomeVsExpenseChart("", "Amount ($)", "Income vs Expense")
    bar_chart.add_data(["Income", "Expense"], [income, expense])

    return render(request, 'charts/index.html', {
        'line_chart': line_chart.render_to_base64(),
        'pie_chart': pie_chart.render_to_base64(),
        'bar_chart': bar_chart.render_to_base64(),
    })

def test_chart_view(request):
    # TEMP: force‑login testuser until you wire up real auth
    user = User.objects.get(username='testuser')

    # filters from GET
    category   = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date   = request.GET.get('end_date')

    qs = Transaction.objects.filter(user=user)
    if category:
        qs = qs.filter(category__iexact=category)
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)

    # aggregate monthly totals
    grouped = (
        qs
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    dates   = [entry['month'].strftime('%b %Y') for entry in grouped]
    amounts = [float(entry['total']) for entry in grouped]

    # build and render chart
    chart = SpendingOverTimeChart("Month", "Spending ($)", "Spending Over Time")
    chart.add_data(dates, amounts, label="Total Spending")
    chart_b64 = chart.render_to_base64()

    return render(request, 'charts/index.html', {
        'chart': chart_b64,
        # if you later add filters, pass them back here:
        'selected_category': category or '',
        'start_date': start_date or '',
        'end_date': end_date or '',
    })