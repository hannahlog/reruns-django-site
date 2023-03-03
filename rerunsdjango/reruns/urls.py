from django.urls import path
from . import views

app_name = "reruns"

urlpatterns = [
    path('', views.index, name='index'),
    path('user/', views.feed_by_user, name='feed_by_user'),
    path('add/', views.add, name='add'),
    path('<int:feed_id>/', views.detail, name='detail'),
    path('<int:feed_id>/edit/', views.edit, name='edit'),
    path('<int:feed_id>/delete/', views.delete, name='delete'),

]

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