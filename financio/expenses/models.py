from django.db import models

from users.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Expense(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='expenses_by_category')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_expenses')

    def __str__(self):
        return self.title
