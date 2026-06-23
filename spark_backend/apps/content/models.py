from django.db import models


class StaticContent(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "static_content"
        verbose_name = "Static Content"
        verbose_name_plural = "Static Contents"

    def __str__(self):
        return self.title
