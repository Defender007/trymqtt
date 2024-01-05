from django.core.exceptions import ObjectDoesNotExist
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
            return Response({"invalid_user_error": "User not found!"}, status=403)

        # if user.password == 'getset123':
        #     user.set_password(password)
        #     user.save()
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
            # profile = UserProfile.objects.get(user=user.pk)
            # profile_serialiser = UserProfileSerializer(profile)
            profile = UserProfile.objects.select_related('user').get(user=user.pk)
            profile_serialiser = UserProfileSerializer(profile)
            # merged_data = {**profile_serialiser.data, **user_serializer.data}
            return Response(data=profile_serialiser.data)
        except UserProfile.DoesNotExist as e:
            print("Exception:", e)
            print("User Data:", user_serializer.data)
            return Response(data=user_serializer.data, status=200)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")
        response.data = {"message": "success"}
        return response


class UserProfileView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, pk=None):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")
        
        try:
            if pk is not None:
                profile = UserProfile.objects.select_related('user').get(user=pk)
                print("Profile PK", profile)
                profile_serialiser = UserProfileSerializer(profile)
                return Response(data=profile_serialiser.data)
            else:
                profiles = UserProfile.objects.select_related('user').all()
                profiles_serializer = UserProfileSerializer(profiles, many=True)
                print("User:", profiles[0].user.first_name)
                return Response(data=profiles_serializer.data)
                
        except UserProfile.DoesNotExist as e:
            print("Exception", e)
            return Response(data={"error": e.args[0]}, status=404)


    def post(self, request):
        token = request.COOKIES.get("jwt")
        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
            print("****payload****:", payload)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")

        # auth_user = User.objects.filter(id=payload["id"]).first()
        auth_user = User.objects.get(id=payload["id"])
        print("****User****:", auth_user)
        # serialised_user = UserProfileSerializer(user)
        # merged_data = {**request.data, "user": auth_user.pk}
        user_data = { "first_name": request.data.pop("first_name"),
            "last_name": request.data.pop("last_name"),
            "email": auth_user.email,"username": auth_user.username,
            "password": auth_user.password
            }
        user_serialiser = UserSerializer(instance=auth_user, data=user_data)
        
        profile_data = {**request.data}
        print("#####Profile Data:", profile_data)
        profile_data["user"] = { "id": auth_user.id,
            "email": "...", "username": "....",
            "password": "..."
            }
        profile_data["user_id"] = auth_user.id
        print('%%%%%%:', profile_data["user_id"])
        
        # {"id":auth_user.id}
        
        
        
        # { "id": auth_user.id,}
        
        profile_serialiser = UserProfileSerializer(data=profile_data)
        if profile_serialiser.is_valid() and user_serialiser.is_valid():
            #....this suite is a candidate for DB Transaction 
            user_serialiser.save()
            profile_serialiser.save()
            print("****CreatedData****:", profile_serialiser.data)
            created_data = {
                **profile_serialiser.data,
            }
            return Response(data=created_data, status=200)
        else:
            # errors = [profile_serialiser.errors, user_serialiser.errors]
            return Response(data=profile_serialiser.errors, status=400)

    def patch(self, request, format=None):
        token = request.COOKIES.get("jwt")
        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")

        auth_user = User.objects.get(id=payload["id"])
        user_data = { "first_name": request.data.pop("first_name", auth_user.first_name),
            "last_name": request.data.pop("last_name", auth_user.last_name),
            "email": auth_user.email,"username": auth_user.username,
            "password": auth_user.password
            }
        user_serialiser = UserSerializer(instance=auth_user, data=user_data)

        profile = UserProfile.objects.get(user=auth_user.pk)
        profile_data = {**request.data}
        profile_data["user"] = { "id": auth_user.id,
            "email": "...", "username": "...",
            "password": "..."
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
            return Response(data=updated_data, status=200)
        else:
            print("Profile PATCH ERROR: ", profile_serialiser.errors)
            return Response(data=profile_serialiser.errors, status=500)


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
