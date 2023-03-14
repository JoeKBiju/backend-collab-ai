from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User
from rest_framework.exceptions import AuthenticationFailed
import jwt
import datetime
import time

# Registers a user
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# Logs user in 
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('Invalid User')

        if (user.check_password(password)) == False:
            raise AuthenticationFailed('Invalid Password')

        payload = {
            'user': user.id,
            'iat': datetime.datetime.utcnow().timestamp(),
            'exp': (datetime.datetime.utcnow() + datetime.timedelta(hours=24)).timestamp()
        }

        encoded = jwt.encode(payload, 'secret', algorithm="HS256")

        response = Response()

        response.set_cookie(key = 'token', value = encoded, httponly = True, samesite='None', secure=True)

        response.data = {'token': encoded}
        time.sleep(1)
        return response
    
# Get user's details from cookie
@api_view()
def user_details(request):
    if request.method == 'POST':
        token = request.data['token']

        if token is None:
            raise AuthenticationFailed('User not logged in')
        
        try:
            data = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('User not logged in')
        
        user = User.objects.get(id=data['user'])
        serializer = UserSerializer(user)
        
        return Response(serializer.data)
    
# Logs out user
@api_view(['POST'])
def logout(request):
    if request.method == 'POST':
        response = Response()

        response.delete_cookie('token', samesite='None')

        response.data = {"message": "User logged out"}

        return response
    
# Changes name of user
@api_view(['PUT'])
def change_name(request):
    if request.method == 'PUT':
        id = request.data['id']
        name = request.data['name']
        user = User.objects.get(id=id)

        serializer = UserSerializer(user, data={'email': user.email, 'name': name, 'password': user.password})

        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data)
    
# Changes name of email
@api_view(['PUT'])
def change_email(request):
    if request.method == 'PUT':
        id = request.data['id']
        email = request.data['email']
        user = User.objects.get(id=id)

        serializer = UserSerializer(user, data={'email': email, 'name': user.name, 'password': user.password})

        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data)
    
# Changes name of password
@api_view(['PUT'])
def change_password(request):
    if request.method == 'PUT':
        id = request.data['id']
        password = request.data['password']
        user = User.objects.get(id=id)

        serializer = UserSerializer(user, data={'email': user.email, 'name': user.name, 'password': password})

        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data)