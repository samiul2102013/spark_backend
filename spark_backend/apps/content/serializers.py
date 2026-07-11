from rest_framework import serializers

from .models import StaticContent


class StaticContentSerializer(serializers.ModelSerializer):
    last_edited_by = serializers.SerializerMethodField()

    class Meta:
        model = StaticContent
        fields = ("slug", "title", "content", "updated_at", "last_edited_by")

    def get_last_edited_by(self, obj):
        return obj.updated_by.full_name if obj.updated_by else None
