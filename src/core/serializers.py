from rest_framework.exceptions import NotFound
from django.core.exceptions import BadRequest
from rest_framework import serializers
from .models import Transaction
from users.serializers import UserProfileSerializer
from users.models import UserProfile


class TransactionSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer()
    authorizer = UserProfileSerializer()
    owner_id = serializers.UUIDField()
    authorizer_id = serializers.UUIDField()

    class Meta:
        model = Transaction
        fields = [
            "owner",
            "authorizer",
            "swipe_count",
            "reader_uid",
            "access_point",
            "raw_payload",
            "grant_type",
            "owner_id",
            "authorizer_id",
            "date"
        ]

    def create(self, validated_data):
        print("**** 1st Validated_data****:", validated_data)
        owner = validated_data.pop("owner", None)
        authorizer = validated_data.pop("authorizer", None)
        if owner is None or authorizer is None:
            raise NotFound("No owner found!")
        transaction = self.Meta.model(**validated_data)
        transaction.owner = UserProfile.objects.get(id=validated_data["owner_id"])
        transaction.authorizer = UserProfile.objects.get(
            id=validated_data["authorizer_id"]
        )
        transaction.save()
        return transaction
