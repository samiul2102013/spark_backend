from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    full_name = serializers.CharField(max_length=255)
    household_size = serializers.IntegerField(required=False, allow_null=True)
    medical_needs = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)


class OTPSendSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField()


class BiometricRegisterSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=255)


class BiometricLoginSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=255)


class InviteGovernmentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255)


class AcceptInviteSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        attrs.pop("confirm_password")
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255)


class ResetPasswordSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        attrs.pop("confirm_password")
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "phone_number",
            "email",
            "username",
            "full_name",
            "role",
            "household_size",
            "medical_needs",
            "hub_id",
            "secondary_hub_id",
            "latitude",
            "longitude",
        )
        read_only_fields = (
            "phone_number",
            "username",
            "role",
            "hub_id",
            "secondary_hub_id",
            "latitude",
            "longitude",
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        attrs.pop("confirm_password")
        return attrs


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        attrs.pop("confirm_password")
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class SetRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["resident", "coordinator", "government", "admin"])
