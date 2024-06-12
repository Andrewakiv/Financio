from django.urls import path
from rest_framework.throttling import ScopedRateThrottle
from . import views


app_name = 'expenses'

urlpatterns = [
    path('add-expense/', views.CreateExpenseView.as_view(), name='add-expense'),
    path('expenses/<int:pk>/', views.ExpenseView.as_view(), name='expenses'),
]
