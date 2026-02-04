from django.urls import path, include
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet, CommentViewSet, LeaderboardView, 
    RegisterView, LoginView, LogoutView, MeView, UserProfileView, SeedDataView,
    FollowView, BlockView, MuteView, ReportView, NotificationViewSet,
    CommunityViewSet, TopicViewSet, ChatMessageViewSet,
    CourseViewSet, EnrollmentViewSet, LessonViewSet,
    BadgeViewSet, UserPointsView
)

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'communities', CommunityViewSet, basename='community')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'chat', ChatMessageViewSet, basename='chat')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'badges', BadgeViewSet, basename='badge')

@ensure_csrf_cookie
def get_csrf_token(request):
    """Endpoint to ensure CSRF cookie is set"""
    return JsonResponse({'csrfToken': 'set'})

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Auth
    path('csrf/', get_csrf_token, name='csrf'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    
    # Social Features
    path('users/<str:username>/follow/', FollowView.as_view(), name='follow'),
    path('users/<str:username>/block/', BlockView.as_view(), name='block'),
    path('users/<str:username>/mute/', MuteView.as_view(), name='mute'),
    path('report/', ReportView.as_view(), name='report'),
    
    # Profiles & Leaderboard
    path('profile/<str:username>/', UserProfileView.as_view(), name='profile'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('points/', UserPointsView.as_view(), name='points'),
    
    # Utils
    path('seed_force_trigger/', SeedDataView.as_view(), name='seed_force'),
]
