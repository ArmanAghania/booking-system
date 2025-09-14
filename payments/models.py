import uuid
from django.db import models
from appointments.models import Appointment
from accounts.models import User


class Payment(models.Model):
    FILED = "failed"
    SUCCESS = 'success'
    STATUS_CHOICES = (
        (FILED, 'Filed'),
        (SUCCESS, 'Success'),
    )
    appointment_id = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False)
    paid_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WalletTransaction(models.Model):
    DEPOSIT = "deposit"
    WITHDRAW = 'withdraw'
    TYPE_CHOICES = (
        (DEPOSIT, 'Deposit'),
        (WITHDRAW, 'Withdraw'),
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    description = models.TextField()
    balance_after = models.DecimalField(decimal_places=2, max_digits=20)
    appointment_id = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)





