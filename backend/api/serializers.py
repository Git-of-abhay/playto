from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Post, Comment, Like, Profile, Follow, Block, Mute, Report, Notification,
    Community, CommunityMembership, Topic, ChatMessage,
    Course, Module, Lesson, Enrollment, LessonProgress, Assignment, AssignmentSubmission, CourseReview,
    Badge, UserBadge, UserPoints,
    Subscription, Payment
)


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='first_name', read_only=True)
    avatar = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'avatar', 'followers_count', 'following_count', 'is_following', 'points', 'badges']
        
    def get_avatar(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.avatar.url)
            return obj.profile.avatar.url
        return None

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(user_from=request.user).exists()
        return False

    def get_points(self, obj):
        if hasattr(obj, 'points'):
            return {'total': obj.points.total_points, 'level': obj.points.level, 'streak': obj.points.streak_days}
        return {'total': 0, 'level': 1, 'streak': 0}

    def get_badges(self, obj):
        return obj.badges.count()


# ============ EXISTING SERIALIZERS ============

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
        likes = getattr(obj, 'prefetched_likes', None)
        if likes is not None:
            return len(likes) if hasattr(likes, '__len__') else likes.count()
        return obj.likes.count()
    
    def get_replies(self, obj):
        replies = getattr(obj, 'prefetched_replies', None)
        if replies is None:
            replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data
    
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
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
        all_comments = getattr(obj, 'prefetched_comments', None)
        if all_comments is None:
            all_comments = list(obj.comments.select_related('author').prefetch_related('likes').all())
        
        for comment in all_comments:
            if not hasattr(comment, 'prefetched_likes'):
                comment.prefetched_likes = list(comment.likes.all())
        
        comment_map = {c.id: c for c in all_comments}
        
        for comment in all_comments:
            comment.prefetched_replies = []
        
        for comment in all_comments:
            if comment.parent_id and comment.parent_id in comment_map:
                comment_map[comment.parent_id].prefetched_replies.append(comment)
        
        top_level = [c for c in all_comments if c.parent_id is None]
        return CommentSerializer(top_level, many=True, context=self.context).data
    
    def get_user_has_liked(self, obj):
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
    author = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'like_count', 'comment_count', 'user_has_liked']
    
    def get_like_count(self, obj):
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
        if hasattr(obj, 'has_liked_annotation'):
            return obj.has_liked_annotation
            
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            likes = getattr(obj, 'prefetched_likes', obj.likes.all())
            return any(like.user_id == request.user.id for like in likes)
        return False


class ProfileCommentSerializer(CommentSerializer):
    post_title = serializers.CharField(source='post.content', read_only=True)
    post_author_username = serializers.CharField(source='post.author.username', read_only=True)
    
    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ['post_title', 'post_author_username']


class LeaderboardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    karma_24h = serializers.IntegerField()


# ============ NOTIFICATION SERIALIZERS ============

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'message', 'link', 'read', 'created_at']
        read_only_fields = ['created_at']


# ============ REPORT SERIALIZER ============

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'reported_user', 'reported_post', 'reason', 'description', 'created_at']
        read_only_fields = ['reporter', 'created_at']


# ============ COMMUNITY & CHAT SERIALIZERS ============

class CommunitySerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'creator', 'avatar', 'is_paid', 'price', 'member_count', 'is_member', 'created_at']
        read_only_fields = ['creator', 'created_at']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False


class TopicSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = ['id', 'community', 'name', 'description', 'message_count', 'created_at']
        read_only_fields = ['created_at']

    def get_message_count(self, obj):
        return obj.messages.count()


class ChatMessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'topic', 'author', 'content', 'parent', 'file', 'replies_count', 'created_at', 'edited_at']
        read_only_fields = ['author', 'created_at']

    def get_replies_count(self, obj):
        return obj.thread_replies.count()


# ============ COURSE SERIALIZERS ============

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'module', 'title', 'content_type', 'content', 'video_url', 'duration_minutes', 'order', 'is_free']
        read_only_fields = ['id']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'description', 'order', 'lessons', 'lesson_count']
        read_only_fields = ['id']

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    enrolled_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'thumbnail', 'is_published', 'is_paid', 'price', 'modules', 'enrolled_count', 'is_enrolled', 'created_at']
        read_only_fields = ['instructor', 'created_at']

    def get_enrolled_count(self, obj):
        return obj.enrollments.count()

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(user=request.user).exists()
        return False


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'enrolled_at', 'completed', 'completed_at', 'progress_percentage']
        read_only_fields = ['enrolled_at']

    def get_progress_percentage(self, obj):
        total_lessons = Lesson.objects.filter(module__course=obj.course).count()
        if total_lessons == 0:
            return 0
        completed_lessons = LessonProgress.objects.filter(
            user=obj.user,
            lesson__module__course=obj.course,
            completed=True
        ).count()
        return int((completed_lessons / total_lessons) * 100)


class CourseReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CourseReview
        fields = ['id', 'course', 'user', 'rating', 'review_text', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


# ==================== GAMIFICATION SERIALIZERS ====================

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'icon', 'points_required']


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'earned_at']
        read_only_fields = ['earned_at']


class UserPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoints
        fields = ['total_points', 'level', 'streak_days', 'last_activity']
        read_only_fields = ['last_activity']


# ============ MONETIZATION SERIALIZERS ============

class SubscriptionSerializer(serializers.ModelSerializer):
    community = CommunitySerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'community', 'tier', 'is_active', 'started_at', 'expires_at']
        read_only_fields = ['started_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'course', 'subscription', 'payment_method', 'status', 'created_at']
        read_only_fields = ['created_at']
