from django.contrib.auth import authenticate, login
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import IntegrityError
from .models import User, Student
import json
import secrets


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('firstName')
            last_name = data.get('lastName')

            # Validate required fields
            if not all([username, email, password, first_name, last_name]):
                return JsonResponse({
                    'message': 'All fields are required'
                }, status=400)

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'message': 'Email already registered'
                }, status=400)

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'message': 'Username already taken'
                }, status=400)

            # Create user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                username=username,  # Save the username
                type='S'  # Student by default
            )

            # Create student profile
            Student.objects.create(user=user, is_verified=False)

            # Generate simple token
            token = secrets.token_urlsafe(32)

            return JsonResponse({
                'message': 'Registration successful',
                'token': token,
                'userId': user.user_id,
                'email': user.email,
                'username': user.username,
                'firstName': user.first_name,
                'lastName': user.last_name,
                'userType': user.type
            }, status=201)

        except IntegrityError as e:
            return JsonResponse({
                'message': 'User already exists'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'message': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username_or_email = data.get('username')
            password = data.get('password')

            if not username_or_email or not password:
                return JsonResponse({
                    'message': 'Username/Email and password are required'
                }, status=400)

            # Try to find user by username or email
            user = None

            # First, try to find by username
            try:
                user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                # If not found by username, try email
                try:
                    user = User.objects.get(email=username_or_email)
                except User.DoesNotExist:
                    pass

            # If still no user found, return error
            if user is None:
                return JsonResponse({
                    'message': 'Invalid credentials'
                }, status=401)

            # Authenticate user (Django's authenticate needs the USERNAME_FIELD which is email)
            authenticated_user = authenticate(
                request,
                username=user.email,  # Use email for authentication
                password=password
            )

            if authenticated_user is None:
                return JsonResponse({
                    'message': 'Invalid credentials'
                }, status=401)

            # Check if user is a student and verified
            if authenticated_user.type == 'S':
                try:
                    student = Student.objects.get(user=authenticated_user)
                    if not student.is_verified:
                        return JsonResponse({
                            'message': 'Account is pending verification'
                        }, status=403)
                except Student.DoesNotExist:
                    return JsonResponse({
                        'message': 'Student profile not found'
                    }, status=404)

            # Log the user in (creates session)
            login(request, authenticated_user)

            # Generate simple token
            token = secrets.token_urlsafe(32)

            return JsonResponse({
                'message': 'Login successful',
                'token': token,
                'userId': authenticated_user.user_id,
                'email': authenticated_user.email,
                'username': authenticated_user.username,
                'firstName': authenticated_user.first_name,
                'lastName': authenticated_user.last_name,
                'userType': authenticated_user.type
            }, status=200)

        except Exception as e:
            return JsonResponse({
                'message': str(e)
            }, status=500)