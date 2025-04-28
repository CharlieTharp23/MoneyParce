from django.db import models
from django.contrib.auth.models import User

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField()  # 1-12 representing the months
    year = models.IntegerField()
    alert_percentage = models.IntegerField(default=80)  # this is an alert when spending reaches this % of budget
    
    class Meta:
        unique_together = ['user', 'category', 'month', 'year']
        
    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.amount} - {self.month}/{self.year}"