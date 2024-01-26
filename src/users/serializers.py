from rest_framework.exceptions import NotFound
from django.core.exceptions import BadRequest
from rest_framework import serializers
from .models import User, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email", "password", "is_superuser"]
        extra_kwargs = {
            "password": {"write_only": True},
            # 'id': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is None:
            raise BadRequest("Password is required!")
        instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password is not None:
            instance.set_password(password)
        instance.first_name = validated_data.pop("first_name", instance.first_name)
        instance.last_name = validated_data.pop("last_name", instance.last_name)
        instance.save(
            update_fields=[
                "first_name",
                "last_name",
            ]
        )
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    user_id = serializers.IntegerField()
    reader_uid = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user_id",
            "user",
            "reader_uid",
            "meal_category",
            "profile_image",
            "department",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "reader_uid": {"read_only": True},
        }

    def create(self, validated_data):
        print("**** 1st Validated_data****:", validated_data)
        user = validated_data.pop("user", None)  # pass  pk value as user
        user_id = validated_data.pop("user_id")  #
        print("**** 2nd Validated_data****:", validated_data)
        profile = self.Meta.model(**validated_data)
        if user_id is None or user is None:
            raise NotFound("User id is required!")
        auth_user = User.objects.get(id=user_id)
        profile.user = auth_user
        profile.save()
        return profile

    def update(self, instance, validated_data):
        # user = validated_data.pop('user', None) # pass  pk value as user
        instance.meal_category = validated_data.get(
            "meal_category", instance.meal_category
        )
        # instance.reader_uid = validated_data.get(
        #     "reader_uid", instance.reader_uid
        # )
        instance.department = validated_data.get("department", instance.department)
        instance.save()
        return instance


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["profile_image"]

    def update(self, instance, validated_data):
        print("Profile Image", validated_data.get("profile_image"))
        instance.profile_image = validated_data.get(
            "profile_image", instance.profile_image
        )
        instance.save()
        return instance


# ...test data
# profile2 = UserProfile(department="Accounting")
# user2 = User.objects.get(id=2)
# data = {"user": 2, "meal_category": profile2.meal_category, "department": profile2.department }
# profile_serial = UserProfileSerializer(data=data)
# profile_serial.is_valid()
# profile_serial.save()

# from users.serializers import UserSerializer, UserProfileSerializer
# from users.models import User, UserProfile
