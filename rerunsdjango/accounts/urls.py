from django.urls import include, path

from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name="login"),
    path('change-password/', auth_views.PasswordChangeView.as_view()),
    # Disabled -- registration is invitation-only
    # (Any invited friends or family can register, but no one else)
    # path('register/', views.SignUpView.as_view(), name='register'),
    path("", views.UserListView.as_view(), name='users'),
    path("<int:pk>/", views.UserProfileDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.UserProfileUpdateView.as_view(), name='edit'),
]
