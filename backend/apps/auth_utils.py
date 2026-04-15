import json
import logging
import jwt
from datetime import datetime, timezone, timedelta
from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# ── Simple in-memory user store (replace with DB-backed users for production) ──
_USERS = {
    'admin': {'password': 'admin123', 'username': 'admin'},
    'demo': {'password': 'demo123', 'username': 'demo'},
}


def create_token(username):
    payload = {
        'sub': username,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def decode_token(token):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_request(request):
    """Extract and verify JWT. Returns username or None."""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    token = auth[7:]
    payload = decode_token(token)
    return payload.get('sub') if payload else None


def require_auth(view_func):
    """Decorator — protects a view with JWT auth."""
    def wrapper(request, *args, **kwargs):
        user = get_user_from_request(request)
        if not user:
            return JsonResponse({'error': 'Authentication required.'}, status=401)
        request.authenticated_user = user
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    username = body.get('username', '').strip()
    password = body.get('password', '')

    user = _USERS.get(username)
    if not user or user['password'] != password:
        return JsonResponse({'error': 'Invalid credentials.'}, status=401)

    token = create_token(username)
    return JsonResponse({'token': token, 'username': username})
