import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Tag

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TagListView(View):
    def get(self, request):
        try:
            tags = list(Tag.objects.values('id', 'name').order_by('name'))
            return JsonResponse({'results': tags, 'total': len(tags)})
        except Exception as e:
            logger.error(f"TagListView error: {e}", exc_info=True)
            return JsonResponse({'error': 'Internal server error.'}, status=500)
