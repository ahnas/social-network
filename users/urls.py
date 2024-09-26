from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('signupf/', signup_view, name='signupf'),
    path('', login_view, name='loginf'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('search/', user_search, name='user_search'), 
]
