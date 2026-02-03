from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from .models import Post, Comment, Like


class LeaderboardTests(TestCase):
    """Test the 24-hour karma leaderboard calculation"""
    
    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.user1 = User.objects.create_user('alice', password='pass123')
        self.user2 = User.objects.create_user('bob', password='pass123')
        self.user3 = User.objects.create_user('charlie', password='pass123')
        self.liker = User.objects.create_user('liker', password='pass123')
    
    def test_leaderboard_only_counts_last_24h(self):
        """Karma from likes older than 24h should NOT count"""
        # Alice's post liked recently (should count: 5 karma)
        alice_post = Post.objects.create(author=self.user1, content="Alice's post")
        recent_like = Like.objects.create(user=self.liker, post=alice_post)
        
        # Bob's post liked 25 hours ago (should NOT count)
        bob_post = Post.objects.create(author=self.user2, content="Bob's post")
        old_like = Like.objects.create(user=self.liker, post=bob_post)
        # Manually set created_at to 25 hours ago
        Like.objects.filter(pk=old_like.pk).update(
            created_at=timezone.now() - timedelta(hours=25)
        )
        
        # Charlie's comment liked recently (should count: 1 karma)
        charlie_comment = Comment.objects.create(
            author=self.user3, 
            post=alice_post, 
            content="Charlie's comment"
        )
        Like.objects.create(user=self.liker, comment=charlie_comment)
        
        # Fetch leaderboard
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        usernames = [entry['username'] for entry in data]
        
        # Alice should be first with 5 karma (post like)
        self.assertEqual(data[0]['username'], 'alice')
        self.assertEqual(data[0]['karma_24h'], 5)
        
        # Charlie should be second with 1 karma (comment like)
        self.assertIn('charlie', usernames)
        charlie_entry = next(e for e in data if e['username'] == 'charlie')
        self.assertEqual(charlie_entry['karma_24h'], 1)
        
        # Bob should NOT be in leaderboard (like was 25h ago)
        self.assertNotIn('bob', usernames)
    
    def test_post_like_gives_5_karma(self):
        """Each like on a post = 5 karma for the author"""
        post = Post.objects.create(author=self.user1, content="Test post")
        Like.objects.create(user=self.user2, post=post)
        Like.objects.create(user=self.user3, post=post)
        
        response = self.client.get('/api/leaderboard/')
        data = response.json()
        
        alice_karma = next(e for e in data if e['username'] == 'alice')['karma_24h']
        self.assertEqual(alice_karma, 10)  # 2 likes × 5 = 10


class LikeTests(TestCase):
    """Test like functionality and race condition prevention"""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass123')
        self.other_user = User.objects.create_user('other', password='pass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.post = Post.objects.create(author=self.other_user, content="Test post")
    
    def test_cannot_double_like_post(self):
        """User cannot like the same post twice"""
        # First like
        response = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])
        
        # Second like should toggle OFF (unlike)
        response = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['liked'])
        
        # Like count should be 0
        self.assertEqual(Like.objects.filter(post=self.post).count(), 0)
    
    def test_unique_constraint_prevents_duplicate(self):
        """DB constraint prevents duplicate likes even if created directly"""
        Like.objects.create(user=self.user, post=self.post)
        
        # Attempting to create duplicate should raise IntegrityError
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Like.objects.create(user=self.user, post=self.post)


class CommentTreeTests(TestCase):
    """Test nested comment retrieval efficiency"""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass123')
        self.post = Post.objects.create(author=self.user, content="Test post")
    
    def test_nested_comments_fetched_efficiently(self):
        """50 comments should not cause 50 queries"""
        # Create nested comment tree
        parent = None
        for i in range(10):
            comment = Comment.objects.create(
                author=self.user,
                post=self.post,
                parent=parent,
                content=f"Comment {i}"
            )
            parent = comment if i % 3 == 0 else parent  # Some nesting
        
        # Fetch post with comments
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(f'/api/posts/{self.post.id}/')
        
        # Should be a small constant number of queries, not N+1
        # Typically: 1 for post, 1 for comments, 1 for likes prefetch
        self.assertLess(len(context), 10, 
            f"Too many queries ({len(context)}). N+1 problem detected!")
