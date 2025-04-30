# utils.py
import jwt
import datetime
from django.conf import settings
from .models import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator


def create_access_token(user):
    payload = {
        'user_id': user.employee_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),  # Token expires in 15 minutes
        'iat': datetime.datetime.utcnow()  # Issued at
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def create_refresh_token(user):
    payload = {
        'user_id': user.employee_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),  # Refresh token expires in 7 days
        'iat': datetime.datetime.utcnow()  # Issued at
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def insert_refresh_token(refresh_token):
    new_token = RefreshToken(token=refresh_token)
    new_token.save()

def check_refresh_token(token_to_check):
    token_exists = RefreshToken.objects.filter(token=token_to_check).exists()
    return token_exists

def make_refresh_token_inactive(refresh_token):
    if check_refresh_token(refresh_token):
        token_instance = RefreshToken.objects.get(token=refresh_token)
        token_instance.is_active = False
        token_instance.save()

def is_refresh_token_active(refresh_token):
    if check_refresh_token(refresh_token):
        token_instance = RefreshToken.objects.get(token=refresh_token)
        return token_instance.is_active
    else:
        return False
    

def convert_to_decimal_hours(hours, minutes, seconds):
    decimal_minutes = minutes / 60
    decimal_seconds = seconds / 3600
    total_hours = hours + decimal_minutes + decimal_seconds
    return round(total_hours, 2)


class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.email}"

token_generator = CustomTokenGenerator()
