from django.contrib import admin
from payments.models import Payment, WalletTransaction

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['user_id_id','amount', 'transaction_type', 'balance_after']
    list_filter = ['transaction_type']
    search_fields = ['transaction_type']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'amount', 'status']
    search_fields = ['appointment_id']