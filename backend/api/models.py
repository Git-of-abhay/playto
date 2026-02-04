from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE, related_name='likes')
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_post_like', condition=models.Q(post__isnull=False)),
            models.UniqueConstraint(fields=['user', 'comment'], name='unique_comment_like', condition=models.Q(comment__isnull=False)),
        ]
        indexes = [
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        target = f"post {self.post_id}" if self.post else f"comment {self.comment_id}"
        return f"{self.user.username} liked {target}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"


class Follow(models.Model):
    user_from = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_from', 'user_to')
        indexes = [
            models.Index(fields=['user_from', 'user_to']),
        ]

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"


class Block(models.Model):
    blocker = models.ForeignKey(User, related_name='blocking', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"


class Mute(models.Model):
    muter = models.ForeignKey(User, related_name='muting', on_delete=models.CASCADE)
    muted = models.ForeignKey(User, related_name='muted_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('muter', 'muted')

    def __str__(self):
        return f"{self.muter} muted {self.muted}"


class Report(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('violence', 'Violence'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='reports_received')
    reported_post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        target = f"user {self.reported_user}" if self.reported_user else f"post {self.reported_post_id}"
        return f"Report by {self.reporter} about {target}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
        ('course', 'Course Update'),
        ('badge', 'Badge Earned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} notification for {self.user.username}"


# ==================== COMMUNITY CHAT ====================

class Community(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_communities')
    members = models.ManyToManyField(User, through='CommunityMembership', related_name='communities')
    avatar = models.ImageField(upload_to='communities/', null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Communities'

    def __str__(self):
        return self.name


class CommunityMembership(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'community')

    def __str__(self):
        return f"{self.user.username} in {self.community.name}"


class Topic(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} in {self.community.name}"


class ChatMessage(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='thread_replies')
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message by {self.author.username} in {self.topic.name}"


# ==================== COURSE SYSTEM ====================

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_created')
    community = models.ForeignKey(Community, null=True, blank=True, on_delete=models.CASCADE, related_name='courses')
    thumbnail = models.ImageField(upload_to='courses/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} - {self.course.title}"


class Lesson(models.Model):
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content = models.TextField(blank=True)  # For text lessons
    video_url = models.URLField(blank=True)  # For video lessons
    file = models.FileField(upload_to='lessons/', null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    order = models.IntegerField(default=0)
    is_free = models.BooleanField(default=False)  # Free preview lessons

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} - {self.module.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


class Assignment(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='assignment_detail')
    instructions = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Assignment for {self.lesson.title}"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    content = models.TextField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(null=True, blank=True)  # 0-100
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('assignment', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.assignment.lesson.title}"


class CourseReview(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    rating = models.IntegerField()  # 1-5
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}★)"


# ==================== GAMIFICATION ====================

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # emoji or icon name
    points_required = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    total_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streak_days = models.IntegerField(default=0)
    last_activity = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.total_points} points"


# ==================== MONETIZATION ====================

class Subscription(models.Model):
    TIER_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='subscriptions')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.community.name} ({self.tier})"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    subscription = models.ForeignKey(Subscription, null=True, blank=True, on_delete=models.SET_NULL)
    payment_method = models.CharField(max_length=50)  # stripe, paypal, etc
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, default='pending')  # pending, completed, failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ${self.amount}"
