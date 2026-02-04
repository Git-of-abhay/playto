# Extended views file with all new features
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.db.models import Count, Sum, Case, When, IntegerField, Value, Q, Exists, OuterRef
from django.utils import timezone
from datetime import timedelta, date
from django.core.management import call_command
from django.shortcuts import get_object_or_404

from .models import (
    Post, Comment, Like, Profile, Follow, Block, Mute, Report, Notification,
    Community, CommunityMembership, Topic, ChatMessage,
    Course, Module, Lesson, Enrollment, LessonProgress, Assignment, AssignmentSubmission,
    Badge, UserBadge, UserPoints,
    Subscription, Payment
)
from .serializers import (
    PostSerializer, PostListSerializer, CommentSerializer, ProfileCommentSerializer,
    LeaderboardSerializer, UserSerializer, NotificationSerializer, ReportSerializer,
    CommunitySerializer, TopicSerializer, ChatMessageSerializer,
    CourseSerializer, ModuleSerializer, LessonSerializer, EnrollmentSerializer,
    BadgeSerializer, UserBadgeSerializer, UserPointsSerializer,
    SubscriptionSerializer, PaymentSerializer
)


# ============ EXISTING VIEWS (Enhanced) ============

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Post.objects.select_related('author', 'author__profile').prefetch_related('likes')
        
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                has_liked_annotation=Exists(
                    Like.objects.filter(user=user, post=OuterRef('pk'))
                )
            )
            
        if self.action == 'list':
            queryset = queryset.annotate(
                like_count=Count('likes', distinct=True),
                comment_count=Count('comments', distinct=True)
            )
        elif self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'comments__author',
                'comments__likes'
            ).annotate(like_count=Count('likes', distinct=True))
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        # Award points for creating post
        self._award_points(self.request.user, 10)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.prefetched_comments = list(instance.comments.all())
        instance.prefetched_likes = list(instance.likes.all())
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        
        with transaction.atomic():
            existing_like = Like.objects.filter(
                user=request.user, 
                post=post
            ).select_for_update().first()
            
            if existing_like:
                existing_like.delete()
                liked = False
            else:
                try:
                    Like.objects.create(user=request.user, post=post)
                    liked = True
                    # Award points to post author
                    self._award_points(post.author, 5)
                except IntegrityError:
                    return Response({'error': 'Already liked'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'liked': liked,
            'like_count': post.likes.count()
        })

    def _award_points(self, user, points):
        """Helper to award points and check for level ups"""
        user_points, created = UserPoints.objects.get_or_create(user=user)
        user_points.total_points += points
        
        # Simple leveling system
        new_level = (user_points.total_points // 100) + 1
        if new_level > user_points.level:
            user_points.level = new_level
            # Check for badges
            self._check_badges(user)
        
        user_points.save()

    def _check_badges(self, user):
        """Check and award badges based on points"""
        user_points = user.points.total_points
        badges_to_award = Badge.objects.filter(points_required__lte=user_points)
        for badge in badges_to_award:
            UserBadge.objects.get_or_create(user=user, badge=badge)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author').prefetch_related('likes')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        # Award points
        self._award_points(self.request.user, 2)
        # Create notification for post author
        if comment.post.author != self.request.user:
            Notification.objects.create(
                user=comment.post.author,
                type='comment',
                message=f"{self.request.user.username} commented on your post",
                link=f"/post/{comment.post.id}"
            )
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        comment = self.get_object()
        
        with transaction.atomic():
            existing_like = Like.objects.filter(
                user=request.user, 
                comment=comment
            ).select_for_update().first()
            
            if existing_like:
                existing_like.delete()
                liked = False
            else:
                try:
                    Like.objects.create(user=request.user, comment=comment)
                    liked = True
                    self._award_points(comment.author, 1)
                except IntegrityError:
                    return Response({'error': 'Already liked'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'liked': liked,
            'like_count': comment.likes.count()
        })

    def _award_points(self, user, points):
        user_points, created = UserPoints.objects.get_or_create(user=user)
        user_points.total_points += points
        user_points.save()


# ============ SOCIAL FEATURES ============

class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        user_to_follow = get_object_or_404(User, username=username)
        
        if user_to_follow == request.user:
            return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow, created = Follow.objects.get_or_create(
            user_from=request.user,
            user_to=user_to_follow
        )
        
        if created:
            # Create notification
            Notification.objects.create(
                user=user_to_follow,
                type='follow',
                message=f"{request.user.username} started following you",
                link=f"/profile/{request.user.username}"
            )
        
        return Response({'following': True})

    def delete(self, request, username):
        user_to_unfollow = get_object_or_404(User, username=username)
        Follow.objects.filter(user_from=request.user, user_to=user_to_unfollow).delete()
        return Response({'following': False})


class BlockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        user_to_block = get_object_or_404(User, username=username)
        
        if user_to_block == request.user:
            return Response({'error': 'Cannot block yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        Block.objects.get_or_create(blocker=request.user, blocked=user_to_block)
        # Also unfollow
        Follow.objects.filter(user_from=request.user, user_to=user_to_block).delete()
        Follow.objects.filter(user_from=user_to_block, user_to=request.user).delete()
        
        return Response({'blocked': True})

    def delete(self, request, username):
        user_to_unblock = get_object_or_404(User, username=username)
        Block.objects.filter(blocker=request.user, blocked=user_to_unblock).delete()
        return Response({'blocked': False})


class MuteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        user_to_mute = get_object_or_404(User, username=username)
        Mute.objects.get_or_create(muter=request.user, muted=user_to_mute)
        return Response({'muted': True})

    def delete(self, request, username):
        user_to_unmute = get_object_or_404(User, username=username)
        Mute.objects.filter(muter=request.user, muted=user_to_unmute).delete()
        return Response({'muted': False})


class ReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response({'message': 'Report submitted successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return Response({'message': 'All notifications marked as read'})


# ============ COMMUNITY & CHAT ============

class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        community = serializer.save(creator=self.request.user)
        # Auto-join creator as owner
        CommunityMembership.objects.create(
            user=self.request.user,
            community=community,
            role='owner'
        )

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        community = self.get_object()
        
        # Check if already member
        if community.members.filter(id=request.user.id).exists():
            return Response({'error': 'Already a member'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if paid community
        if community.is_paid:
            return Response({'error': 'Paid community - payment required'}, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        CommunityMembership.objects.create(
            user=request.user,
            community=community,
            role='member'
        )
        return Response({'message': 'Joined successfully'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        community = self.get_object()
        CommunityMembership.objects.filter(user=request.user, community=community).delete()
        return Response({'message': 'Left community'})


class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        community_id = self.request.query_params.get('community')
        if community_id:
            return Topic.objects.filter(community_id=community_id)
        return Topic.objects.all()


class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        topic_id = self.request.query_params.get('topic')
        if topic_id:
            return ChatMessage.objects.filter(topic_id=topic_id)
        return ChatMessage.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# ============ COURSE SYSTEM ============

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        course = self.get_object()
        
        # Check if already enrolled
        if course.enrollments.filter(user=request.user).exists():
            return Response({'error': 'Already enrolled'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if paid course
        if course.is_paid:
            return Response({'error': 'Paid course - payment required'}, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        Enrollment.objects.create(user=request.user, course=course)
        return Response({'message': 'Enrolled successfully'})


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        lesson = self.get_object()
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        
        # Award points
        user_points, _ = UserPoints.objects.get_or_create(user=request.user)
        user_points.total_points += 20
        user_points.save()
        
        return Response({'message': 'Lesson marked complete'})


# ============ GAMIFICATION ============

class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [AllowAny]


class UserPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        points, created = UserPoints.objects.get_or_create(user=request.user)
        serializer = UserPointsSerializer(points)
        return Response(serializer.data)


class LeaderboardView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        time_range = request.query_params.get('range', '24h')  # 24h, 7d, all-time
        
        if time_range == '24h':
            cutoff = timezone.now() - timedelta(hours=24)
            recent_likes = Like.objects.filter(created_at__gte=cutoff).select_related(
                'post__author', 'comment__author'
            )
        elif time_range == '7d':
            cutoff = timezone.now() - timedelta(days=7)
            recent_likes = Like.objects.filter(created_at__gte=cutoff).select_related(
                'post__author', 'comment__author'
            )
        else:  # all-time from UserPoints
            top_users = UserPoints.objects.select_related('user').order_by('-total_points')[:10]
            return Response([{
                'id': up.user.id,
                'username': up.user.username,
                'points': up.total_points,
                'level': up.level,
                'streak': up.streak_days
            } for up in top_users])
        
        # Calculate karma from likes
        user_karma = {}
        for like in recent_likes:
            if like.post_id:
                author_id = like.post.author_id
                if author_id not in user_karma:
                    user_karma[author_id] = {'karma': 0, 'username': like.post.author.username}
                user_karma[author_id]['karma'] += 5
            
            if like.comment_id:
                author_id = like.comment.author_id
                if author_id not in user_karma:
                    user_karma[author_id] = {'karma': 0, 'username': like.comment.author.username}
                user_karma[author_id]['karma'] += 1
        
        sorted_users = sorted(
            [{'id': uid, 'username': data['username'], 'karma_24h': data['karma']} 
             for uid, data in user_karma.items()],
            key=lambda x: x['karma_24h'],
            reverse=True
        )[:10]
        
        return Response(sorted_users)


# ============ EXISTING AUTH VIEWS ============

class CsrfExemptSessionAuthentication:
    def authenticate(self, request):
        return None
    
    def enforce_csrf(self, request):
        return


class RegisterView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        name = request.data.get('name', '')
        
        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

        # Password validation
        if len(password) < 8:
            return Response({'error': 'Password must be at least 8 characters'}, status=status.HTTP_400_BAD_REQUEST)
        if not any(c.isdigit() for c in password):
            return Response({'error': 'Password must contain at least one number'}, status=status.HTTP_400_BAD_REQUEST)
        if not any(c.isalpha() for c in password):
            return Response({'error': 'Password must contain at least one letter'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password, first_name=name)
                Profile.objects.create(user=user)
                UserPoints.objects.create(user=user)  # Initialize points
        except Exception as e:
            return Response({'error': 'Registration failed'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserSerializer(user, context={'request': request}).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        from django.contrib.auth import authenticate, login
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Update streak
            self._update_streak(user)
            return Response(UserSerializer(user, context={'request': request}).data)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    def _update_streak(self, user):
        points, _ = UserPoints.objects.get_or_create(user=user)
        today = date.today()
        
        if points.last_activity:
            days_diff = (today - points.last_activity).days
            if days_diff == 1:
                points.streak_days += 1
            elif days_diff > 1:
                points.streak_days = 1
        else:
            points.streak_days = 1
        
        points.save()


class LogoutView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        from django.contrib.auth import logout
        logout(request)
        return Response({'message': 'Logged out'})


class MeView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user, context={'request': request}).data)
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
            
        user = request.user
        
        if 'name' in request.data:
            user.first_name = request.data['name']
            user.save()
            
        if 'avatar' in request.FILES:
            profile, created = Profile.objects.get_or_create(user=user)
            profile.avatar = request.FILES['avatar']
            profile.save()
            
        return Response(UserSerializer(user, context={'request': request}).data)


class UserProfileView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, username):
        try:
            target_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
        post_likes = Like.objects.filter(post__author=target_user).count()
        comment_likes = Like.objects.filter(comment__author=target_user).count()
        total_karma = (post_likes * 5) + (comment_likes * 1)
        
        recent_posts = Post.objects.filter(author=target_user).order_by('-created_at')[:5]
        recent_comments = Comment.objects.filter(author=target_user)\
            .select_related('post', 'post__author', 'post__author__profile')\
            .order_by('-created_at')[:5]
        
        user_data = UserSerializer(target_user, context={'request': request}).data
        
        return Response({
            **user_data,
            'date_joined': target_user.date_joined,
            'stats': {
                'total_karma': total_karma,
                'post_count': Post.objects.filter(author=target_user).count(),
                'comment_count': Comment.objects.filter(author=target_user).count(),
                'likes_received': post_likes + comment_likes
            },
            'recent_posts': PostListSerializer(recent_posts, many=True, context={'request': request}).data,
            'recent_comments': ProfileCommentSerializer(recent_comments, many=True, context={'request': request}).data
        })


class SeedDataView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get(self, request):
        try:
            call_command('seed_data')
            return Response({'message': 'Database seeded successfully!'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
