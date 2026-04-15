import uuid
from django.db import models


class Prompt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, db_index=True)
    content = models.TextField()
    complexity = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'prompts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['complexity', 'is_active']),
            models.Index(fields=['created_at', 'is_active']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title
