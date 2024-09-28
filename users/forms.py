from django import forms
from .models import FriendRequest

class AcceptFriendRequestForm(forms.ModelForm):
    class Meta:
        model = FriendRequest
        fields = ['status',] 