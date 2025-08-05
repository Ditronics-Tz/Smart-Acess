
from django.core.mail import send_mail

def send_otp_email(recipient_email, otp_code):
    subject = "Your SmartCampus OTP Code"
    message = f"Your one-time password (OTP) is: {otp_code}. It will expire in 5 minutes."
    from_email = "no-reply@smartcampus.com"

    send_mail(subject, message, from_email, [recipient_email])
