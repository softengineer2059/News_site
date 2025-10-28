from django.urls import path
from account import views


urlpatterns = [
    path('login/', views.Login.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path('register/', views.Register.as_view(), name="register"),
    path("profile/", views.Account.as_view(), name="profile"),
    path('change_base_info/', views.change_base_info, name='change_base_info'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('upload_avatar/', views.upload_avatar_image, name='upload_avatar')
]