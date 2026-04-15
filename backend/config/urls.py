from django.http import JsonResponse
from django.urls import path, include


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('health/', health, name='health'),
    path('api/', include('apps.prompts.urls')),
    path('api/', include('apps.tags.urls')),
]
