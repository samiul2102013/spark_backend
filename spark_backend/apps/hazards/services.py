from django.db import transaction

from .models import Comment, Hazard


class HazardService:
    @staticmethod
    def list_hazards(status=None, category=None, hub_id=None):
        qs = Hazard.objects.select_related("reporter", "hub").all()
        if status:
            qs = qs.filter(status=status)
        if category:
            qs = qs.filter(category=category)
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        return qs

    @staticmethod
    def get_hazard(hazard_id):
        return Hazard.objects.select_related("reporter", "hub").get(id=hazard_id)

    @staticmethod
    @transaction.atomic
    def create_hazard(data, reporter=None):
        if reporter:
            data["reporter"] = reporter
        return Hazard.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update_hazard(hazard_id, data):
        hazard = Hazard.objects.get(id=hazard_id)
        for key, value in data.items():
            setattr(hazard, key, value)
        hazard.save()
        return hazard

    @staticmethod
    @transaction.atomic
    def delete_hazard(hazard_id):
        hazard = Hazard.objects.get(id=hazard_id)
        hazard.delete()

    @staticmethod
    def list_comments(hazard_id):
        return Comment.objects.filter(hazard_id=hazard_id).select_related("author")

    @staticmethod
    @transaction.atomic
    def add_comment(hazard_id, body, author=None, photo=None):
        return Comment.objects.create(hazard_id=hazard_id, author=author, body=body, photo=photo)
