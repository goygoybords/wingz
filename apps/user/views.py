from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from apps.user.models import User
from apps.user.serializers import CustomTokenObtainPairSerializer, UserSerializer
from apps.user.permissions import IsAdminRole

class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"message": "User updated successfully."}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({"message": "User partially updated successfully."}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
