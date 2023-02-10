from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import RerunsFeed


class RerunsFeedSerializer(serializers.Serializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = RerunsFeed
        fields = [
            'id',
            'owner',
            'creation_date',
            'active',
            'source_url',
            'source_title',
            'task'
        ]

class UserSerializer(serializers.HyperlinkedModelSerializer):
    feeds = serializers.HyperlinkedRelatedField(
        many=True, view_name="feeds-detail", read_only=True
    )

    class Meta:
        model = User
        fields = ("url", "id", "username", "feeds")