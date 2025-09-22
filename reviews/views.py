# reviews/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from appointments.models import Appointment
from .forms import ReviewForm

@login_required
def submit_review(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    # Security checks
    if appointment.patient != request.user:
        return HttpResponseForbidden("You can only review your own appointments.")
    if appointment.status != 'COMPLETED':
        messages.error(request, "You can only review completed appointments.")
        return redirect('appointments:my_appointments')
    if hasattr(appointment, 'review'):
        messages.info(request, "You have already submitted a review for this appointment.")
        return redirect('doctors:doctor_detail', doctor_id=appointment.doctor.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.appointment = appointment
            review.save()
            messages.success(request, "Thank you! Your review has been submitted.")
            return redirect('doctors:doctor_detail', doctor_id=appointment.doctor.pk)
    else:
        form = ReviewForm()

    context = {'form': form, 'appointment': appointment}
    return render(request, 'reviews/submit_review.html', context)