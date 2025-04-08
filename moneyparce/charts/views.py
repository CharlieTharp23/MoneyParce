from django.shortcuts import render
from .charts import SpendingOverTimeChart, CategoryBreakdownChart, IncomeVsExpenseChart
from .models import Transaction  # Assuming your Transaction model exists

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
    # Example data (replace with real transaction query later)
    dates = ["Jan", "Feb", "Mar", "Apr"]
    spending = [500, 650, 400, 700]

    chart = SpendingOverTimeChart("Month", "Spending ($)", "Spending Over Time")
    chart.add_data(dates, spending, label="Total Spending")

    chart_base64 = chart.render_to_base64()

    return render(request, 'charts/index.html', {
    'spending_chart': chart_base64,
    'category_chart': chart_base64,
    'income_chart': chart_base64
    })
