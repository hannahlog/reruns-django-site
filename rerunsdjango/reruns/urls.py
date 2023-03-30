from django.urls import path
from . import views

app_name = "reruns"

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('by-user/<int:pk>', views.UserFeedsList.as_view(), name='feeds_by_user'),
    path('add/', views.CreateView.as_view(), name='create'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.UpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.DeleteView.as_view(), name='delete'),
    path('<int:pk>/feed.xml', views.feed, name='feed'),
]
