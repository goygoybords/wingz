from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        data['email'] = self.user.email
        data['user_type'] = self.user.user_type.name
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        
        return data
