from django.shortcuts import render
from .models import Room, Message, RoomUsers
from authentication.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RoomSerializer, RoomUsersSerializer

# Gets all rooms
@api_view(['GET'])
def get_rooms(request):
    rooms = Room.objects.all()
    serilaized_data = RoomSerializer(rooms, many=True)
    return Response(serilaized_data.data)

# Creates a new room
@api_view(['POST'])
def create_room(request):
    if request.method == 'POST':
        serializer = RoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# Get stored messages in a room
@api_view(['POST'])
def get_messages(request):
    if request.method == 'POST':
        room = request.data['room']
        room_id = Room.objects.get(slug=room)
        messages = Message.objects.filter(room=room_id)
        json_list = []

        for message in messages:
            user = User.objects.get(email=message.author)
            json_obj = {
                'author': user.name,
                'content': message.message,
                'timestamp': message.timestamp.isoformat()
            }
            json_list.append(json_obj)

        return Response(json_list[-20:])

# Views users in a room
@api_view(['POST'])
def room_users(request):
    if request.method == 'POST':
        room = request.data['room']
        room_id = Room.objects.get(slug=room)
        users = RoomUsers.objects.filter(room=room_id)
        json_list = []

        for user in users:
            name = User.objects.get(id=user.id)
            dict = {
                'id': user.id,
                'name': name.name,
                'email': name.email,
                'sentiment': user.sentiment
            }
            json_list.append(dict)

        return Response(json_list)

# Adds users to a room
@api_view(['POST'])
def add_users(request):
    if request.method == 'POST':
        slug = request.data['room']
        email = request.data['email']

        room = Room.objects.get(slug=slug)
        user = User.objects.get(email=email)

        serializer = RoomUsersSerializer(data={'room': room.id, 'user': user.id, 'sentiment': 'dummy'})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer.data)

        return Response({'id': user.id, 'name': user.name, 'email': user.email, 'sentiment': 'dummy'})
        