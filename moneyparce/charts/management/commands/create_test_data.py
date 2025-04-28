from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from charts.models import Transaction
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Creates test transaction data for a user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='testuser', help='Username to create data for')
        parser.add_argument('--count', type=int, default=200, help='Number of transactions to create')
        parser.add_argument('--months', type=int, default=12, help='Number of months of history to create')

    def handle(self, *args, **options):
        username = options['username']
        count = options['count']
        months = options['months']
        
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
        start_date = end_date - timedelta(days=30 * months) 
        
        Transaction.objects.filter(user=user).delete()
        
        # create varying patterns by month to make the graph less linear
        monthly_multipliers = {}
        for m in range(months + 1):
            # create some rand variation in monthly spending
            monthly_multipliers[m] = random.uniform(0.7, 1.3)
        
        for _ in range(count):
            # rand date within the range
            days_offset = random.randint(0, (end_date - start_date).days)
            transaction_date = start_date + timedelta(days=days_offset)
            
            month_offset = (transaction_date.year - start_date.year) * 12 + transaction_date.month - start_date.month
            month_multiplier = monthly_multipliers.get(month_offset, 1.0)
            
            category = random.choice(categories)
            
            # base amount varies by category
            base_amounts = {
                'Food': random.uniform(5, 30),
                'Groceries': random.uniform(20, 100),
                'Dining': random.uniform(15, 80),
                'Transportation': random.uniform(10, 50),
                'Entertainment': random.uniform(15, 60),
                'Housing': random.uniform(500, 1200),
                'Utilities': random.uniform(30, 150),
                'Shopping': random.uniform(20, 200),
                'Health': random.uniform(15, 100),
                'Travel': random.uniform(50, 500),
                'Education': random.uniform(20, 200),
                'Subscriptions': random.uniform(5, 20)
            }
            
            # get base amount for this category
            base_amount = base_amounts.get(category, random.uniform(10, 100))
            
            amount = round(base_amount * month_multiplier, 2)

            day_of_month = transaction_date.day
            if day_of_month < 5 or day_of_month > 25:
                if random.random() < 0.6:
                    extra_category = random.choice(categories)
                    extra_amount = round(base_amounts.get(extra_category, random.uniform(10, 100)) * month_multiplier, 2)
                    
                    descriptions = self.get_description_options(extra_category)
                    description = f"{random.choice(descriptions)} - {extra_category}"
                    
                    Transaction.objects.create(
                        user=user,
                        amount=extra_amount,
                        category=extra_category,
                        date=transaction_date,
                        description=description
                    )
                    transactions_created += 1
            
            descriptions = self.get_description_options(category)
            description = f"{random.choice(descriptions)} - {category}"
            
            Transaction.objects.create(
                user=user,
                amount=amount,
                category=category,
                date=transaction_date,
                description=description
            )
            
            transactions_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {transactions_created} transactions spanning {months} months for {username}')
        )
    
    def get_description_options(self, category):
        descriptions = {
            'Food': ['Lunch', 'Dinner', 'Breakfast', 'Coffee', 'Snacks', 'Food Delivery'],
            'Groceries': ['Supermarket', 'Farmers Market', 'Grocery Store', 'Organic Store', 'Butcher', 'Bakery'],
            'Dining': ['Restaurant', 'Fast Food', 'Takeout', 'Cafe', 'Pizza', 'Sushi'],
            'Transportation': ['Gas', 'Bus Fare', 'Uber', 'Taxi', 'Train Ticket', 'Car Maintenance'],
            'Entertainment': ['Movies', 'Concert', 'Streaming Service', 'Game', 'Theater', 'Museum'],
            'Housing': ['Rent', 'Mortgage', 'Home Repairs', 'Furniture', 'Cleaning Service', 'Property Tax'],
            'Utilities': ['Electricity', 'Water', 'Internet', 'Phone', 'Gas', 'Trash Service'],
            'Shopping': ['Clothes', 'Electronics', 'Home Goods', 'Gifts', 'Books', 'Online Purchase'],
            'Health': ['Pharmacy', 'Doctor Visit', 'Gym', 'Dental', 'Health Insurance', 'Vitamins'],
            'Travel': ['Flight', 'Hotel', 'Car Rental', 'Vacation', 'Travel Insurance', 'Resort'],
            'Education': ['Books', 'Tuition', 'Course Fee', 'Supplies', 'Software', 'Workshop'],
            'Subscriptions': ['Netflix', 'Spotify', 'Amazon Prime', 'Software', 'Magazine', 'Gym Membership']
        }
        
        return descriptions.get(category, ['Payment'])
