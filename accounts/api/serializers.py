from django.contrib.auth.models import User, Group
from rest_framework import serializers, exceptions, request
from rest_framework.decorators import action
from rest_framework.response import Response


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate(self, data):
        # TODO<HOMEWORK> 增加验证 username 是不是只由给定的字符集合构成
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This username has been occupied.'
        })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This email address has been occupied.'
        })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        """
        查看用户当前的登录状态和具体信息
        """

        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)
