from rest_framework_simplejwt.views import TokenObtainPairView
from apps.user.serializers import CustomTokenObtainPairSerializer
from rest_framework import viewsets
from apps.user.models import User
from apps.user.serializers import UserSerializer
from apps.user.permissions import IsAdminRole

class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]