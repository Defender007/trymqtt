from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.response import Response
from .serializers import UserSerializer, UserProfileSerializer, AvatarSerializer
from .models import User, UserProfile
import jwt, datetime


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
            return Response({"invalid_user_error": "User not found!"}, status=200)

        if not user.check_password(password):
            # raise AuthenticationFailed("Incorrect password!")
            return Response({"password_error": "Incorrect password!"}, status=403)

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


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")

        user = User.objects.filter(id=payload["id"]).first()
        user_serializer = UserSerializer(user)
        try:
            profile = UserProfile.objects.get(user=user.pk)
            profile_serialiser = UserProfileSerializer(profile)
            merged_data = {**profile_serialiser.data, **user_serializer.data}
            return Response(merged_data)
        except Exception as e:
            print("Exception", e)
            return Response(user_serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")
        response.data = {"message": "success"}
        return response


class UserProfileView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.COOKIES.get("jwt")
        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
            print("****payload****:", payload)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")

        user = User.objects.filter(id=payload["id"]).first()
        print("****User****:", user)
        # serialised_user = UserProfileSerializer(user)
        merged_data = {**request.data, "user": user.pk}
        serialiser = UserProfileSerializer(data=merged_data)
        if serialiser.is_valid():
            serialiser.save()
            print("****Data****:", serialiser.data)
            return Response(data=serialiser.data, status=200)
        else:
            return Response(data=serialiser.errors, status=400)

    def patch(self, request, format=None):
        token = request.COOKIES.get("jwt")
        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")

        user_data = {
            "first_name": request.data.pop("first_name", None),
            "last_name": request.data.pop("last_name", None),
        }
        print("****LeanRequestData****:", request.data)

        auth_user = User.objects.get(id=payload["id"])
        profile = UserProfile.objects.get(user=auth_user.pk)

        auth_user.first_name = user_data["first_name"]
        auth_user.last_name = user_data["last_name"]

        profile_data = {**request.data, "user": auth_user.id}
        print("****MergeData****:", profile_data)
        # user_serialiser = UserSerializer(instance=auth_user,data=user_data)
        profile_serialiser = UserProfileSerializer(instance=profile, data=profile_data)
        if profile_serialiser.is_valid():
            auth_user.save()
            profile_serialiser.save()
            # merged_data = {**profile_serialiser.data, **user_serialiser.data}
            print("****UpdateData****:", profile_serialiser.data)
            updated_data = {
                **profile_serialiser.data,
                "first_name": auth_user.first_name,
                "last_name": auth_user.last_name,
            }
            return Response(data=updated_data, status=200)
        else:
            return Response(data=profile_serialiser.errors, status=400)


class UploadProfileImageView(APIView):
    # permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser, FileUploadParser]

    def patch(self, request, format=None):
        # print("****FILE****:", request.FILES['file'])
        token = request.COOKIES.get("jwt")
        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")
        # file = request.FILES['file']
        user = User.objects.get(id=payload["id"])
        profile = UserProfile.objects.get(user=user.pk)
        serialiser = AvatarSerializer(instance=profile, data=request.data)
        # serialiser = AvatarSerializer(instance=profile, data=request.data.file)
        if serialiser.is_valid():
            serialiser.save()
            return Response(data=serialiser.data, status=200)
        else:
            return Response(data=serialiser.errors, status=400)
