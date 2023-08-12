from celery import task
from django.core.mail import send_mail
from datetime import datetime, timedelta
from .models import RoomReservation

@task
def send_reminder_emails():
    tomorrow = datetime.now() + timedelta(days=1)
    reservations = RoomReservation.objects.filter(start_time__date=tomorrow.date())

   # Send reminder emails to each team member
    for reservation in reservations:
        team = reservation.team
        members = team.members.all()

        subject = f'Reservation Reminder for Team: {team.name}'
        message = f'Dear team members of {team.name},\n\nThis is a reminder for your reservation on {reservation.start_time}.\n\nBest regards,\nThe Reservation Team'

        for member in members:
            send_mail(subject, message, 'testusing11@gmail.com', [member.email])
