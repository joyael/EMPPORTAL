# utils.py
import jwt
import datetime
from django.conf import settings
from .models import RefreshToken

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