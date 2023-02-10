from django.urls import path, include
from rest_framework import routers
from . import views

# app_name = "reruns"


    # path("snippets/", views.SnippetList.as_view(), name="snippet-list"),
    # path("snippets/<int:pk>/", views.SnippetDetail.as_view(), name="snippet-detail"),
    # path(
    #     "snippets/<int:pk>/highlight/",
    #     views.SnippetHighlight.as_view(),
    #     name="snippet-highlight",
    # ),  # new
    # path("users/", views.UserList.as_view(), name="user-list"),
    # path("users/<int:pk>/", views.UserDetail.as_view(), name="user-detail"),
    # path("", views.api_root),


# Create a router and register our viewsets with it.
router = routers.DefaultRouter()
router.register(r'feeds', views.RerunsFeedViewSet,basename="feed")
router.register(r'users', views.UserViewSet,basename="user")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]


# urlpatterns = [
#     #path('reruns/', views.feed_list),
#     #path('reruns/<int:pk>/', views.feed_detail),
#     path('', views.api_root),
#     #path('user/', views.feed_by_user, name='feed_by_user'),
#     #path('add/', views.add, name='add'),
#     #path('<int:feed_id>/', views.detail, name='detail'),
#     #path('<int:feed_id>/edit/', views.edit, name='edit'),
#     #path('<int:feed_id>/delete/', views.delete, name='delete'),
#     path('users/', views.UserList.as_view()),
#     path('users/<int:pk>/', views.UserDetail.as_view()),
# ]

# urlpatterns = [
#     # ex: /polls/
#     path('', views.index, name='index'),
#     # ex: /polls/5/
#     path('<int:question_id>/', views.detail, name='detail'),
#     # ex: /polls/5/results/
#     path('<int:question_id>/results/', views.results, name='results'),
#     # ex: /polls/5/vote/
#     path('<int:question_id>/vote/', views.vote, name='vote'),
# ]

# urlpatterns = [
#     path('list/', views.polls_list, name='list'),
#     path('list/user/', views.list_by_user, name='list_by_user'),
#     path('add/', views.polls_add, name='add'),
#     path('edit/<int:poll_id>/', views.polls_edit, name='edit'),
#     path('delete/<int:poll_id>/', views.polls_delete, name='delete_poll'),
#     path('end/<int:poll_id>/', views.endpoll, name='end_poll'),
#     path('edit/<int:poll_id>/choice/add/', views.add_choice, name='add_choice'),
#     path('edit/choice/<int:choice_id>/', views.choice_edit, name='choice_edit'),
#     path('delete/choice/<int:choice_id>/',
#          views.choice_delete, name='choice_delete'),
#     path('<int:poll_id>/', views.poll_detail, name='detail'),
#     path('<int:poll_id>/vote/', views.poll_vote, name='vote'),
# ]