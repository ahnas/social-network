from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import *
from django.shortcuts import redirect, render
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
import logging
from rest_framework.decorators import api_view
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import *

logger = logging.getLogger(__name__)

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save() 
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Save tokens to the user instance
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.save()  # Save the user with tokens

            return Response({
                "message": "User created successfully",
                "access_token": access_token,
                "refresh_token": refresh_token
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        logger.debug(f"Request data: {request.data}") 
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email'] 
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                return Response({
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        logger.error(f"Validation errors: {serializer.errors}")  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def signup_view(request):
    return render(request, 'signup.html')

def login_view(request):
    return render(request, 'login.html')

@login_required
def profile_view(request):
    email = request.user.email
    return render(request, 'profile.html', {'email': email})

def logout_view(request):
    logout(request)
    return redirect('loginf')

@login_required
@api_view(['GET'])
def user_search(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(email__icontains=query)
    friendRequests = FriendRequest.objects.all()
    paginator = Paginator(users, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user_data = [{'email': user.email} for user in page_obj]
    friend_requests_data = [
        {
            'from_user': fr.from_user.email,
            'to_user': fr.to_user.email,
            'status': fr.status,
            'created_at': fr.created_at.isoformat(),  
        }
        for fr in friendRequests
    ]

    return Response({
        'results': user_data,
        'count': paginator.count,
        'next': page_obj.has_next(),
        'previous': page_obj.has_previous(),
        'friendRequests': friend_requests_data,
    })

@csrf_exempt
def send_friend_request(request):
    if request.method == "POST":
        from_email = request.POST.get('from_email')
        to_email = request.POST.get('to_email')

        # Get the sender (from_email) and recipient (to_email) users
        from_user = get_object_or_404(User, email=from_email)
        to_user = get_object_or_404(User, email=to_email)

        # Check if the friend request already exists
        existing_request = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).first()
        if existing_request:
            return JsonResponse({'message': 'Friend request already sent.'}, status=400)

        # Create a new friend request
        friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user, status='pending')

        return JsonResponse({'message': 'Friend request sent successfully!'})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)