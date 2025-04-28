from django.db.models import Sum
from django.conf import settings
from datetime import datetime, timedelta
from moneyparce.email import send_simple_email
from .models import Budget, Bill

def check_budget_and_notify(user, transaction_category, transaction_amount):
    """
    Check if a new transaction would exceed the user's budget limit and send an email notification if it does.
    
    Parameters:
    - user: User model instance
    - transaction_category: String of the transaction category
    - transaction_amount: Decimal or float value of the transaction
    
    Returns:
    - Boolean: True if notification was sent, False otherwise
    """
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    try:
        budget = Budget.objects.get(
            user=user,
            category__iexact=transaction_category,
            month=current_month,
            year=current_year
        )
    except Budget.DoesNotExist:
        return False
    
    # total spending w/ transaction
    from charts.models import Transaction
    
    # calc date range for cur month
    start_date = f"{current_year}-{current_month:02d}-01"
    if current_month == 12:
        end_date = f"{current_year + 1}-01-01"
    else:
        end_date = f"{current_year}-{current_month + 1:02d}-01"
    
    # get exisitng spending
    existing_spending = Transaction.objects.filter(
        user=user,
        category__iexact=transaction_category,
        date__gte=start_date,
        date__lt=end_date
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # add new amt
    total_spending = float(existing_spending) + float(transaction_amount)
    
    # check if exceeds
    if total_spending > budget.amount:
        #send notification email
        subject = f"Budget Alert: You've exceeded your {transaction_category} budget"
        
        message = f"""
Hi {user.username},

Your recent transaction of ${transaction_amount:.2f} in the {transaction_category} category 
has caused you to exceed your monthly budget.

Budget: ${budget.amount:.2f}
Current Spending: ${total_spending:.2f}
Amount Over Budget: ${(total_spending - float(budget.amount)):.2f}

Log in to MoneyParce to review your spending and adjust your budget if needed.

Best regards,
The MoneyParce Team
        """
        
        recipient_list = [user.email]
        send_simple_email(subject, message, recipient_list)
        
        return True
    
    # check if this approaches the alert threshold
    threshold_amount = float(budget.amount) * (budget.alert_percentage / 100)
    
    if total_spending >= threshold_amount and total_spending < float(budget.amount):
        # Send approach notification
        subject = f"Budget Alert: You're approaching your {transaction_category} budget limit"
        
        percentage = int((total_spending / float(budget.amount)) * 100)
        
        message = f"""
Hi {user.username},

Your recent transaction of ${transaction_amount:.2f} in the {transaction_category} category 
has brought you to {percentage}% of your monthly budget.

Budget: ${budget.amount:.2f}
Current Spending: ${total_spending:.2f}
Remaining Budget: ${(float(budget.amount) - total_spending):.2f}

Log in to MoneyParce to review your spending and adjust your budget if needed.

Best regards,
The MoneyParce Team
        """
        
        recipient_list = [user.email]
        send_simple_email(subject, message, recipient_list)
        
        return True
    
    # No notification needed
    return False



def check_bills_and_notify(user):
    """
    Check if the user has any bills due today or within the next 7 days, and send an email reminder.

    Args:
    - user: User instance

    Returns:
    - True if a notification was sent, False otherwise
    """
    today = datetime.today().date()
    next_week = today + timedelta(days=7)

    upcoming_bills = Bill.objects.filter(
        user=user,
        due_date__gte=today,
        due_date__lte=next_week
    )

    if not upcoming_bills.exists():
        return False

    bill_list = ""
    for bill in upcoming_bills:
        bill_list += f"- {bill.name}: Due {bill.due_date.strftime('%B %d, %Y')} (${bill.amount:.2f})\n"

    subject = "Upcoming Bill Reminder - MoneyParce"
    message = f"""
                Hi {user.username},

                You have the following bills due soon:

                {bill_list}

                Make sure to review and pay them on time to avoid any late fees!

                Best regards,
                The MoneyParce Team
            """

    recipient = [user.email]
    send_simple_email(subject, message, recipient)
    return True