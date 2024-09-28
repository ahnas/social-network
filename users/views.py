from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .forms import AcceptFriendRequestForm
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
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.views.decorators.http import require_POST
from rest_framework.permissions import IsAuthenticated


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
    incoming_friend_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
    return render(request, 'profile.html', {
        'email': email,
        'incoming_requests_count': incoming_friend_requests.count(),
        'incoming_requests': incoming_friend_requests
    })

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
        status = request.POST.get('status')
        from_user = get_object_or_404(User, email=from_email)
        to_user = get_object_or_404(User, email=to_email)

        now = timezone.now()
        one_minute_ago = now - timedelta(minutes=1)

        sent_requests_count = FriendRequest.objects.filter(
            from_user=from_user,
            created_at__gte=one_minute_ago
        ).count()

        if sent_requests_count >= 3:
            return JsonResponse({'error': 'You can only send 3 friend requests per minute.'}, status=400)
        with transaction.atomic():
            existing_request = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).first()
            if existing_request:
                return JsonResponse({'message': 'Friend request already sent.'}, status=400)
            friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user, status=status)

        return JsonResponse({'message': 'Friend request sent successfully!'})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    

class AcceptFriendRequestFormView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, request_id):
        # Retrieve the friend request by ID and ensure it's for the authenticated user
        friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
        
        # Update the friend request with the new data (rejected or accepted)
        form = AcceptFriendRequestForm(request.data, instance=friend_request)
    
        if form.is_valid():
            # Save the updated friend request
            friend_request = form.save()
            serializer = FriendRequestSerializer(friend_request)

            # Return the response
            return Response({
                "message": "Friend request updated successfully.",
                "friend_request": serializer.data
            }, status=status.HTTP_200_OK)

        # Return form errors if the data is invalid
        return Response({
            "errors": form.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    
    

class AllRequest(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Debugging: Print the authenticated user's email
        print(f"Authenticated user: {request.user.email}")

        # Retrieve all incoming friend requests for the authenticated user
        incoming_requests = FriendRequest.objects.all()

        # Debugging: Print incoming requests
        print(f"Incoming requests: {incoming_requests}")

        # Serialize the incoming friend requests
        incoming_serializer = FriendRequestSerializer(incoming_requests, many=True)

        # Return the serialized data in the response
        return Response({
            "incoming_requests": incoming_serializer.data
        }, status=status.HTTP_200_OK)