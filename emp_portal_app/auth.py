
from django.http import JsonResponse
from django.conf import settings

from emp_portal_app.utils import check_refresh_token, create_access_token, create_refresh_token, insert_refresh_token, is_refresh_token_active, make_refresh_token_inactive

from .models import Permission, Employee
import jwt


def get_current_user(request):
    access_token = request.COOKIES.get('access_token')
    if not access_token:
        return JsonResponse({'error': 'Access token not found'}, status=401)

    try:
        # Decode the access token
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user = Employee.objects.get(employee_id=user_id)  #user retrieving
    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'Access token has expired'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Invalid access token'}, status=401)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'User  not found'}, status=404)

    return user  # Return the user object if everything is fine

def role_required(request, permission_name):
    user = get_current_user(request)

    if isinstance(user, JsonResponse):
        return user  # Return the error response directly

    permission = Permission.objects.filter(name=permission_name).first()
    if permission is None:
        return JsonResponse({'error': 'Permission not found'}, status=404)

    if int(user.role) > permission.level:  
        return JsonResponse({'error': 'Not enough permissions'}, status=403)
    
    refresh_token = request.COOKIES.get('refresh_token')  # Get the refresh token from the cookie

    if not refresh_token:
        return user
    if check_refresh_token(refresh_token):
        if not is_refresh_token_active(refresh_token):
            return user
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            user = Employee.objects.get(employee_id=user_id)

            # Generate a new access token
            new_access_token = create_access_token(user)
            
            # Set the new access token as a cookie
            response = JsonResponse({'message': 'Access token refreshed successfully'})
            response.set_cookie('access_token', new_access_token, httponly=True, secure=True)  # Set the access token cookie

            return user
        except jwt.ExpiredSignatureError:
            return user
        except jwt.InvalidTokenError:
            return user

    return user  # Return the user object if they have the required permissions