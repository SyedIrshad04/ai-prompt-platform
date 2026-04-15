import logging
from apps.redis_client import get_redis_client, redis_available
from .repositories import PromptRepository

logger = logging.getLogger(__name__)

VIEW_KEY = "prompt:{}:views"
LEADERBOARD_KEY = "prompts:leaderboard"


class PromptService:
    """Business logic layer. Orchestrates repositories and cache."""

    @staticmethod
    def list_prompts(params):
        search = params.get('search', '').strip() or None
        complexity = params.get('complexity')
        tag = params.get('tag', '').strip() or None
        sort = params.get('sort', '-created_at')

        try:
            page = max(1, int(params.get('page', 1)))
            page_size = min(50, max(1, int(params.get('page_size', 10))))
        except (ValueError, TypeError):
            page, page_size = 1, 10

        offset = (page - 1) * page_size
        prompts, total = PromptRepository.get_all(
            search=search, complexity=complexity, tag=tag,
            sort=sort, limit=page_size, offset=offset
        )

        results = [PromptService._serialize(p, include_view_count=True) for p in prompts]
        return {
            'results': results,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
        }

    @staticmethod
    def get_prompt(prompt_id):
        prompt = PromptRepository.get_by_id(prompt_id)
        if not prompt:
            return None

        # Increment view in Redis — Redis is source of truth
        view_count = PromptService._increment_view(str(prompt.id))
        data = PromptService._serialize(prompt)
        data['view_count'] = view_count
        return data

    @staticmethod
    def create_prompt(data, user=None):
        if user:
            data['created_by'] = user
        prompt = PromptRepository.create(data)
        logger.info(f"Prompt created: {prompt.id} — '{prompt.title}'")
        return PromptService._serialize(prompt)

    @staticmethod
    def update_prompt(prompt_id, data):
        prompt = PromptRepository.get_by_id(prompt_id)
        if not prompt:
            return None
        prompt = PromptRepository.update(prompt, data)
        return PromptService._serialize(prompt)

    @staticmethod
    def delete_prompt(prompt_id):
        prompt = PromptRepository.get_by_id(prompt_id)
        if not prompt:
            return False
        PromptRepository.soft_delete(prompt)
        # Clean up Redis keys
        client = get_redis_client()
        if client:
            try:
                client.delete(VIEW_KEY.format(prompt_id))
                client.zrem(LEADERBOARD_KEY, str(prompt_id))
            except Exception as e:
                logger.warning(f"Redis cleanup failed for {prompt_id}: {e}")
        return True

    @staticmethod
    def get_analytics():
        """Return top prompts by views and complexity distribution."""
        client = get_redis_client()
        top_prompts = []

        if client:
            try:
                # Top 10 from sorted set (leaderboard)
                top_ids_scores = client.zrevrange(LEADERBOARD_KEY, 0, 9, withscores=True)
                if top_ids_scores:
                    ids = [item[0] for item in top_ids_scores]
                    prompts = PromptRepository.get_top_by_ids(ids)
                    score_map = {item[0]: int(item[1]) for item in top_ids_scores}
                    for p in prompts:
                        d = PromptService._serialize(p)
                        d['view_count'] = score_map.get(str(p.id), 0)
                        top_prompts.append(d)
            except Exception as e:
                logger.warning(f"Analytics leaderboard fetch failed: {e}")

        # Complexity distribution from DB
        from django.db.models import Count
        from apps.prompts.models import Prompt
        complexity_dist = list(
            Prompt.objects.filter(is_active=True)
            .values('complexity')
            .annotate(count=Count('id'))
            .order_by('complexity')
        )

        return {
            'top_viewed': top_prompts,
            'complexity_distribution': complexity_dist,
            'redis_status': 'connected' if redis_available() else 'unavailable',
        }

    # ── Internal helpers ──────────────────────────────────────────────────

    @staticmethod
    def _increment_view(prompt_id):
        client = get_redis_client()
        if client:
            try:
                key = VIEW_KEY.format(prompt_id)
                count = client.incr(key)
                # Keep leaderboard in sync
                client.zadd(LEADERBOARD_KEY, {prompt_id: count}, gt=True)
                # Ensure member exists even if zadd with GT didn't add it
                client.zadd(LEADERBOARD_KEY, {prompt_id: count})
                return count
            except Exception as e:
                logger.warning(f"Redis view increment failed for {prompt_id}: {e}")

        # Fallback: return 0 if Redis is down
        return 0

    @staticmethod
    def get_view_count(prompt_id):
        client = get_redis_client()
        if client:
            try:
                val = client.get(VIEW_KEY.format(str(prompt_id)))
                return int(val) if val else 0
            except Exception:
                pass
        return 0

    @staticmethod
    def _serialize(prompt, include_view_count=False):
        data = {
            'id': str(prompt.id),
            'title': prompt.title,
            'content': prompt.content,
            'complexity': prompt.complexity,
            'is_active': prompt.is_active,
            'created_at': prompt.created_at.isoformat(),
            'updated_at': prompt.updated_at.isoformat(),
            'created_by': prompt.created_by,
            'tags': [t.name for t in prompt.tags.all()],
        }
        if include_view_count:
            data['view_count'] = PromptService.get_view_count(str(prompt.id))
        return data
