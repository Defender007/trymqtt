from rest_framework.exceptions import NotFound
from django.core.exceptions import BadRequest
from rest_framework import serializers
from .models import User, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is  None:
            raise BadRequest('Password is required!')
        instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = instance.first_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance
    
class UserProfileSerializer(serializers.ModelSerializer):
    # first_name = serializers.CharField(required=True)
    # last_name = serializers.CharField(required=True)
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'meal_category', 'department']
        extra_kwargs = {
            'id': {'read_only': True}
        }
    
    def create(self, validated_data):
        user = validated_data.pop('user', None) # pass  pk value as user
        print("****Validated_data****:", validated_data)
        instance = self.Meta.model(**validated_data)
        if user is  None:
            raise NotFound('User id is required!')
        instance.user = user
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        user = validated_data.pop('user', None) # pass  pk value as user
        # first_name = validated_data.pop('first_name', None)
        # last_name = validated_data.pop('last_name', None)
        instance.meal_category = validated_data.get('meal_category', instance.meal_category)
        instance.department = validated_data.get('department', instance.department)
        # instance.user.first_name = first_name
        # instance.user.last_name = last_name
        instance.save()
        return instance
 
 
class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_image']
    
    def update(self, instance, validated_data):
        print("Profile Image", validated_data.get('profile_image'))
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance
    
#...test data   
# profile2 = UserProfile(department="Accounting")
# user2 = User.objects.get(id=2)
# data = {"user": 2, "meal_category": profile2.meal_category, "department": profile2.department }
# profile_serial = UserProfileSerializer(data=data)
# profile_serial.is_valid()
# profile_serial.save()

# from users.serializers import UserSerializer, UserProfileSerializer
# from users.models import User, UserProfile
