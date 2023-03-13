from .models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # Hashes Password and adds to database
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, vaildated_data):
        name = vaildated_data.pop('name', None)
        email = vaildated_data.pop('email', None)
        password = vaildated_data.pop('password', None)

        if name != instance.name:
            instance.name = name
        elif email != instance.email:
            instance.email = email
        elif not instance.check_password(password):
            instance.set_password(password)

        instance.save()
        return instance