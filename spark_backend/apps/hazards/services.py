from django.db import transaction

from .models import Comment, Hazard


class HazardService:
    def list_hazards(self, status=None, category=None, hub_id=None, period=None, hours=None):
        from datetime import timedelta
        from django.utils import timezone

        qs = Hazard.objects.select_related("reporter", "hub").all()
        if status:
            qs = qs.filter(status=status)
        if category:
            qs = qs.filter(category=category)
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        if period:
            qs = qs.filter(period=period)
        if hours:
            cutoff = timezone.now() - timedelta(hours=int(hours))
            qs = qs.filter(created_at__gte=cutoff)
        return qs

    def get_hazard(self, hazard_id):
        return Hazard.objects.select_related("reporter", "hub").get(id=hazard_id)

    @transaction.atomic
    def create_hazard(self, data, reporter):
        if reporter:
            data["reporter"] = reporter
        hazard = Hazard.objects.create(**data)
        if hazard.description:
            from apps.ai.services import AIScoringService
            hazard.risk_score = AIScoringService.assign_risk_score(
                hazard.description, hazard.category
            )
            if hazard.risk_score is not None:
                hazard.save(update_fields=["risk_score"])
        return hazard

    @transaction.atomic
    def update_hazard(self, hazard_id, data):
        hazard = Hazard.objects.get(id=hazard_id)
        for key, value in data.items():
            setattr(hazard, key, value)
        hazard.save()
        return hazard

    @transaction.atomic
    def delete_hazard(self, hazard_id):
        hazard = Hazard.objects.get(id=hazard_id)
        hazard.delete()

    @transaction.atomic
    def mark_cleared(self, hazard_id, user):
        hazard = Hazard.objects.get(id=hazard_id)
        hazard.status = "cleared"
        hazard.save(update_fields=["status"])
        return hazard

    def list_comments(self, hazard_id):
        return Comment.objects.filter(hazard_id=hazard_id).select_related("author")

    @transaction.atomic
    def add_comment(self, hazard_id, body, author=None, photo=None):
        return Comment.objects.create(hazard_id=hazard_id, author=author, body=body, photo=photo)
