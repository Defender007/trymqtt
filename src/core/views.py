import jwt, datetime
import json
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from openpyxl import load_workbook
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.exceptions import NotFound
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.exceptions import AuthenticationFailed
from .serializers import TransactionSerializer
from .models import Transaction
from users.models import User, UserProfile
from users.auth_service import user_auth
from .reports import report


# Create your views here.
class TransactionView(APIView):
    def get_queryset(self):
        report_type = self.request.query_params.get("report-type", None)
        sort_option = self.request.query_params.get("sort-option", None)
        if report_type == "":
            report_type = None
        if sort_option == "":
            sort_option = None
        print("0: @@@@@@@@@@@@@@", report_type, sort_option)
        if report_type is not None and sort_option is not None:
            return report(
                report=report_type.lower(),
                sort_by=sort_option.lower(),
            )
        if report_type is not None and sort_option is None:
            return report(report=report_type.lower())

        if report_type is None and sort_option is not None:
            print("3: @@@@@@@@@@@@@@", report_type, sort_option.lower())
            return report(sort_by=sort_option.lower())

        if report_type is None and sort_option is None:
            print("4@@@@@@@@@@@@@@", report_type, sort_option)
            return report()
        return Transaction.objects.filter().order_by(sort_option)

    def get(self, request, pk=None):
        NOT_ADMIN = "User is not an Admin!"
        payload = user_auth(request)
        if payload.get("auth_error", None):
            return Response(payload, status=status.HTTP_403_FORBIDDEN)
        _user = User.objects.filter(id=payload["id"]).first()
        if not _user.is_superuser:
            return Response(
                data={
                    "error": NOT_ADMIN,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        transactions = self.get_queryset()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(data=serializer.data)

    def post(self, request):
        ACCESS_GRANTED = "ACCESS GRANTED"
        ACCESS_DENIED = "ACCESS DENIED"
        ACCESS_POINT = "REMOTE"

        payload = user_auth(request)
        if payload.get("auth_error", None):
            return Response(payload, status=status.HTTP_403_FORBIDDEN)
        _user = User.objects.filter(id=payload["id"]).first()
        if not _user.is_superuser:
            return Response(
                data={
                    "error": "User is not an Admin!",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            today = timezone.now().date()
            authorizer = UserProfile.objects.get(user=payload["id"])
            request_data = {**request.data}
            card_owner = UserProfile.objects.get(
                user__username=request_data["username"], reader_uid=request_data["uid"]
            )

            today_transactions = Transaction.objects.filter(
                reader_uid=request_data["uid"],
                grant_type=ACCESS_GRANTED,
                date__date=today,
            )
            if today_transactions.first() is None:
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
            transaction_count = today_transactions.count()
            meal_category = today_transactions.first().owner.meal_category
            SWIPE_COUNT = transaction_count
            if SWIPE_COUNT < meal_category:
                SWIPE_COUNT += 1
                transaction_data = {
                    "owner": owner_profile_data,
                    "authorizer": request_user_profile_data,
                    "swipe_count": SWIPE_COUNT,
                    "reader_uid": request_data["uid"],
                    "access_point": ACCESS_POINT,
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
                    return Response(
                        data=transaction_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            if SWIPE_COUNT >= meal_category:
                today_transactions = Transaction.objects.filter(
                    reader_uid=request_data["uid"],
                    date__date=today,
                )
                transaction_count = today_transactions.count()
                NEW_SWIPE_COUNT = transaction_count + 1
                transaction_data = {
                    "owner": owner_profile_data,
                    "authorizer": request_user_profile_data,
                    "swipe_count": NEW_SWIPE_COUNT,
                    "reader_uid": request_data["uid"],
                    "access_point": ACCESS_POINT,
                    "raw_payload": json.dumps(request_data),
                    "grant_type": ACCESS_DENIED,
                    "owner_id": card_owner.id,
                    "authorizer_id": authorizer.id,
                }
                return Response(
                    data={"error": "ACCESS DENIED. YOU HAD ENOUGH MEAL TODAY!"},
                    status=status.HTTP_400_BAD_REQUEST,
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
                "access_point": ACCESS_POINT,
                "raw_payload": json.dumps(request_data),
                "grant_type": ACCESS_GRANTED,
                "owner_id": card_owner.id,
                "authorizer_id": authorizer.id,
            }

            transaction_serializer = TransactionSerializer(data=transaction_data)
            if transaction_serializer.is_valid():
                transaction_serializer.save()
                return Response(data=transaction_serializer.data)
            else:
                return Response(
                    data=transaction_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )


@api_view(["GET", "POST"])
def get_owner_transaction_details(request, pk=None):
    payload = user_auth(request)
    if payload.get("auth_error", None):
        return Response(payload, status=status.HTTP_403_FORBIDDEN)
    _user = User.objects.filter(id=payload["id"]).first()
    if not _user.is_superuser or not _user.is_staff:
        return Response(
            data={
                "error": "User is not an Admin!",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )
    if not request.data:
        return Response(data={"NO PAYLOAD!"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == "POST":
        ACCESS_GRANTED = "ACCESS GRANTED"
        request_data = {**request.data}
        # get today's transaction based on grant type and uid
        today = timezone.now().date()
        transactions = Transaction.objects.filter(
            reader_uid=request_data["uid"], date__date=today
        )
        if transactions.count() == 0:
            return Response(data={"NO TRANSACTION MATCH!"}, status=status.HTTP_200_OK)
        approved_transaction_counts = transactions.filter(
            grant_type=ACCESS_GRANTED,
        ).count()
        last_transaction = transactions.last()
        serializer = TransactionSerializer(last_transaction)
        meal_category = serializer.data["owner"]["meal_category"]
        username = serializer.data["owner"]["user"]["username"]
        balance = meal_category - approved_transaction_counts
        avatar = serializer.data["owner"]["profile_image"]
        grant_type = serializer.data["grant_type"]
        response_data = {
            "meal_category": meal_category,
            "used_count": approved_transaction_counts,
            "balance": balance,
            "username": username,
            "avatar": avatar,
            "grant_type": grant_type,
        }
        return Response(data=response_data, status=status.HTTP_200_OK)
    return Response(data={_user.username}, status=status.HTTP_200_OK)

    # {"meal_category": 5, "used": 1, "balance": 4, "username": "", "avatar": ""}
    # {"bulk_create": 1}
