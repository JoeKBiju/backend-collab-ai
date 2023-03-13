from django.urls import path
from .views import get_rooms, create_room, get_messages, add_users, room_users

urlpatterns = [
    path('rooms', get_rooms),
    path('create-room', create_room),
    path('get-messages', get_messages),
    path('add-users', add_users),
    path('room-users', room_users)
]