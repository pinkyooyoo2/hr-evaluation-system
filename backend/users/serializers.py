from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'role', 'team', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', '')
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            generated_password = f"{validated_data.get('username', 'user')}123!"
            user.set_password(generated_password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
