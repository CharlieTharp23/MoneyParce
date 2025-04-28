from charts.models import Transaction
from django.contrib.auth.models import User
import random
from datetime import datetime, timedelta

def populate_transactions():
    user, created = User.objects.get_or_create(username='testuser', defaults={"password":"testpass"})  # Adjust username if needed

    categories = ['Food', 'Transport', 'Rent', 'Entertainment', 'Other']
    start_date = datetime.now() - timedelta(days=90)

    for _ in range(500):
        date = start_date + timedelta(days=random.randint(0, 90))
        amount = round(random.uniform(5.0, 200.0), 2)
        category = random.choice(categories)
        description = f'{category} expense'

        Transaction.objects.create(
            user=user,
            amount=amount,
            date=date,
            category=category,
            description = description
        )

    print("Transactions populated successfully!")
