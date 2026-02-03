from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Like


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='first_name', read_only=True)
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'avatar']
        
    def get_avatar(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.avatar.url)
            return obj.profile.avatar.url
        return None


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'content', 'created_at', 'like_count', 'replies', 'parent', 'user_has_liked']
        read_only_fields = ['author', 'created_at']
    
    def get_like_count(self, obj):
        # Use prefetched likes if available, else query
        likes = getattr(obj, 'prefetched_likes', None)
        if likes is not None:
            return len(likes) if hasattr(likes, '__len__') else likes.count()
        return obj.likes.count()
    
    def get_replies(self, obj):
        # Get replies from prefetched data if available
        replies = getattr(obj, 'prefetched_replies', None)
        if replies is None:
            replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data
    
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Use prefetched likes if available
            likes = getattr(obj, 'prefetched_likes', None)
            if likes is None:
                likes = obj.likes.all()
            return any(like.user_id == request.user.id for like in likes)
        return False


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'like_count', 'comment_count', 'comments', 'user_has_liked']
        read_only_fields = ['author', 'created_at']
    
    def get_like_count(self, obj):
        # Try annotated value first, then count
        if hasattr(obj, '_like_count'):
            return obj._like_count
        like_count = getattr(obj, 'like_count', None)
        if isinstance(like_count, int):
            return like_count
        return obj.likes.count()
    
    def get_comment_count(self, obj):
        if hasattr(obj, 'comment_count') and isinstance(obj.comment_count, int):
            return obj.comment_count
        return obj.comments.count()
    
    def get_comments(self, obj):
        # Get only top-level comments (no parent), build tree from there
        all_comments = getattr(obj, 'prefetched_comments', None)
        if all_comments is None:
            all_comments = list(obj.comments.select_related('author').prefetch_related('likes').all())
        
        # Attach prefetched likes to each comment
        for comment in all_comments:
            if not hasattr(comment, 'prefetched_likes'):
                comment.prefetched_likes = list(comment.likes.all())
        
        # Build a lookup map for efficient tree construction
        comment_map = {c.id: c for c in all_comments}
        
        # Attach replies to each comment
        for comment in all_comments:
            comment.prefetched_replies = []
        
        for comment in all_comments:
            if comment.parent_id and comment.parent_id in comment_map:
                comment_map[comment.parent_id].prefetched_replies.append(comment)
        
        # Return only top-level comments
        top_level = [c for c in all_comments if c.parent_id is None]
        return CommentSerializer(top_level, many=True, context=self.context).data
    
    def get_user_has_liked(self, obj):
        # Use DB annotation if available (most robust)
        if hasattr(obj, 'has_liked_annotation'):
            return obj.has_liked_annotation
            
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            likes = getattr(obj, 'prefetched_likes', None)
            if likes is None:
                likes = obj.likes.all()
            return any(like.user_id == request.user.id for like in likes)
        return False


class PostListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view (no nested comments)"""
    author = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'like_count', 'comment_count', 'user_has_liked']
    
    def get_like_count(self, obj):
        # Try annotated value first, then count
        like_count = getattr(obj, 'like_count', None)
        if isinstance(like_count, int):
            return like_count
        return obj.likes.count()
    
    def get_comment_count(self, obj):
        comment_count = getattr(obj, 'comment_count', None)
        if isinstance(comment_count, int):
            return comment_count
        return obj.comments.count()
    
    def get_user_has_liked(self, obj):
        # Use DB annotation if available (most robust)
        if hasattr(obj, 'has_liked_annotation'):
            return obj.has_liked_annotation
            
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            likes = getattr(obj, 'prefetched_likes', obj.likes.all())
            return any(like.user_id == request.user.id for like in likes)
        return False


class LeaderboardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    karma_24h = serializers.IntegerField()
