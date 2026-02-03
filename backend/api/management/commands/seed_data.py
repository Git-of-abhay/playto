from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Post, Comment, Like, Profile
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Seeds the database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        fake = Faker()

        # Create Users
        users = []
        for _ in range(50):
            username = fake.unique.user_name()
            email = fake.email()
            password = 'password123'
            
            # Avoid duplicate usernames
            if User.objects.filter(username=username).exists():
                continue
                
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = fake.name()
            user.save()
            Profile.objects.create(user=user) # Ensure profile exists
            users.append(user)
        
        self.stdout.write(f'Created {len(users)} users')

        if not users:
            self.stdout.write(self.style.WARNING('No new users created (maybe they already exist?)'))
            users = list(User.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR('No users found in database to attach content to.'))
            return

        # Create Posts
        posts = []
        for _ in range(50):
            author = random.choice(users)
            content = fake.paragraph(nb_sentences=3)
            post = Post.objects.create(author=author, content=content)
            posts.append(post)
        
        self.stdout.write(f'Created {len(posts)} posts')

        # Create Comments
        for _ in range(200):
            author = random.choice(users)
            post = random.choice(posts)
            content = fake.sentence()
            Comment.objects.create(author=author, post=post, content=content)
        
        self.stdout.write('Created 200 comments')

        # Create Likes (Posts)
        for _ in range(300):
            user = random.choice(users)
            post = random.choice(posts)
            # Avoid duplicate likes
            if not Like.objects.filter(user=user, post=post).exists():
                Like.objects.create(user=user, post=post)
        
        self.stdout.write('Created random post likes')

        # Create Likes (Comments)
        comments = list(Comment.objects.all())
        for _ in range(200):
            user = random.choice(users)
            comment = random.choice(comments)
            if not Like.objects.filter(user=user, comment=comment).exists():
                Like.objects.create(user=user, comment=comment)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))
