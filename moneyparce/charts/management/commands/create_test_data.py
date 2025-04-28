from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from charts.models import Transaction
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Creates test transaction data for a user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='testuser', help='Username to create data for')
        parser.add_argument('--count', type=int, default=50, help='Number of transactions to create')

    def handle(self, *args, **options):
        username = options['username']
        count = options['count']
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': f'{username}@gmail.com'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created new user: {username}'))
            user.set_password('testpassword123')
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'Login credentials:'))
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Password: testpassword123')
            self.stdout.write(f'Email: {username}@example.com')
        
        categories = [
            'Food', 'Groceries', 'Dining', 'Transportation', 
            'Entertainment', 'Housing', 'Utilities', 'Shopping',
            'Health', 'Travel', 'Education', 'Subscriptions'
        ]
        
        # gen random transactions
        transactions_created = 0
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)
        
        Transaction.objects.filter(user=user).delete()
        
        for _ in range(count):
            # rand date then category amount within the range
            days_offset = random.randint(0, (end_date - start_date).days)
            transaction_date = start_date + timedelta(days=days_offset)
            
            category = random.choice(categories)
            
            amount = round(random.uniform(1, 200), 2)
            
            descriptions = {
                'Food': ['Lunch', 'Dinner', 'Breakfast', 'Coffee'],
                'Groceries': ['Supermarket', 'Farmers Market', 'Grocery Store'],
                'Dining': ['Restaurant', 'Fast Food', 'Takeout'],
                'Transportation': ['Gas', 'Bus Fare', 'Uber', 'Taxi'],
                'Entertainment': ['Movies', 'Concert', 'Streaming Service'],
                'Housing': ['Rent', 'Mortgage', 'Home Repairs'],
                'Utilities': ['Electricity', 'Water', 'Internet', 'Phone'],
                'Shopping': ['Clothes', 'Electronics', 'Home Goods'],
                'Health': ['Pharmacy', 'Doctor Visit', 'Gym'],
                'Travel': ['Flight', 'Hotel', 'Car Rental'],
                'Education': ['Books', 'Tuition', 'Course Fee'],
                'Subscriptions': ['Netflix', 'Spotify', 'Amazon Prime']
            }
            
            description_options = descriptions.get(category, ['Payment'])
            description = f"{random.choice(description_options)} - {category}"
            
            Transaction.objects.create(
                user=user,
                amount=amount,
                category=category,
                date=transaction_date,
                description=description
            )
            
            transactions_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {transactions_created} transactions for {username}')
        )