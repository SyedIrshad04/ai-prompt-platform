import json
import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.auth_utils import require_auth, get_user_from_request
from .services import PromptService
from .validators import validate_prompt_create, validate_prompt_update

logger = logging.getLogger(__name__)


def json_body(request):
    """Parse JSON body safely."""
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, ValueError) as e:
        return None, JsonResponse({'error': 'Invalid JSON body.'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PromptListView(View):
    """GET /api/prompts/  — list with pagination, search, filter
       POST /api/prompts/ — create (auth required)
    """

    def get(self, request):
        try:
            data = PromptService.list_prompts(request.GET)
            return JsonResponse(data)
        except Exception as e:
            logger.error(f"PromptListView.get error: {e}", exc_info=True)
            return JsonResponse({'error': 'Internal server error.'}, status=500)

    def post(self, request):
        user = get_user_from_request(request)
        if not user:
            return JsonResponse({'error': 'Authentication required.'}, status=401)

        body, err = json_body(request)
        if err:
            return err

        errors = validate_prompt_create(body)
        if errors:
            return JsonResponse({'errors': errors}, status=400)

        try:
            prompt = PromptService.create_prompt({
                'title': body['title'].strip(),
                'content': body['content'].strip(),
                'complexity': int(body['complexity']),
                'tags': body.get('tags', []),
            }, user=user)
            return JsonResponse(prompt, status=201)
        except Exception as e:
            logger.error(f"PromptListView.post error: {e}", exc_info=True)
            return JsonResponse({'error': 'Internal server error.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PromptDetailView(View):
    """GET /api/prompts/<id>/   — increments Redis view counter
       PUT /api/prompts/<id>/   — update (auth required)
       DELETE /api/prompts/<id>/ — soft delete (auth required)
    """

    def get(self, request, prompt_id):
        try:
            prompt = PromptService.get_prompt(prompt_id)
            if not prompt:
                return JsonResponse({'error': 'Prompt not found.'}, status=404)
            return JsonResponse(prompt)
        except Exception as e:
            logger.error(f"PromptDetailView.get error: {e}", exc_info=True)
            return JsonResponse({'error': 'Internal server error.'}, status=500)

    def put(self, request, prompt_id):
        user = get_user_from_request(request)
        if not user:
            return JsonResponse({'error': 'Authentication required.'}, status=401)

        body, err = json_body(request)
        if err:
            return err

        errors = validate_prompt_update(body)
        if errors:
            return JsonResponse({'errors': errors}, status=400)

        try:
            prompt = PromptService.update_prompt(prompt_id, body)
            if not prompt:
                return JsonResponse({'error': 'Prompt not found.'}, status=404)
            return JsonResponse(prompt)
        except Exception as e:
            logger.error(f"PromptDetailView.put error: {e}", exc_info=True)
            return JsonResponse({'error': 'Internal server error.'}, status=500)

    def delete(self, request, prompt_id):
        user = get_user_from_request(request)
        if not user:
            return JsonResponse({'error': 'Authentication required.'}, status=401)

        try:
            deleted = PromptService.delete_prompt(prompt_id)
            if not deleted:
                return JsonResponse({'error': 'Prompt not found.'}, status=404)
            return JsonResponse({'message': 'Prompt deleted.'}, status=200)
        except Exception as e:
            logger.error(f"PromptDetailView.delete error: {e}", exc_info=True)
            return JsonResponse({'error': 'Internal server error.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AnalyticsView(View):
    """GET /api/analytics/ — top viewed prompts + complexity distribution"""

    def get(self, request):
        try:
            data = PromptService.get_analytics()
            return JsonResponse(data)
        except Exception as e:
            logger.error(f"AnalyticsView.get error: {e}", exc_info=True)
            return JsonResponse({'error': 'Internal server error.'}, status=500)
