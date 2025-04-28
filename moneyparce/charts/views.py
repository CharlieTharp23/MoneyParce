from django.shortcuts import render
from .charts import SpendingOverTimeChart, CategoryBreakdownChart, IncomeVsExpenseChart
from .models import Transaction  # Assuming your Transaction model exists
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from datetime import date, timedelta

def chart_view(request):
    user = request.user
    
    # filters from GET
    category   = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date   = request.GET.get('end_date')

    qs = Transaction.objects.filter(user=user)
    if category:
        qs = qs.filter(category__iexact=category)
    if not start_date and not end_date:
        # Default to last 30 days
        default_start_date = date.today() - timedelta(days=30)
        qs = qs.filter(date__gte=default_start_date)
    else:
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)

    # Today's date
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    start_of_month = today.replace(day=1)

    spent_today = qs.filter(date=today).aggregate(total=Sum('amount'))['total'] or 0
    spent_week  = qs.filter(date__gte=start_of_week).aggregate(total=Sum('amount'))['total'] or 0
    spent_month = qs.filter(date__gte=start_of_month).aggregate(total=Sum('amount'))['total'] or 0
    if category:
        spent_today = qs.filter(date=today, category__iexact=category).aggregate(total=Sum('amount'))['total'] or 0
        spent_week  = qs.filter(date__gte=start_of_week, category__iexact=category).aggregate(total=Sum('amount'))['total'] or 0
        spent_month = qs.filter(date__gte=start_of_month, category__iexact=category).aggregate(total=Sum('amount'))['total'] or 0

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
        'spent_today' : spent_today,
        'spent_week' : spent_week,
        'spent_month' : spent_month,
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

    if not start_date and not end_date:
        # Default to last 30 days
        default_start_date = date.today() - timedelta(days=30)
        qs = qs.filter(date__gte=default_start_date)
    else:
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)


    categories = Transaction.objects.filter(user=user).values_list('category', flat=True).distinct()
    
    # Today's date
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    start_of_month = today.replace(day=1)
    
    spent_today = qs.filter(date=today).aggregate(total=Sum('amount'))['total'] or 0
    spent_week  = qs.filter(date__gte=start_of_week).aggregate(total=Sum('amount'))['total'] or 0
    spent_month = qs.filter(date__gte=start_of_month).aggregate(total=Sum('amount'))['total'] or 0
    if category:
        spent_today = qs.filter(date=today, category__iexact=category).aggregate(total=Sum('amount'))['total'] or 0
        spent_week  = qs.filter(date__gte=start_of_week, category__iexact=category).aggregate(total=Sum('amount'))['total'] or 0
        spent_month = qs.filter(date__gte=start_of_month, category__iexact=category).aggregate(total=Sum('amount'))['total'] or 0


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
        'spent_today' : spent_today,
        'spent_week' : spent_week,
        'spent_month' : spent_month,
    })