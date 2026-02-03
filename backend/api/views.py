from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.db.models import Count, Sum, Case, When, IntegerField, Value, Q
from django.utils import timezone
from datetime import timedelta

from .models import Post, Comment, Like, Profile
from .serializers import (
    PostSerializer, PostListSerializer, CommentSerializer, 
    LeaderboardSerializer, UserSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        # Base queryset
        queryset = Post.objects.select_related('author', 'author__profile').prefetch_related('likes')
        
        # Annotate user_has_liked if user is authenticated
        user = self.request.user
        if user.is_authenticated:
            # This is the most robust way to check likes vs Python loops
            from django.db.models import Exists, OuterRef
            queryset = queryset.annotate(
                has_liked_annotation=Exists(
                    Like.objects.filter(user=user, post=OuterRef('pk'))
                )
            )
            
        # For list view, just count comments
        if self.action == 'list':
            queryset = queryset.annotate(
                like_count=Count('likes', distinct=True),
                comment_count=Count('comments', distinct=True)
            )
        # For detail view, prefetch all comments for tree building
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
        serializer.save(author=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Attach prefetched comments for the serializer
        instance.prefetched_comments = list(instance.comments.all())
        instance.prefetched_likes = list(instance.likes.all())
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Toggle like on a post with race condition prevention"""
        post = self.get_object()
        
        with transaction.atomic():
            # select_for_update prevents race conditions
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
                except IntegrityError:
                    # Double-like attempt blocked by DB constraint
                    return Response({'error': 'Already liked'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'liked': liked,
            'like_count': post.likes.count()
        })


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author').prefetch_related('likes')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Toggle like on a comment with race condition prevention"""
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
                except IntegrityError:
                    return Response({'error': 'Already liked'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'liked': liked,
            'like_count': comment.likes.count()
        })


class LeaderboardView(APIView):
    """
    Top 5 users by karma earned in the LAST 24 HOURS ONLY.
    
    Karma calculation:
    - 1 Like on your Post = 5 Karma
    - 1 Like on your Comment = 1 Karma
    
    This is calculated dynamically from Like timestamps,
    NOT stored in a simple integer field.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        cutoff = timezone.now() - timedelta(hours=24)
        
        # Simpler approach: calculate karma for each user individually
        # This is more reliable than complex nested aggregations
        
        # Get all recent likes
        recent_likes = Like.objects.filter(created_at__gte=cutoff).select_related(
            'post__author', 'comment__author'
        )
        
        # Calculate karma per user
        user_karma = {}
        for like in recent_likes:
            # Post like = 5 karma for post author
            if like.post_id:
                author_id = like.post.author_id
                if author_id not in user_karma:
                    user_karma[author_id] = {'karma': 0, 'username': like.post.author.username}
                user_karma[author_id]['karma'] += 5
            
            # Comment like = 1 karma for comment author
            if like.comment_id:
                author_id = like.comment.author_id
                if author_id not in user_karma:
                    user_karma[author_id] = {'karma': 0, 'username': like.comment.author.username}
                user_karma[author_id]['karma'] += 1
        
        # Sort by karma and take top 5
        sorted_users = sorted(
            [{'id': uid, 'username': data['username'], 'karma_24h': data['karma']} 
             for uid, data in user_karma.items()],
            key=lambda x: x['karma_24h'],
            reverse=True
        )[:5]
        
        return Response(sorted_users)


# CSRF-exempt authentication for public auth endpoints
class CsrfExemptSessionAuthentication:
    def authenticate(self, request):
        return None  # Allow unauthenticated access
    
    def enforce_csrf(self, request):
        return  # Skip CSRF check


class RegisterView(APIView):
    """Simple registration for demo purposes"""
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        name = request.data.get('name', '')
        
        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

        # Strict Password Validation
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
                # Create profile
                Profile.objects.create(user=user)
        except Exception as e:
            return Response({'error': 'Registration failed'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Custom login endpoint"""
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        from django.contrib.auth import authenticate, login
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """Custom logout endpoint"""
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        from django.contrib.auth import logout
        logout(request)
        return Response({'message': 'Logged out'})


class MeView(APIView):
    """Get or update current user info"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
            
        user = request.user
        
        # Update name
        if 'name' in request.data:
            user.first_name = request.data['name']
            user.save()
            
        # Update avatar
        if 'avatar' in request.FILES:
            # Ensure profile exists
            profile, created = Profile.objects.get_or_create(user=user)
            profile.avatar = request.FILES['avatar']
            profile.save()
            
        # Refresh serializers context
        return Response(UserSerializer(user, context={'request': request}).data)


class UserProfileView(APIView):
    """Get public profile stats for a user"""
    permission_classes = [AllowAny]
    
    def get(self, request, username):
        try:
            target_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
        # Calculate Total Karma (Lifetime)
        post_likes = Like.objects.filter(post__author=target_user).count()
        comment_likes = Like.objects.filter(comment__author=target_user).count()
        total_karma = (post_likes * 5) + (comment_likes * 1)
        
        # Get recent activity
        recent_posts = Post.objects.filter(author=target_user).order_by('-created_at')[:5]
        recent_comments = Comment.objects.filter(author=target_user).order_by('-created_at')[:5]
        
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
            'recent_comments': CommentSerializer(recent_comments, many=True, context={'request': request}).data
        })

