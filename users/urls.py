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
    path('accept_friend_request/<int:request_id>/', AcceptFriendRequestFormView.as_view(), name='accept_friend_request'),
    path('send_friend_request/', send_friend_request, name='send_friend_request'),
    path('friend_requests/', AllRequest.as_view(), name='all_friend_requests'),



]
