<<<<<<< HEAD
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import IsOrganizer
from .serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    UserPublicSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .services import AccountService


class RegisterView(generics.CreateAPIView):
=======
"""
Views for user accounts.
"""

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, UserPublicSerializer
)
from .services import AccountService
from .permissions import IsOrganizer


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""

>>>>>>> main
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
<<<<<<< HEAD
                "message": "User registered successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
=======
                'message': 'User registered successfully.',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
>>>>>>> main
        )


class LoginView(APIView):
<<<<<<< HEAD
=======
    """User login endpoint."""

>>>>>>> main
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
<<<<<<< HEAD
        user = serializer.validated_data["user"]
        AccountService.login_user(request, user)
        return Response(
            {"message": "Login successful.", "user": UserSerializer(user).data}
        )


class LogoutView(APIView):
=======
        user = serializer.validated_data['user']
        AccountService.login_user(request, user)
        return Response({
            'message': 'Login successful.',
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """User logout endpoint."""

>>>>>>> main
    permission_classes = [IsAuthenticated]

    def post(self, request):
        AccountService.logout_user(request)
<<<<<<< HEAD
        return Response({"message": "Logout successful."})


class ProfileView(generics.RetrieveUpdateAPIView):
=======
        return Response({'message': 'Logout successful.'})


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint."""

>>>>>>> main
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
<<<<<<< HEAD
        if self.request.method in ("PUT", "PATCH"):
=======
        if self.request.method in ('PUT', 'PATCH'):
>>>>>>> main
            return UserUpdateSerializer
        return UserSerializer


class PasswordChangeView(APIView):
<<<<<<< HEAD
=======
    """Password change endpoint."""

>>>>>>> main
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
<<<<<<< HEAD
            data=request.data, context={"request": request}
=======
            data=request.data,
            context={'request': request}
>>>>>>> main
        )
        serializer.is_valid(raise_exception=True)
        AccountService.change_password(
            request.user,
<<<<<<< HEAD
            serializer.validated_data["old_password"],
            serializer.validated_data["new_password"],
        )
        return Response({"message": "Password changed successfully."})


class DeleteAccountView(APIView):
=======
            serializer.validated_data['old_password'],
            serializer.validated_data['new_password']
        )
        return Response({'message': 'Password changed successfully.'})


class DeleteAccountView(APIView):
    """Account deletion endpoint."""

>>>>>>> main
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        AccountService.delete_account(request.user, request.user)
        return Response(
<<<<<<< HEAD
            {"message": "Account deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
=======
            {'message': 'Account deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
>>>>>>> main
        )


class PlayerListView(generics.ListAPIView):
<<<<<<< HEAD
=======
    """List all players."""

>>>>>>> main
    serializer_class = UserPublicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AccountService.get_all_players()


class RefereeListView(generics.ListAPIView):
<<<<<<< HEAD
=======
    """List all referees."""

>>>>>>> main
    serializer_class = UserPublicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AccountService.get_all_referees()


class UserListView(generics.ListAPIView):
<<<<<<< HEAD
=======
    """List all users (organizer only)."""

>>>>>>> main
    serializer_class = UserPublicSerializer
    permission_classes = [IsOrganizer]
    queryset = User.objects.filter(is_active=True)
