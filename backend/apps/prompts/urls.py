from django.urls import path
from .views import PromptListView, PromptDetailView, AnalyticsView
from apps.auth_utils import login_view

urlpatterns = [
    path('prompts/', PromptListView.as_view(), name='prompt-list'),
    path('prompts/<str:prompt_id>/', PromptDetailView.as_view(), name='prompt-detail'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('auth/login/', login_view, name='login'),
]
