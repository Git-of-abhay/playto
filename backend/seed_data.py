"""
Seed script to populate database with dummy data.
Run with: python manage.py shell < seed_data.py
"""
import random
from django.contrib.auth.models import User
from api.models import Post, Comment, Like
from django.utils import timezone
from datetime import timedelta

# Create users
usernames = ['alex', 'sam', 'jordan', 'taylor', 'casey', 'morgan', 'riley', 'drew', 'avery', 'quinn']
users = []
for name in usernames:
    user, created = User.objects.get_or_create(username=name, defaults={'password': 'unused'})
    if created:
        user.set_password('demo123')
        user.save()
    users.append(user)

print(f"Created/found {len(users)} users")

# Sample post content
post_contents = [
    "Just shipped a major feature. The feeling when everything works on the first deploy is unmatched.",
    "Hot take: tabs are better than spaces. Fight me.",
    "Anyone else spend more time naming variables than actually writing code?",
    "Finally understood recursion. Turns out you just need to understand recursion first.",
    "Day 47 of pretending to know what I'm doing. Nobody has noticed yet.",
    "The best code is no code. Unfortunately, my boss disagrees.",
    "Just discovered dark mode. How did I live before this?",
    "Debugging is like being a detective in a crime movie where you're also the murderer.",
    "My code works and I have no idea why. Time to ship it.",
    "Stack Overflow just saved my life for the 1000th time today.",
    "The only thing worse than documentation is no documentation.",
    "Why do we call it 'refactoring' when 'making it actually work' is more accurate?",
    "Just realized my rubber duck is a better debugger than most of my colleagues.",
    "Spent 3 hours on a bug. It was a typo. Classic.",
    "Building side projects is my cardio.",
    "Merge conflicts are just the universe testing your patience.",
    "Clean code is not about perfection, it's about communication.",
    "The best time to write tests was before the bug. The second best time is now.",
    "Agile is just organized chaos, change my mind.",
    "Every great developer you know got there by solving problems they were unqualified for.",
    "Just automated my job. Now I have more time to automate more of my job.",
    "The real treasure was the bugs we fixed along the way.",
    "Code reviews are just polite arguments about semicolons.",
    "Started learning Rust. Send help.",
    "Remember: legacy code is just code that works and makes money.",
]

comment_contents = [
    "This is so true!",
    "I felt this in my soul.",
    "Couldn't agree more.",
    "Wait, you guys are getting deploys that work?",
    "Tabs gang rise up!",
    "Spaces forever, sorry not sorry.",
    "I spend at least 30% of my time on naming.",
    "The recursion joke never gets old... because it keeps calling itself.",
    "Imposter syndrome is real.",
    "Shipping fast > shipping perfect.",
    "Dark mode is the way.",
    "Been there, done that, got the t-shirt.",
    "This is why I drink coffee.",
    "Underrated take.",
    "Big if true.",
    "The duck knows all.",
    "Story of my life.",
    "Merge conflicts give me nightmares.",
    "Clean code is a journey, not a destination.",
    "Tests? In this economy?",
]

# Create posts
posts = []
for i, content in enumerate(post_contents):
    author = random.choice(users)
    post = Post.objects.create(
        author=author,
        content=content,
    )
    # Randomize created_at within last 48 hours
    hours_ago = random.randint(0, 48)
    post.created_at = timezone.now() - timedelta(hours=hours_ago)
    post.save()
    posts.append(post)

print(f"Created {len(posts)} posts")

# Create comments (some nested)
comments = []
for post in posts:
    # 0-4 comments per post
    num_comments = random.randint(0, 4)
    for _ in range(num_comments):
        comment = Comment.objects.create(
            author=random.choice(users),
            post=post,
            content=random.choice(comment_contents),
        )
        # Randomize created_at
        hours_ago = random.randint(0, 24)
        comment.created_at = timezone.now() - timedelta(hours=hours_ago)
        comment.save()
        comments.append(comment)
        
        # 30% chance of a reply
        if random.random() < 0.3:
            reply = Comment.objects.create(
                author=random.choice(users),
                post=post,
                parent=comment,
                content=random.choice(comment_contents),
            )
            hours_ago = random.randint(0, 12)
            reply.created_at = timezone.now() - timedelta(hours=hours_ago)
            reply.save()
            comments.append(reply)

print(f"Created {len(comments)} comments")

# Create likes (spread across last 24-48 hours)
like_count = 0

# Like posts
for post in posts:
    # Random number of likes (0-6)
    num_likes = random.randint(0, 6)
    likers = random.sample(users, min(num_likes, len(users)))
    for liker in likers:
        if liker != post.author:  # Don't self-like
            like, created = Like.objects.get_or_create(user=liker, post=post)
            if created:
                # Randomize timestamp (mostly within 24h for leaderboard)
                hours_ago = random.randint(0, 30)
                like.created_at = timezone.now() - timedelta(hours=hours_ago)
                like.save()
                like_count += 1

# Like comments
for comment in random.sample(comments, min(30, len(comments))):
    num_likes = random.randint(0, 3)
    likers = random.sample(users, min(num_likes, len(users)))
    for liker in likers:
        if liker != comment.author:
            like, created = Like.objects.get_or_create(user=liker, comment=comment)
            if created:
                hours_ago = random.randint(0, 24)
                like.created_at = timezone.now() - timedelta(hours=hours_ago)
                like.save()
                like_count += 1

print(f"Created {like_count} likes")
print("Done! Seed data created successfully.")
