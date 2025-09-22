from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("wallet/", views.wallet_detail, name="wallet_detail"),
    path("deposit/", views.deposit_funds, name="deposit_funds"),
    path("withdraw/", views.withdraw_funds, name="withdraw_funds"),
    path("history/", views.payment_history, name="payment_history"),
    path("transactions/", views.view_transactions, name="view_transactions"),
    path(
        "process/<int:appointment_id>/", views.process_payment, name="process_payment"
    ),
]
