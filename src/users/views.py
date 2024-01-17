import jwt, datetime
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from .serializers import UserSerializer, UserProfileSerializer, AvatarSerializer
from .models import User, UserProfile
from .auth_service import user_auth


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = User.objects.filter(email=email).first()
        if user is None:
            # raise AuthenticationFailed("User not found!")
            return Response(
                {"invalid_user_error": "User not found!"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.check_password(password):
            # raise AuthenticationFailed("Incorrect password!")
            return Response(
                {"password_error": "Incorrect password!"},
                status=status.HTTP_403_FORBIDDEN,
            )

        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow(),
        }
        token = jwt.encode(payload, "secret", algorithm="HS256")

        response = Response()

        response.set_cookie(key="jwt", value=token, httponly=True)
        response.data = {"jwt": token}

        return response


class AuthUserView(APIView):
    def get(self, request, pk=None):
        payload = user_auth(request)
        if payload.get("auth_error", None):
            return Response(payload, status=status.HTTP_403_FORBIDDEN)
        user = User.objects.filter(id=payload["id"]).first()
        try:
            user_serializer = UserSerializer(user)
            profile = UserProfile.objects.select_related("user").get(user=user.pk)
            profile_serialiser = UserProfileSerializer(profile)
            return Response(data=profile_serialiser.data)
        except UserProfile.DoesNotExist:
            return Response(data=user_serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")
        response.data = {"message": "success"}
        return response


class UserProfileView(APIView):
    def get(self, request, pk=None):
        payload = user_auth(request)
        if payload.get("auth_error", None):
            return Response(payload, status=status.HTTP_403_FORBIDDEN)
        try:
            if pk is not None:
                profile = UserProfile.objects.select_related("user").get(user=pk)
                profile_serialiser = UserProfileSerializer(profile)
                return Response(data=profile_serialiser.data)
            else:
                profiles = UserProfile.objects.select_related("user").all()
                profiles_serializer = UserProfileSerializer(profiles, many=True)
                return Response(data=profiles_serializer.data)
        except UserProfile.DoesNotExist as e:
            return Response(data={"no_profile_error": e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        payload = user_auth(request)
        if payload.get("auth_error", None):
            return Response(payload, status=status.HTTP_403_FORBIDDEN)
        auth_user = User.objects.get(id=payload["id"])
        user_data = {
            "first_name": request.data.pop("first_name"),
            "last_name": request.data.pop("last_name"),
            "email": auth_user.email,
            "username": auth_user.username,
            "password": auth_user.password,
        }
        ###...Update related User before creating Profile
        user_serialiser = UserSerializer(instance=auth_user, data=user_data)
        profile_data = {**request.data}
        print("#####Profile Data:", profile_data)
        profile_data["user"] = {
            "id": auth_user.id,
            "email": "...",
            "username": "...",
            "password": "...",
        }
        profile_data["user_id"] = auth_user.id
        print("%%%%%%:", profile_data["user_id"])

        profile_serialiser = UserProfileSerializer(data=profile_data)
        if profile_serialiser.is_valid() and user_serialiser.is_valid():
            # ....this suite is a candidate for DB Transaction
            user_serialiser.save()
            profile_serialiser.save()
            print("****CreatedData****:", profile_serialiser.data)
            created_data = {
                **profile_serialiser.data,
            }
            return Response(data=created_data, status=status.HTTP_200_OK)
        else:
            errors = [profile_serialiser.errors, user_serialiser.errors]
            return Response(data=errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, format=None):
        payload = user_auth(request)
        if payload.get("auth_error", None):
            return Response(payload, status=status.HTTP_403_FORBIDDEN)
        auth_user = User.objects.get(id=payload["id"])
        user_data = {
            "first_name": request.data.pop("first_name", auth_user.first_name),
            "last_name": request.data.pop("last_name", auth_user.last_name),
            "email": auth_user.email,
            "username": auth_user.username,
            "password": auth_user.password,
        }
        user_serialiser = UserSerializer(instance=auth_user, data=user_data)

        profile = UserProfile.objects.get(user=auth_user.pk)
        profile_data = {**request.data}
        profile_data["user"] = {
            "id": auth_user.id,
            "email": "...",
            "username": "...",
            "password": "...",
        }
        profile_data["user_id"] = auth_user.id
        print("****MergeData****:", profile_data)
        profile_serialiser = UserProfileSerializer(instance=profile, data=profile_data)
        if profile_serialiser.is_valid() and user_serialiser.is_valid():
            user_serialiser.save()
            profile_serialiser.save()
            print("****UpdateData****:", profile_serialiser.data)
            updated_data = {
                **profile_serialiser.data,
            }
            return Response(data=updated_data, status=status.HTTP_200_OK)
        else:
            print("Profile PATCH ERROR: ", profile_serialiser.errors)
            return Response(data=profile_serialiser.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadProfileImageView(APIView):
    parser_classes = [FormParser, MultiPartParser, FileUploadParser]

    def patch(self, request, format=None):
        payload = user_auth(request)
        if payload.get("auth_error", None):
            return Response(payload, status=status.HTTP_403_FORBIDDEN)
        user = User.objects.get(id=payload["id"])
        profile = UserProfile.objects.get(user=user.pk)
        serialiser = AvatarSerializer(instance=profile, data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(data=serialiser.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
