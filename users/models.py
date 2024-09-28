from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("The Email field is required")
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email=email, password=password)
        user.is_admin = True
        user.is_staff = True  
        user.is_superuser = True  
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):

    FRIEND_REQUEST_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)  
    is_superuser = models.BooleanField(default=True) 
    refresh_token = models.TextField(blank=True, null=True)  
    access_token = models.TextField(blank=True, null=True)   
    objects = UserManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class FriendRequest(models.Model):
    FRIEND_REQUEST_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('blocked', 'Blocked'),
    ]

    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=FRIEND_REQUEST_CHOICES,)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')  

    def reject(self):
        """Method to reject and delete the friend request."""
        self.status = 'rejected'
        self.save()
        self.delete()  # Delete the instance after saving the rejection

    def save(self, *args, **kwargs):
        """Custom save method to check status before saving."""
        if self.status == 'rejected':
            self.delete()  # Automatically delete if status is rejected
        else:
            super(FriendRequest, self).save(*args, **kwargs) 


    def __str__(self):
        return f"Friend request from {self.from_user.email} to {self.to_user.email} - Status: {self.status}"