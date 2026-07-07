from django.db import transaction

from apps.notifications.services import NotificationOrchestrator

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
        if hazard.hub:
            NotificationOrchestrator.notify_hub_users(
                hub=hazard.hub,
                type="alert",
                title=f"{hazard.get_category_display()} Alert",
                body=f"{hazard.get_category_display()} reported near you. Severity: {hazard.severity}. {hazard.description[:100]}",
                link=f"/hazards/{hazard.id}",
                data={"hazard_id": str(hazard.id), "category": hazard.category},
            )
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
        if hazard.reporter:
            NotificationOrchestrator.notify(
                user=hazard.reporter,
                type="alert",
                title="Hazard Resolved",
                body=f"{hazard.get_category_display()} at {hazard.description[:100]} has been cleared.",
                link=f"/hazards/{hazard.id}",
                data={"hazard_id": str(hazard.id), "status": "cleared"},
            )
        return hazard

    def list_comments(self, hazard_id):
        return Comment.objects.filter(hazard_id=hazard_id).select_related("author")

    @transaction.atomic
    def add_comment(self, hazard_id, body, author=None, photo=None):
        comment = Comment.objects.create(hazard_id=hazard_id, author=author, body=body, photo=photo)
        hazard = comment.hazard
        if hazard.reporter and (not author or hazard.reporter != author):
            NotificationOrchestrator.notify(
                user=hazard.reporter,
                type="alert",
                title="New Update",
                body=f"{author.full_name if author else 'Someone'} commented on your {hazard.get_category_display()} report.",
                link=f"/hazards/{hazard.id}",
                data={"hazard_id": str(hazard.id), "comment_id": str(comment.id)},
            )
        return comment
