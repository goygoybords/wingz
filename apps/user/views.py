from rest_framework_simplejwt.views import TokenObtainPairView
from apps.user.serializers import CustomTokenObtainPairSerializer

class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer