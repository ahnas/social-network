from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import FriendRequest


User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(email=email, password=password)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user,
            'email': email,
            'password': password,
        }
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'is_active', 'is_staff'] 

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField(source='from_user.id', read_only=True)  # Foreign key ID for from_user
    to_user_id = serializers.IntegerField(source='to_user.id', read_only=True)      # Foreign key ID for to_user
    from_user_email = serializers.EmailField(source='from_user.email', read_only=True)  # Optional: include email if needed
    to_user_email = serializers.EmailField(source='to_user.email', read_only=True)      # Optional: include email if needed

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user_id', 'to_user_id', 'from_user_email', 'to_user_email', 'status', 'created_at']  # Including created_at

    def update(self, instance, validated_data):
        # Update the status or any other field you want
        instance.status = validated_data.get('status', instance.status)
        # You can add more fields to update here if needed

        instance.save()  # Save the updated instance
        return instance