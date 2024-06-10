from django.contrib import admin

from expenses.models import Category, Expense

admin.site.register(Category)
admin.site.register(Expense)
