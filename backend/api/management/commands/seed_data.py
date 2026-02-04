"""
Comprehensive seed script to populate the database with rich dummy data.
Run with: python manage.py seed_data
"""
import random
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from api.models import (
    Post, Comment, Like, Profile, Follow, Block, Mute, Report, Notification,
    Community, CommunityMembership, Topic, ChatMessage,
    Course, Module, Lesson, Enrollment, LessonProgress, Assignment, AssignmentSubmission, CourseReview,
    Badge, UserBadge, UserPoints,
    Subscription, Payment
)


class Command(BaseCommand):
    help = 'Seeds the database with comprehensive dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Clear existing data (optional)
        self.stdout.write('Clearing existing data...')
        # Be careful with this in production!
        
        # Create Users with Profiles
        self.stdout.write('Creating users...')
        users = self.create_users()
        
        # Create Follow relationships
        self.stdout.write('Creating follow relationships...')
        self.create_follows(users)
        
        # Create Blocks and Mutes
        self.stdout.write('Creating blocks and mutes...')
        self.create_blocks_mutes(users)
        
        # Create Posts with nested comments (N+1 test)
        self.stdout.write('Creating posts with deeply nested comments...')
        posts = self.create_posts(users)
        
        # Create Likes
        self.stdout.write('Creating likes...')
        self.create_likes(users, posts)
        
        # Create Communities
        self.stdout.write('Creating communities...')
        communities = self.create_communities(users)
        
        # Create Courses with rich content
        self.stdout.write('Creating courses...')
        courses = self.create_courses(users, communities)
        
        # Create Enrollments and Reviews
        self.stdout.write('Creating enrollments and reviews...')
        self.create_enrollments_reviews(users, courses)
        
        # Create Badges and Points
        self.stdout.write('Creating badges and points...')
        self.create_badges_points(users)
        
        # Create Payments
        self.stdout.write('Creating payments...')
        self.create_payments(users, courses, communities)
        
        # Create Notifications
        self.stdout.write('Creating notifications...')
        self.create_notifications(users)
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def create_users(self):
        """Create 25 diverse users with profiles"""
        
        user_data = [
            ('alex_dev', 'Alex Rivera', 'Full-stack developer passionate about React and Django. Coffee addict ☕'),
            ('sarah_design', 'Sarah Chen', 'UI/UX Designer | Making the web beautiful one pixel at a time 🎨'),
            ('mike_backend', 'Mike Johnson', 'Backend engineer | Python & Go enthusiast | Open source contributor'),
            ('emma_product', 'Emma Watson', 'Product Manager | Building products people love 💡'),
            ('james_ml', 'James Lee', 'ML Engineer | Deep Learning | Computer Vision | AI Enthusiast 🤖'),
            ('olivia_frontend', 'Olivia Brown', 'Frontend Developer | React | Vue | TypeScript lover'),
            ('noah_devops', 'Noah Davis', 'DevOps Engineer | Kubernetes | Docker | Cloud Native'),
            ('sophia_data', 'Sophia Garcia', 'Data Scientist | Analytics | Visualization | Python'),
            ('william_mobile', 'William Martinez', 'Mobile Developer | React Native | iOS | Android'),
            ('ava_security', 'Ava Wilson', 'Security Engineer | Ethical Hacker | InfoSec'),
            ('ethan_qa', 'Ethan Anderson', 'QA Engineer | Test Automation | Selenium | Cypress'),
            ('mia_tech', 'Mia Thomas', 'Tech Lead | Architecture | Mentorship | Code Reviews'),
            ('lucas_startup', 'Lucas Jackson', 'Startup Founder | Entrepreneur | Building the future'),
            ('charlotte_writer', 'Charlotte White', 'Technical Writer | Documentation | Clear Communication'),
            ('henry_blockchain', 'Henry Harris', 'Blockchain Developer | Web3 | Smart Contracts'),
            ('amelia_ai', 'Amelia Clark', 'AI Researcher | NLP | LLMs | GPT'),
            ('jack_game', 'Jack Lewis', 'Game Developer | Unity | Unreal | Indie Games'),
            ('harper_cloud', 'Harper Robinson', 'Cloud Architect | AWS | Azure | GCP'),
            ('leo_cyber', 'Leo Walker', 'Cybersecurity Analyst | Penetration Testing'),
            ('ella_growth', 'Ella Hall', 'Growth Hacker | Marketing | SEO | Analytics'),
            ('daniel_db', 'Daniel Allen', 'Database Admin | PostgreSQL | MySQL | NoSQL'),
            ('grace_api', 'Grace Young', 'API Developer | REST | GraphQL | Microservices'),
            ('ryan_infra', 'Ryan King', 'Infrastructure Engineer | Terraform | Ansible'),
            ('chloe_scrum', 'Chloe Scott', 'Scrum Master | Agile Coach | Team Facilitator'),
            ('mason_code', 'Mason Green', 'Coding Instructor | Teaching | Mentoring | Community'),
        ]
        
        users = []
        for username, name, bio in user_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': name}
            )
            if created:
                user.set_password('demo123')
                user.save()
                
                # Create profile
                Profile.objects.get_or_create(user=user, defaults={'bio': bio})
                
                # Create user points
                UserPoints.objects.get_or_create(
                    user=user,
                    defaults={
                        'total_points': random.randint(50, 5000),
                        'level': random.randint(1, 15),
                        'streak_days': random.randint(0, 30)
                    }
                )
            
            users.append(user)
        
        return users

    def create_follows(self, users):
        """Create realistic follow graph"""
        for user in users:
            # Each user follows 3-12 others
            num_follows = random.randint(3, 12)
            to_follow = random.sample([u for u in users if u != user], num_follows)
            
            for follow_user in to_follow:
                Follow.objects.get_or_create(user_from=user, user_to=follow_user)

    def create_blocks_mutes(self, users):
        """Create some blocks and mutes"""
        # 10% of users have blocked someone
        for _ in range(len(users) // 10):
            blocker = random.choice(users)
            blocked = random.choice([u for u in users if u != blocker])
            Block.objects.get_or_create(blocker=blocker, blocked=blocked)
        
        # 15% have muted someone
        for _ in range(len(users) // 7):
            muter = random.choice(users)
            muted = random.choice([u for u in users if u != muter])
            Mute.objects.get_or_create(muter=muter, muted=muted)

    def create_posts(self, users):
        """Create posts with deep comment trees to test N+1"""
        
        post_contents = [
            "Just deployed to production on a Friday. Living dangerously! 🚀",
            "Hot take: Code reviews should focus on architecture, not syntax nitpicks.",
            "Spent 3 hours debugging. The bug? A missing semicolon. Classic.",
            "Anyone else feel like 80% of programming is naming things?",
            "Finally understood monads. Turns out I didn't need to understand monads.",
            "The best code is the code you never have to write.",
            "Refactoring legacy code is like archaeology, but scarier.",
            "Rubber duck debugging: still undefeated champion.",
            "My code works and I don't know why. Time to merge.",
            "Stack Overflow down? Guess I'll just panic.",
            "Documentation is love. Documentation is life.",
            "Git commit -m 'fixed stuff' // we've all been there",
            "Real developers test in production. 😎",
            "The cloud is just someone else's computer.",
            "Microservices: because one big problem is better as 100 small problems.",
            "Design patterns are great until you overuse them.",
            "Premature optimization is the root of all evil - Knuth",
            "Every 'temporary' solution becomes permanent.",
            "Debugging: being a detective where you're also the murderer.",
            "Tabs vs Spaces: the eternal debate continues.",
        ]
        
        comment_contents = [
            "This is so relatable!",
            "I felt this in my soul 😂",
            "Couldn't agree more.",
            "Hard disagree, but I respect your opinion.",
            "Can you elaborate on this?",
            "Brilliant insight!",
            "This changed my perspective.",
            "Exactly what I needed to hear today.",
            "Bold take, but you're right.",
            "As someone who's been there, yes.",
            "This deserves more upvotes.",
            "Saving this for later.",
            "Mind blown 🤯",
            "Thanks for sharing!",
            "Great point!",
            "I learned something new today.",
            "This is the way.",
            "Underrated comment.",
            "Big if true.",
            "Source: trust me bro",
        ]
        
        posts = []
        
        # Create 30 posts
        for i, content in enumerate(post_contents):
            author = random.choice(users)
            post = Post.objects.create(author=author, content=content)
            
            # Randomize created_at
            hours_ago = random.randint(1, 72)
            post.created_at = timezone.now() - timedelta(hours=hours_ago)
            post.save()
            
            # Create deeply nested comments for some posts (to test N+1)
            if i < 5:  # First 5 posts get deep trees
                self.create_deep_comments(post, users, comment_contents, depth=4, breadth=3)
            else:
                # Regular comments
                num_comments = random.randint(0, 8)
                for _ in range(num_comments):
                    comment = Comment.objects.create(
                        author=random.choice(users),
                        post=post,
                        content=random.choice(comment_contents)
                    )
                    
                    # Some replies
                    if random.random() < 0.5:
                        reply = Comment.objects.create(
                            author=random.choice(users),
                            post=post,
                            parent=comment,
                            content=random.choice(comment_contents)
                        )
            
            posts.append(post)
        
        return posts

    def create_deep_comments(self, post, users, comment_contents, depth=4, breadth=3, parent=None):
        """Recursively create nested comments to test N+1 optimization"""
        if depth == 0:
            return
        
        for _ in range(breadth):
            comment = Comment.objects.create(
                author=random.choice(users),
                post=post,
                parent=parent,
                content=random.choice(comment_contents)
            )
            
            # Recurse with decreasing breadth
            self.create_deep_comments(post, users, comment_contents, depth - 1, max(breadth - 1, 1), comment)

    def create_likes(self, users, posts):
        """Create likes on posts and comments"""
        for post in posts:
            # Random likes on post
            num_likes = random.randint(0, 15)
            likers = random.sample(users, min(num_likes, len(users)))
            
            for liker in likers:
                if liker != post.author:
                    Like.objects.get_or_create(user=liker, post=post)
            
            # Like some comments
            for comment in post.comments.all()[:5]:
                num_likes = random.randint(0, 5)
                likers = random.sample(users, min(num_likes, len(users)))
                for liker in likers:
                    if liker != comment.author:
                        Like.objects.get_or_create(user=liker, comment=comment)

    def create_communities(self, users):
        """Create diverse communities"""
        
        community_data = [
            ('Python Developers', 'A community for Python enthusiasts and developers', False, 0),
            ('React Masters', 'Learn and discuss React, Next.js, and modern frontend', False, 0),
            ('DevOps Academy', 'Docker, Kubernetes, CI/CD, and cloud infrastructure', True, 29.99),
            ('AI & ML Hub', 'Machine Learning, Deep Learning, and Artificial Intelligence', True, 49.99),
            ('Startup Founders', 'For entrepreneurs building the next big thing', False, 0),
        ]
        
        communities = []
        for name, desc, is_paid, price in community_data:
            creator = random.choice(users)
            community = Community.objects.create(
                name=name,
                description=desc,
                creator=creator,
                is_paid=is_paid,
                price=Decimal(str(price))
            )
            
            # Creator is owner
            CommunityMembership.objects.create(
                user=creator,
                community=community,
                role='owner'
            )
            
            # Add random members
            num_members = random.randint(5, 15)
            members = random.sample([u for u in users if u != creator], num_members)
            
            for member in members:
                role = random.choice(['member', 'member', 'member', 'moderator'])
                CommunityMembership.objects.create(
                    user=member,
                    community=community,
                    role=role
                )
            
            # Create topics
            topic_data = [
                ('General Discussion', 'General chat and discussions'),
                ('Help & Support', 'Get help from the community'),
                ('Showcase', 'Show off your projects'),
                ('Resources', 'Share useful resources')
            ]
            
            for topic_name, topic_desc in topic_data:
                topic = Topic.objects.create(
                    community=community,
                    name=topic_name,
                    description=topic_desc
                )
                
                # Create realistic Q&A conversations
                members_list = list(community.members.all())
                if len(members_list) < 2:
                    continue
                    
                if topic_name == 'Help & Support':
                    # Q&A style conversation
                    q_author = random.choice(members_list)
                    ChatMessage.objects.create(
                        topic=topic,
                        author=q_author,
                        content=f"Hey everyone! I'm having trouble with {community.name.split()[0].lower()}. Can anyone help me debug this error I'm getting?"
                    )
                    
                    a_author = random.choice([m for m in members_list if m != q_author])
                    ChatMessage.objects.create(
                        topic=topic,
                        author=a_author,
                        content="Sure! What's the error message you're seeing? Can you share more details?"
                    )
                    
                    ChatMessage.objects.create(
                        topic=topic,
                        author=q_author,
                        content="It says 'ImportError: cannot import name'. I've tried reinstalling but no luck."
                    )
                    
                    helper = random.choice([m for m in members_list if m not in [q_author, a_author]])
                    ChatMessage.objects.create(
                        topic=topic,
                        author=helper,
                        content="Have you checked your virtual environment? Make sure you're using the right one. Also try: pip list | grep package-name"
                    )
                    
                    ChatMessage.objects.create(
                        topic=topic,
                        author=q_author,
                        content="OMG that fixed it! Thank you so much! 🙏"
                    )
                    
                elif topic_name == 'Showcase':
                    # Show projects
                    creator = random.choice(members_list)
                    ChatMessage.objects.create(
                        topic=topic,
                        author=creator,
                        content=f"Just finished building a real-time dashboard using {community.name.split()[0]}! Check it out: github.com/example/project"
                    )
                    
                    viewer1 = random.choice([m for m in members_list if m != creator])
                    ChatMessage.objects.create(
                        topic=topic,
                        author=viewer1,
                        content="Wow, this looks amazing! How long did it take you to build?"
                    )
                    
                    ChatMessage.objects.create(
                        topic=topic,
                        author=creator,
                        content="About 2 weeks! The hardest part was optimizing the WebSocket connections."
                    )
                    
                    viewer2 = random.choice([m for m in members_list if m not in [creator, viewer1]])
                    ChatMessage.objects.create(
                        topic=topic,
                        author=viewer2,
                        content="This is exactly what I needed! Mind if I fork it? ⭐"
                    )
                    
                    ChatMessage.objects.create(
                        topic=topic,
                        author=creator,
                        content="Go for it! PRs welcome too 😊"
                    )
                    
                elif topic_name == 'Resources':
                    # Share resources
                    sharer = random.choice(members_list)
                    ChatMessage.objects.create(
                        topic=topic,
                        author=sharer,
                        content=f"Found this amazing tutorial on {community.name.split()[0]}: youtube.com/watch?v=example. Worth checking out!"
                    )
                    
                    viewer = random.choice([m for m in members_list if m != sharer])
                    ChatMessage.objects.create(
                        topic=topic,
                        author=viewer,
                        content="Thanks for sharing! Been looking for something like this."
                    )
                    
                    another = random.choice([m for m in members_list if m not in [sharer, viewer]])
                    ChatMessage.objects.create(
                        topic=topic,
                        author=another,
                        content="Also recommend checking out the official docs - they just updated them with new examples!"
                    )
                    
                else:  # General Discussion
                    # Discussion threads
                    starter = random.choice(members_list)
                    ChatMessage.objects.create(
                        topic=topic,
                        author=starter,
                        content=f"What's everyone's favorite feature of {community.name.split()[0]}? Mine is definitely the ecosystem."
                    )
                    
                    responder1 = random.choice([m for m in members_list if m != starter])
                    ChatMessage.objects.create(
                        topic=topic,
                        author=responder1,
                        content="The community! Everyone is so helpful here 💙"
                    )
                    
                    responder2 = random.choice([m for m in members_list if m not in [starter, responder1]])
                    ChatMessage.objects.create(
                        topic=topic,
                        author=responder2,
                        content="Performance and developer experience. It just works!"
                    )
                    
                    ChatMessage.objects.create(
                        topic=topic,
                        author=starter,
                        content="Great points! The DX is really top-notch."
                    )
                    
                    # Add some more variety
                    asker = random.choice(members_list)
                    ChatMessage.objects.create(
                        topic=topic,
                        author=asker,
                        content="Anyone attending the upcoming conference next month?"
                    )
                    
                    attendee = random.choice([m for m in members_list if m != asker])
                    ChatMessage.objects.create(
                        topic=topic,
                        author=attendee,
                        content="Yes! Already got my tickets. Can't wait for the talks!"
                    )
            
            communities.append(community)
        
        return communities

    def create_courses(self, users, communities):
        """Create courses with modules, lessons, and authentic notes"""
        
        course_data = [
            {
                'title': 'Full Stack Web Development Bootcamp',
                'description': 'Learn to build modern web applications from scratch using React, Node.js, and PostgreSQL.',
                'community': communities[0],
                'is_paid': True,
                'price': 99.99,
                'modules': [
                    {
                        'title': 'Frontend Fundamentals',
                        'description': 'HTML, CSS, JavaScript fundamentals',
                        'lessons': [
                            ('HTML Semantic Structure', 'text', 'Learn about semantic HTML5 elements like <header>, <nav>, <main>, <article>, <section>, and <footer>. Semantic HTML improves accessibility, SEO, and code maintainability. Use appropriate tags for content meaning, not just styling.', 30),
                            ('CSS Flexbox Layout', 'text', 'Flexbox is a one-dimensional layout system. Key concepts: flex-direction (row/column), justify-content (main axis alignment), align-items (cross axis alignment). Use flex-grow, flex-shrink, and flex-basis for responsive layouts.', 45),
                            ('JavaScript ES6+ Features', 'text', 'Modern JavaScript includes: arrow functions, destructuring, spread/rest operators, template literals, async/await, modules. Arrow functions have lexical this binding. Async/await makes promise handling cleaner.', 60),
                        ]
                    },
                    {
                        'title': 'React Deep Dive',
                        'description': 'Master React hooks, state management, and best practices',
                        'lessons': [
                            ('Understanding React Hooks', 'text', 'Hooks let you use state in functional components. useState for local state, useEffect for side effects, useContext for consuming context. Custom hooks enable reusable logic. Rules: only call at top level, only in React functions.', 50),
                            ('State Management with Context', 'text', 'Context API provides global state without prop drilling. Create context with createContext(), provide with Provider, consume with useContext(). Best for theme, auth, language. For complex state, consider Redux or Zustand.', 40),
                            ('Building a Todo App', 'assignment', 'Create a full-featured todo app with CRUD operations, filtering, and localStorage persistence. Apply React best practices.', 120),
                        ]
                    },
                ]
            },
            {
                'title': 'Machine Learning Fundamentals',
                'description': 'Introduction to ML concepts, algorithms, and implementation with Python and scikit-learn.',
                'community': communities[3],
                'is_paid': True,
                'price': 149.99,
                'modules': [
                    {
                        'title': 'ML Basics',
                        'description': 'Core concepts and supervised learning',
                        'lessons': [
                            ('Supervised vs Unsupervised Learning', 'text', 'Supervised learning uses labeled data (classification/regression). Unsupervised finds patterns in unlabeled data (clustering/dimensionality reduction). Semi-supervised combines both. Choose based on data availability and problem type.', 40),
                            ('Linear Regression in Depth', 'text', 'Linear regression models relationships using y = mx + b. Ordinary Least Squares minimizes sum of squared residuals. Assumptions: linearity, independence, homoscedasticity, normality. Evaluate with R², MSE, RMSE. Watch for multicollinearity.', 55),
                            ('Training Your First Model', 'assignment', 'Implement linear regression from scratch, then compare with scikit-learn. Use cross-validation and evaluate performance.', 90),
                        ]
                    },
                ]
            },
            {
                'title': 'DevOps Mastery: Docker to Kubernetes',
                'description': 'Complete guide to containerization, orchestration, and cloud-native deployment strategies.',
                'community': communities[2],
                'is_paid': True,
                'price': 129.99,
                'modules': [
                    {
                        'title': 'Docker Essentials',
                        'description': 'Containerization with Docker',
                        'lessons': [
                            ('Docker Architecture', 'text', 'Docker uses a client-server architecture. Docker daemon builds, runs containers. Images are immutable templates built from Dockerfiles. Containers are runtime instances. Layered filesystem enables efficient storage and caching.', 35),
                            ('Writing Efficient Dockerfiles', 'text', 'Dockerfile best practices: use official base images, minimize layers with multi-line RUN commands, leverage build cache by ordering commands from least to most frequently changing, use .dockerignore, prefer COPY over ADD, run as non-root user.', 45),
                            ('Docker Compose for Multi-Container Apps', 'text', 'Docker Compose defines multi-container applications in YAML. Specify services, networks, volumes. Use environment variables for configuration. Commands: docker-compose up/down, logs, exec. Perfect for local development environments.', 50),
                        ]
                    },
                    {
                        'title': 'Kubernetes Orchestration',
                        'description': 'Container orchestration at scale',
                        'lessons': [
                            ('Kubernetes Core Concepts', 'text', 'K8s orchestrates containers at scale. Key objects: Pods (smallest unit), Deployments (manage replicas), Services (networking), ConfigMaps/Secrets (configuration). Control plane manages cluster state. Nodes run workloads. Declarative configuration via YAML.', 60),
                            ('Deploying Apps to K8s', 'assignment', 'Deploy a multi-tier application to Kubernetes with proper resource limits, health checks, and auto-scaling.', 120),
                        ]
                    },
                ]
            },
        ]
        
        courses = []
        for course_info in course_data:
            instructor = random.choice(users)
            
            course = Course.objects.create(
                title=course_info['title'],
                description=course_info['description'],
                instructor=instructor,
                community=course_info.get('community'),
                is_published=True,
                is_paid=course_info['is_paid'],
                price=Decimal(str(course_info['price']))
            )
            
            for mod_idx, module_info in enumerate(course_info['modules']):
                module = Module.objects.create(
                    course=course,
                    title=module_info['title'],
                    description=module_info['description'],
                    order=mod_idx
                )
                
                for lesson_idx, (title, content_type, content, duration) in enumerate(module_info['lessons']):
                    lesson = Lesson.objects.create(
                        module=module,
                        title=title,
                        content_type=content_type,
                        content=content,
                        duration_minutes=duration,
                        order=lesson_idx,
                        is_free=(lesson_idx == 0)  # First lesson is free preview
                    )
                    
                    # Create assignment if needed
                    if content_type == 'assignment':
                        Assignment.objects.create(
                            lesson=lesson,
                            instructions=content
                        )
            
            courses.append(course)
        
        return courses

    def create_enrollments_reviews(self, users, courses):
        """Create enrollments, progress, and reviews"""
        for course in courses:
            # Random enrollments
            num_enrolled = random.randint(10, 20)
            enrolled_users = random.sample(users, num_enrolled)
            
            for user in enrolled_users:
                enrollment = Enrollment.objects.create(
                    user=user,
                    course=course
                )
                
                # Random progress
                all_lessons = Lesson.objects.filter(module__course=course)
                completed_lessons = random.sample(
                    list(all_lessons),
                    random.randint(0, all_lessons.count())
                )
                
                for lesson in completed_lessons:
                    LessonProgress.objects.create(
                        user=user,
                        lesson=lesson,
                        completed=True,
                        completed_at=timezone.now() - timedelta(days=random.randint(1, 30))
                    )
                
                # 50% chance of review
                if random.random() < 0.5:
                    rating = random.randint(3, 5)
                    reviews = [
                        "Excellent course! Learned so much.",
                        "Great content and well-structured lessons.",
                        "The instructor explains concepts clearly.",
                        "Perfect for beginners and intermediates.",
                        "Highly recommend this course!",
                        "Worth every penny. Great investment.",
                        "Clear explanations and practical examples.",
                        "This course exceeded my expectations.",
                    ]
                    
                    CourseReview.objects.create(
                        course=course,
                        user=user,
                        rating=rating,
                        review_text=random.choice(reviews)
                    )

    def create_badges_points(self, users):
        """Create badges and award to users"""
        
        badge_data = [
            ('First Steps', 'Created your first post', '🚀', 10),
            ('Conversationalist', 'Posted 10 comments', '💬', 50),
            ('Popular', 'Received 50 likes', '⭐', 100),
            ('Knowledge Seeker', 'Enrolled in a course', '📚', 20),
            ('Dedicated Learner', 'Completed 5 lessons', '🎓', 200),
            ('Community Builder', 'Joined 3 communities', '👥', 150),
            ('Streak Master', 'Maintained 7-day streak', '🔥', 300),
            ('Expert', 'Reached level 10', '🏆', 1000),
        ]
        
        for name, desc, icon, points_req in badge_data:
            badge, _ = Badge.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'icon': icon,
                    'points_required': points_req
                }
            )
            
            # Award to eligible users
            for user in users:
                if hasattr(user, 'points') and user.points.total_points >= points_req:
                    if random.random() < 0.7:  # 70% chance if eligible
                        UserBadge.objects.get_or_create(user=user, badge=badge)

    def create_payments(self, users, courses, communities):
        """Create payment records"""
        payment_count = 0
        
        # Course purchases
        for course in courses:
            if course.is_paid:
                enrollments = Enrollment.objects.filter(course=course)[:10]
                for enrollment in enrollments:
                    Payment.objects.create(
                        user=enrollment.user,
                        amount=course.price,
                        course=course,
                        payment_method='stripe',
                        transaction_id=f'txn_{payment_count:06d}',
                        status='completed'
                    )
                    payment_count += 1
        
        # Community subscriptions
        for community in communities:
            if community.is_paid:
                memberships = CommunityMembership.objects.filter(community=community, role='member')[:5]
                for membership in memberships:
                    subscription = Subscription.objects.create(
                        user=membership.user,
                        community=community,
                        tier='premium',
                        is_active=True,
                        expires_at=timezone.now() + timedelta(days=30)
                    )
                    
                    Payment.objects.create(
                        user=membership.user,
                        amount=community.price,
                        subscription=subscription,
                        payment_method='paypal',
                        transaction_id=f'txn_{payment_count:06d}',
                        status='completed'
                    )
                    payment_count += 1

    def create_notifications(self, users):
        """Create sample notifications"""
        notification_templates = [
            ('like', '{} liked your post', '/post/{}'),
            ('comment', '{} commented on your post', '/post/{}'),
            ('follow', '{} started following you', '/profile/{}'),
            ('course', 'New lesson available in {}', '/course/{}'),
            ('badge', 'Congratulations! You earned the {} badge', '/profile'),
        ]
        
        for user in users[:10]:  # First 10 users get notifications
            num_notifications = random.randint(2, 8)
            for _ in range(num_notifications):
                notif_type, message_template, link_template = random.choice(notification_templates)
                other_user = random.choice([u for u in users if u != user])
                
                if notif_type == 'badge':
                    message = message_template.format('First Steps')
                    link = link_template
                else:
                    message = message_template.format(other_user.username)
                    link = link_template.format(random.randint(1, 10))
                
                Notification.objects.create(
                    user=user,
                    type=notif_type,
                    message=message,
                    link=link,
                    read=random.choice([True, False])
                )
