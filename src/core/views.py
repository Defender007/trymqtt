import jwt, datetime
import json
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import TransactionSerializer
from .models import Transaction
from users.models import User, UserProfile


# Create your views here.
class TransactionView(APIView):
    def get(self, request, pk=None):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")
        _user = User.objects.filter(id=payload["id"]).first()
        if not _user.is_superuser:
            return Response(
                data={
                    "error": "User is not an Admin!",
                },
                status=400,
            )
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(data=serializer.data)

    def post(self, request):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")
        _user = User.objects.filter(id=payload["id"]).first()
        if not _user.is_superuser:
            return Response(
                data={
                    "error": "User is not an Admin!",
                },
                status=400,
            )
        try:
            today = timezone.now().date()
            authorizer = UserProfile.objects.get(user=payload["id"])
            request_data = {**request.data}
            card_owner = UserProfile.objects.get(
                user__username=request_data["username"], reader_uid=request_data["uid"]
            )

            today_transaction = Transaction.objects.filter(
                reader_uid=request_data["uid"],
                grant_type="ACCESS GRANTED",
                date__date=today,
            )
            if today_transaction.first() is None:
                raise ObjectDoesNotExist("No transaction exists yet for this owner")

            owner_profile_data = {
                "id": card_owner.id,
                "user_id": 0,
                "user": {"username": "...", "email": "...", "password": "..."},
                "meal_category": 1,
                # "profile_image": "...",
                "department": "...",
            }
            request_user_profile_data = {
                "id": authorizer.id,
                "user_id": 0,
                "user": {"username": "...", "email": "...", "password": "..."},
                "meal_category": 1,
                # "profile_image": "...",
                "department": "...",
            }
            transaction_count = today_transaction.count()
            meal_category = today_transaction.first().owner.meal_category
            SWIPE_COUNT = transaction_count
            if SWIPE_COUNT < meal_category:
                SWIPE_COUNT += 1
                transaction_data = {
                    "owner": owner_profile_data,
                    "authorizer": request_user_profile_data,
                    "swipe_count": SWIPE_COUNT,
                    "reader_uid": request_data["uid"],
                    "access_point": "REMOTE",
                    "raw_payload": json.dumps(request_data),
                    "grant_type": "ACCESS GRANTED",
                    "owner_id": card_owner.id,
                    "authorizer_id": authorizer.id,
                }
                transaction_serializer = TransactionSerializer(data=transaction_data)
                if transaction_serializer.is_valid():
                    transaction_serializer.save()
                    return Response(data=transaction_serializer.data)
                else:
                    return Response(data=transaction_serializer.errors, status=400)
            else:
                return Response(
                    data={"error": "ACCESS DENIED. YOU HAD ENOUGH MEAL TODAY!"},
                    status=400,
                )
        except User.DoesNotExist:
            raise NotFound("ACCESS DENIED. User not found!")
        except UserProfile.DoesNotExist:
            raise NotFound("ACCESS DENIED. User must setup a profile!")
        except ObjectDoesNotExist:
            authorizer = UserProfile.objects.get(user=payload["id"])
            request_data = {**request.data}
            card_owner = UserProfile.objects.get(
                user__username=request_data["username"]
            )
            owner_profile_data = {
                "id": card_owner.id,
                "user_id": 0,
                "user": {"username": "...", "email": "...", "password": "..."},
                "meal_category": 1,
                # "profile_image": "...",
                "department": "...",
            }
            request_user_profile_data = {
                "id": authorizer.id,
                "user_id": 0,
                "user": {"username": "...", "email": "...", "password": "..."},
                "meal_category": 1,
                # "profile_image": "...",
                "department": "...",
            }
            SWIPE_COUNT = 1
            transaction_data = {
                "owner": owner_profile_data,
                "authorizer": request_user_profile_data,
                "swipe_count": SWIPE_COUNT,
                "reader_uid": request_data["uid"],
                "access_point": "REMOTE",
                "raw_payload": json.dumps(request_data),
                "grant_type": "ACCESS GRANTED",
                "owner_id": card_owner.id,
                "authorizer_id": authorizer.id,
            }

            transaction_serializer = TransactionSerializer(data=transaction_data)
            if transaction_serializer.is_valid():
                transaction_serializer.save()
                return Response(data=transaction_serializer.data)
            else:
                return Response(data=transaction_serializer.errors, status=400)
