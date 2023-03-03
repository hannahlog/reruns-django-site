from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.shortcuts import get_object_or_404, render


from .models import RerunsFeed

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'reruns/index.html'
    context_object_name = 'latest_feeds_list'

    def get_queryset(self):
        """Return the last five added feeds."""
        return RerunsFeed.objects.order_by('-creation_date')[:5]

class DetailView(generic.DetailView):
    model = RerunsFeed
    template_name = 'reruns/detail.html'


# def index(request):
#     return HttpResponse("Hello, world! This is the reruns index.")


# def detail(request, feed_id):
#     pass


def user(request):
    pass

def add(request):
    pass

def edit(request, feed_id):
    pass

def delete(request, feed_id):
    pass

    # path('user/', views.feed_by_user, name='feed_by_user'),
    # path('add/', views.add, name='add'),
    # path('<int:feed_id>/', views.detail, name='detail'),
    # path('<int:feed_id>/edit/', views.edit, name='edit'),
    # path('<int:feed_id>/delete/', views.delete, name='delete'),
