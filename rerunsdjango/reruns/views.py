from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.core.exceptions import FieldDoesNotExist

from .models import RerunsFeed
from .forms import RerunsFeedAddForm, RerunsFeedUpdateForm

DATETIME_FIELDS = {
    "start_time",
    "last_task_run",
    "next_task_run",
    "created"
}

LISTVIEW_FIELDS = [
    "title",
    "contents",
    "source_url",
    "created",
    "last_task_run",
    "next_task_run",
    "owner",
]

class VerboseMixin(object):
    def get_context_data(self, **kwargs):
        """."""
        context = super(VerboseMixin, self).get_context_data(**kwargs)
        context["meta"] = RerunsFeed._meta
        context["datetime_fields"] = DATETIME_FIELDS
        return context

class IndexView(VerboseMixin, generic.ListView):
    template_name = 'reruns/index.html'
    context_object_name = 'latest_feeds_list'
    fields = LISTVIEW_FIELDS

    def get_queryset(self):
        """Return the last added or last updated feeds."""

        order_by = _order_by(self.request.GET.get("order_by"))
        return RerunsFeed.objects.order_by(order_by)[:50]

    def get_context_data(self, **kwargs):
        """."""
        context = super(IndexView, self).get_context_data(**kwargs)
        context["fields"] = self.fields
        return context

class UserFeedsList(VerboseMixin, generic.ListView):
    model = RerunsFeed
    template_name = 'reruns/feeds_by_user.html'
    context_object_name = 'feeds_by_user'

    def get_queryset(self):
        order_by = _order_by(self.request.GET.get("order_by"))
        return RerunsFeed.objects \
            .filter(owner=self.kwargs['pk']) \
            .order_by(order_by)[:50]

    def get_context_data(self, **kwargs):
        """."""
        context = super(UserFeedsList, self).get_context_data(**kwargs)
        context["fields"] = LISTVIEW_FIELDS
        return context

class DetailView(VerboseMixin, generic.DetailView):
    model = RerunsFeed
    template_name = 'reruns/detail.html'
    fields = [
        "title",
        "id",
        "owner",
        "created",
        "source_url",
        "contents",
        "feed_type",
        "interval",
        "entries_per_update",
        "title_prefix",
        "title_suffix",
        "entry_title_prefix",
        "entry_title_suffix",
        "entry_order",
        "run_forever",
        "active",
        "start_time",
        "last_task_run",
        "next_task_run",
        "task_run_count",
    ]
    def get_context_data(self, **kwargs):
        """Add the user's username as extra context."""
        context = super(DetailView, self).get_context_data(**kwargs)
        context["fields"] = self.fields
        return context

class CreateView(PermissionRequiredMixin, generic.CreateView):
    permission_required = "reruns.add_rerunsfeed"
    model = RerunsFeed
    # fields = [
    #     "source_url",
    #     "interval",
    #     "interval_unit",
    #     "entries_per_update",
    #     "start_time",
    #     "use_timezone",
    #     "title_prefix",
    #     "title_suffix",
    #     "entry_title_prefix",
    #     "entry_title_suffix",
    #     "entry_order",
    #     "run_forever",
    #     "active",
    # ]
    form_class = RerunsFeedAddForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
        #obj = form.save(commit=False)
        #obj.owner = self.request.user
        #obj.save()
        #return HttpResponseRedirect(obj.get_absolute_url())


class UpdateView(PermissionRequiredMixin, generic.UpdateView):
    permission_required = "reruns.update_rerunsfeed"
    model = RerunsFeed
    template_name = 'reruns/rerunsfeed_update.html'
    form_class = RerunsFeedUpdateForm


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
    return HttpResponse(feed.contents, content_type='application/xml')


def _order_by(name):
    """"""
    try:
        field = RerunsFeed._meta.get_field(name)
        return "-" + field.name
    except FieldDoesNotExist:
        return "-last_task_run"
