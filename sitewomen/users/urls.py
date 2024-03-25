from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy
from . import views
from .views import UserResetView, UserPasswordResetConfirm

app_name = "users"

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),# http://127.0.0.1:8000
    path('password-change/',views.UserPasswordChange.as_view(),name = 'password_change'),
    path('password-change/done/',PasswordChangeView.as_view(template_name='users/password_change_done.html'),name = 'password_change_done'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('profile/', views.ProfileUser.as_view(), name='profile'),
    path('password-reset/',UserResetView.as_view(template_name='users/password_reset.html',email_template_name='users/password_reset_email.html',success_url=reverse_lazy("users:password_reset_done")),name='password_reset'),
    path('password-reset/done/',PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),name='password_reset_done'),
    path('password-reset/<token>/',UserPasswordResetConfirm.as_view(),name='password_reset_confirm'),
    path('password-reset/complete',PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),name = 'password_reset_complete')
]
