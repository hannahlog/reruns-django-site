from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy

from .models import RerunsFeed


class IndexView(generic.ListView):
    template_name = 'reruns/index.html'
    context_object_name = 'latest_feeds_list'

    def get_queryset(self):
        """Return the last added or last updated feeds."""

        order_by = "-creation_date" \
                    if (self.request.GET.get("order_by") == "created") \
                    else "-last_updated"
        return RerunsFeed.objects.order_by(order_by)[:50]

class UserFeedsList(generic.ListView):
    model = RerunsFeed
    template_name = 'reruns/feeds_by_user.html'
    context_object_name = 'feeds_by_user'

    def get_queryset(self):
        return RerunsFeed.objects.filter(owner=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        """Add the user's username as extra context."""
        context = super(UserFeedsList, self).get_context_data(**kwargs)
        context['username'] = get_user_model().objects.get(pk=self.kwargs['pk'])
        return context

class DetailView(generic.DetailView):
    model = RerunsFeed
    template_name = 'reruns/detail.html'
    fields = [
        "source_url",
        "interval",
        "interval_unit",
        "entries_per_update",
        "start_time",
        "use_timezone",
        "title_prefix",
        "title_suffix",
        "entry_title_prefix",
        "entry_title_suffix",
        "entry_order",
        "run_forever",
        "active",
    ]

class CreateView(PermissionRequiredMixin, generic.CreateView):
    permission_required = "reruns.add_rerunsfeed"
    model = RerunsFeed
    fields = [
        "source_url",
        "interval",
        "interval_unit",
        "entries_per_update",
        "start_time",
        "use_timezone",
        "title_prefix",
        "title_suffix",
        "entry_title_prefix",
        "entry_title_suffix",
        "entry_order",
        "run_forever",
        "active",
    ]

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class UpdateView(PermissionRequiredMixin, generic.UpdateView):
    permission_required = "reruns.update_rerunsfeed"
    model = RerunsFeed
    fields = [
        "interval",
        "interval_unit",
        "entries_per_update",
        "start_time",
        "use_timezone",
        "title_prefix",
        "title_suffix",
        "entry_title_prefix",
        "entry_title_suffix",
        "entry_order",
        "run_forever",
        "active",
    ]


class DeleteView(PermissionRequiredMixin, generic.DeleteView):
    permission_required = "reruns.delete_rerunsfeed"
    model = RerunsFeed
    success_url = reverse_lazy('reruns:index')

    def get_queryset(self):
        # Limit the queryset to only the current user's RerunsFeeds.
        #
        # Without this override, it was previously possible for a non-super, non-staff
        # user to delete another user's RerunsFeed, despite it not being possible for
        # them to edit the same feed.
        #
        # Solution courtesy of
        # https://stackoverflow.com/questions/5531258/example-of-django-class-based-deleteview
        #
        # TODO: Determine why users could previously delete other user's RerunsFeeds
        # (before this fix was added), but couldn't update them? Despite both the
        # DeleteView and UpdateView using the same default permissions settings?
        owner = self.request.user
        return self.model.objects.filter(owner=owner)


def feed(request, pk):
    """Function-based view for accessing the feed itself (as XML)."""
    feed = get_object_or_404(RerunsFeed, pk=pk)
    return HttpResponse(feed.contents, content_type='text/xml')

