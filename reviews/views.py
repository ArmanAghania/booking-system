# reviews/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from .forms import ReviewForm
from .models import Review
from appointments.models import Appointment  # Make sure the Appointment model exists


@login_required
def submit_review(request, appointment_id):
    """
    View for a patient to submit a review for a completed appointment.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # --- Security and Business Logic Checks ---

    # 1. Check if the logged-in user is the patient for this appointment.
    if appointment.patient != request.user:
        messages.error(request, "You are not authorized to review this appointment.")
        return HttpResponseForbidden("You can only review your own appointments.")

    # 2. Check if the appointment status is 'COMPLETED'.
    if appointment.status != Appointment.AppointmentStatus.COMPLETED:
        messages.warning(request, "You can only review appointments that have been completed.")
        return redirect('core:home')  # Redirect to home or another appropriate page

    # 3. Check if a review for this appointment already exists.
    if hasattr(appointment, 'review'):
        messages.info(request, "You have already submitted a review for this appointment.")
        return redirect('doctors:doctor_detail', pk=appointment.doctor.pk)

    # --- Form Processing ---

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.appointment = appointment
            review.patient = request.user
            review.doctor = appointment.doctor
            review.save()

            messages.success(request,
                             f"Thank you! Your review for Dr. {appointment.doctor.user.get_full_name()} has been submitted.")
            return redirect('doctors:doctor_detail', pk=appointment.doctor.pk)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'appointment': appointment
    }
    return render(request, 'reviews/submit_review.html', context)