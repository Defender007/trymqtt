from django.urls import path
from .views import (RegisterView,
                    LoginView, 
                    UserView, 
                    LogoutView,
                    UserProfileView, 
                    UploadProfileImageView,)

urlpatterns = [
    path('register', RegisterView.as_view(), name='register_api_view'),
    path('login', LoginView.as_view(), name='login_api_view'),
    path('user', UserView.as_view(), name='current_user_view'),
    path('logout', LogoutView.as_view(), name='logout_api_view'),
    path('profiles/users/<int:pk>', UserProfileView.as_view(), name='profile_get_update_delete_api_view'),
    path('profiles', UserProfileView.as_view(), name='profiles_list_create_api_view'),
    path('avatar', UploadProfileImageView.as_view(), name='avatar_api_view'),
]