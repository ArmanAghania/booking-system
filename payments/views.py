from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Payment, WalletTransaction
from appointments.models import Appointment
from accounts.models import User
from decimal import Decimal
import uuid


@login_required
def wallet_detail(request):
    """Display user's wallet balance and transaction history."""
    user = request.user

    # Get recent wallet transactions
    transactions = WalletTransaction.objects.filter(user_id=user).order_by(
        "-created_at"
    )[:10]

    context = {
        "user": user,
        "transactions": transactions,
        "balance": user.wallet_balance,
    }
    return render(request, "payments/wallet_detail.html", context)


@login_required
def deposit_funds(request):
    """Handle wallet deposit."""
    if request.method == "POST":
        amount = request.POST.get("amount")
        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect("payments:wallet_detail")

            # Add funds to wallet
            with transaction.atomic():
                user = request.user
                user.wallet_balance += amount
                user.save()

                # Create wallet transaction record
                WalletTransaction.objects.create(
                    user_id=user,
                    transaction_type=WalletTransaction.DEPOSIT,
                    amount=amount,
                    description=f"Deposit of ${amount}",
                    balance_after=user.wallet_balance,
                )

                messages.success(
                    request, f"Successfully deposited ${amount} to your wallet."
                )
                return redirect("payments:wallet_detail")

        except (ValueError, TypeError):
            messages.error(request, "Invalid amount entered.")
            return redirect("payments:wallet_detail")

    return render(request, "payments/deposit.html")


@login_required
def withdraw_funds(request):
    """Handle wallet withdrawal."""
    if request.method == "POST":
        amount = request.POST.get("amount")
        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect("payments:wallet_detail")

            if amount > request.user.wallet_balance:
                messages.error(request, "Insufficient funds in wallet.")
                return redirect("payments:wallet_detail")

            # Withdraw funds from wallet
            with transaction.atomic():
                user = request.user
                user.wallet_balance -= amount
                user.save()

                # Create wallet transaction record
                WalletTransaction.objects.create(
                    user_id=user,
                    transaction_type=WalletTransaction.WITHDRAW,
                    amount=amount,
                    description=f"Withdrawal of ${amount}",
                    balance_after=user.wallet_balance,
                )

                messages.success(
                    request, f"Successfully withdrew ${amount} from your wallet."
                )
                return redirect("payments:wallet_detail")

        except (ValueError, TypeError):
            messages.error(request, "Invalid amount entered.")
            return redirect("payments:wallet_detail")

    return render(request, "payments/withdraw.html")


@login_required
def payment_history(request):
    """Display payment history for the user."""
    payments = (
        Payment.objects.filter(appointment_id__patient=request.user)
        .select_related("appointment_id__doctor__user")
        .order_by("-created_at")
    )

    context = {
        "payments": payments,
    }
    return render(request, "payments/payment_history.html", context)


@login_required
def view_transactions(request):
    """Display all wallet transactions for the user."""
    transactions = WalletTransaction.objects.filter(user_id=request.user).order_by(
        "-created_at"
    )

    context = {
        "transactions": transactions,
    }
    return render(request, "payments/view_transactions.html", context)


@login_required
def process_payment(request, appointment_id):
    """Process payment for an appointment."""
    appointment = get_object_or_404(
        Appointment, id=appointment_id, patient=request.user
    )

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method == "wallet":
            # Process wallet payment
            if request.user.wallet_balance >= appointment.consultation_fee:
                with transaction.atomic():
                    # Deduct from wallet
                    user = request.user
                    user.wallet_balance -= appointment.consultation_fee
                    user.save()

                    # Create payment record
                    payment = Payment.objects.create(
                        appointment_id=appointment,
                        amount=appointment.consultation_fee,
                        status=Payment.SUCCESS,
                    )

                    # Create wallet transaction
                    WalletTransaction.objects.create(
                        user_id=user,
                        transaction_type=WalletTransaction.WITHDRAW,
                        amount=appointment.consultation_fee,
                        description=f"Payment for appointment with Dr. {appointment.doctor.user.get_full_name()}",
                        balance_after=user.wallet_balance,
                        appointment_id=appointment,
                    )

                    # Update appointment status
                    appointment.status = "CONFIRMED"
                    appointment.save()

                    messages.success(
                        request,
                        "Payment successful! Your appointment has been confirmed.",
                    )
                    return redirect(
                        "appointments:booking_confirmation",
                        appointment_id=appointment.id,
                    )
            else:
                messages.error(
                    request,
                    "Insufficient funds in wallet. Please add funds or use another payment method.",
                )
                return redirect("payments:wallet_detail")

        elif payment_method == "card":
            # For now, simulate card payment success
            with transaction.atomic():
                payment = Payment.objects.create(
                    appointment_id=appointment,
                    amount=appointment.consultation_fee,
                    status=Payment.SUCCESS,
                )

                appointment.status = "CONFIRMED"
                appointment.save()

                messages.success(
                    request, "Payment successful! Your appointment has been confirmed."
                )
                return redirect(
                    "appointments:booking_confirmation", appointment_id=appointment.id
                )

    context = {
        "appointment": appointment,
        "user_balance": request.user.wallet_balance,
    }
    return render(request, "payments/process_payment.html", context)
