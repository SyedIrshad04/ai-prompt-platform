import logging
from django.db.models import Q
from .models import Prompt

logger = logging.getLogger(__name__)


class PromptRepository:
    """Data access layer — only raw DB operations here, no business logic."""

    @staticmethod
    def get_all(search=None, complexity=None, tag=None, sort='-created_at', limit=10, offset=0):
        qs = Prompt.objects.filter(is_active=True)

        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))

        if complexity is not None:
            try:
                qs = qs.filter(complexity=int(complexity))
            except (ValueError, TypeError):
                pass

        if tag:
            qs = qs.filter(tags__name__iexact=tag)

        allowed_sorts = ['created_at', '-created_at', 'title', '-title', 'complexity', '-complexity']
        if sort not in allowed_sorts:
            sort = '-created_at'

        qs = qs.prefetch_related('tags').order_by(sort)
        total = qs.count()
        items = list(qs[offset:offset + limit])
        return items, total

    @staticmethod
    def get_by_id(prompt_id):
        try:
            return Prompt.objects.prefetch_related('tags').get(pk=prompt_id, is_active=True)
        except (Prompt.DoesNotExist, Exception):
            return None

    @staticmethod
    def create(data):
        tags = data.pop('tags', [])
        prompt = Prompt.objects.create(**data)
        if tags:
            from apps.tags.models import Tag
            tag_objects = []
            for tag_name in tags:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name.strip().lower())
                tag_objects.append(tag_obj)
            prompt.tags.set(tag_objects)
        return prompt

    @staticmethod
    def update(prompt, data):
        tags = data.pop('tags', None)
        for field, value in data.items():
            setattr(prompt, field, value)
        prompt.save()
        if tags is not None:
            from apps.tags.models import Tag
            tag_objects = []
            for tag_name in tags:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name.strip().lower())
                tag_objects.append(tag_obj)
            prompt.tags.set(tag_objects)
        return prompt

    @staticmethod
    def soft_delete(prompt):
        prompt.is_active = False
        prompt.save(update_fields=['is_active'])

    @staticmethod
    def get_top_by_ids(prompt_ids):
        """Fetch prompts by list of ids preserving order."""
        prompts = {str(p.id): p for p in Prompt.objects.filter(pk__in=prompt_ids, is_active=True)}
        return [prompts[pid] for pid in prompt_ids if pid in prompts]
