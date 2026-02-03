from django.urls import path, include
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, LeaderboardView, RegisterView, LoginView, LogoutView, MeView, UserProfileView, SeedDataView

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

@ensure_csrf_cookie
def get_csrf_token(request):
    """Endpoint to ensure CSRF cookie is set"""
    return JsonResponse({'csrfToken': 'set'})

urlpatterns = [
    path('', include(router.urls)),
    path('csrf/', get_csrf_token, name='csrf'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='profile'),
    path('seed_force_trigger/', SeedDataView.as_view(), name='seed_force'),
]
