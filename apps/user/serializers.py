from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from apps.user.models import User, UserType

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        data['email'] = self.user.email
        data['user_type'] = self.user.user_type.name
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        
        return data

class UserSerializer(serializers.ModelSerializer):
    user_type = serializers.StringRelatedField(read_only=True)
    user_type_id = serializers.PrimaryKeyRelatedField(
        queryset=UserType.objects.all(),
        source='user_type',
        write_only=True
    )
    password = serializers.CharField(write_only=True, required=True)
    is_active = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
            'is_active',
            'is_staff',
            'is_superuser',
            'user_type',
            'user_type_id'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user