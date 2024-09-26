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

logger = logging.getLogger(__name__)

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
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
                
                return redirect('profile') 
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


@api_view(['GET'])
def user_search(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(email__icontains=query)
    
    paginator = Paginator(users, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return Response({
        'results': [{'email': user.email,} for user in page_obj],
        'count': paginator.count,
        'next': page_obj.has_next(),
        'previous': page_obj.has_previous()
    })