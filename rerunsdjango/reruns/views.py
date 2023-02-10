from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, generics, permissions


from .models import RerunsFeed
from .serializers import RerunsFeedSerializer, UserSerializer
from .permissions import IsOwnerOrReadOnly

# Create your views here.



class RerunsFeedViewSet(viewsets.ModelViewSet):

    serializer_class = RerunsFeedSerializer
    queryset = RerunsFeed.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if instance.task is not None:
            instance.task.delete()
        return super().perform_destroy(instance)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer



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

@login_required()
def add(request):
    if request.method == 'POST':
        form = PollAddForm(request.POST)
        if form.is_valid:
            poll = form.save(commit=False)
            poll.owner = request.user
            poll.save()
            new_choice1 = Choice(
                poll=poll, choice_text=form.cleaned_data['choice1']).save()
            new_choice2 = Choice(
                poll=poll, choice_text=form.cleaned_data['choice2']).save()

            messages.success(
                request, "Poll & Choices added successfully.", extra_tags='alert alert-success alert-dismissible fade show')

            return redirect('polls:list')
    else:
        form = PollAddForm()
    context = {
        'form': form,
    }
    return render(request, 'reruns/add.html', context)

def edit(request, feed_id):
    pass

def delete(request, feed_id):
    pass

    # path('user/', views.feed_by_user, name='feed_by_user'),
    # path('add/', views.add, name='add'),
    # path('<int:feed_id>/', views.detail, name='detail'),
    # path('<int:feed_id>/edit/', views.edit, name='edit'),
    # path('<int:feed_id>/delete/', views.delete, name='delete'),
