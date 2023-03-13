from .models import Room, RoomUsers
from authentication.models import User
from rest_framework import serializers
from django.utils.text import slugify

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['name', 'slug', 'admin']

    def create(self, validated_data):
        pre_slug = validated_data.pop('slug', None)
        instance = self.Meta.model(**validated_data)
        lower = pre_slug.lower()
        instance.slug = lower.replace(" ", "")
        instance.save()
        return instance
    
class RoomUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomUsers
        fields = ['room', 'user', 'sentiment']

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance
    
    def update(self, instance, vaildated_data):
        sentiment = vaildated_data.pop('sentiment', vaildated_data.get('sentiment', instance.sentiment))
        instance.room = vaildated_data.get('room', instance.room)
        instance.user = vaildated_data.get('user', instance.user)
        instance.sentiment = sentiment
        instance.save()
        return instance