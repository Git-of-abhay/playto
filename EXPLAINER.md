# EXPLAINER

Here's how I approached the trickier parts of this project.

---

## The Tree (Nested Comments)

I went with an **adjacency list** model - each comment has a `parent` field pointing to its parent comment (null for top-level ones).

```python
class Comment(models.Model):
    post = models.ForeignKey(Post, ...)
    parent = models.ForeignKey('self', null=True, blank=True, ...)
    content = models.TextField()
```

The challenge was avoiding the N+1 query problem. If I had 50 comments and fetched each one's replies separately, that's 50+ database hits. Not great.

**My solution:** Fetch ALL comments for a post in one query, then build the tree in Python:

```python
# One query gets everything
all_comments = list(post.comments.select_related('author').all())

# Build a lookup map
comment_map = {c.id: c for c in all_comments}

# Link children to parents
for comment in all_comments:
    if comment.parent_id:
        parent = comment_map[comment.parent_id]
        parent.replies.append(comment)
```

This way I'm doing 2-3 queries total, regardless of how deep the nesting goes.

---

## The Math (Leaderboard)

The requirement was to show karma earned in the last 24 hours *only*, and to calculate it dynamically (not just store a counter on the user).

I store timestamps on every like, then query like this:

```python
cutoff = timezone.now() - timedelta(hours=24)

# Get recent likes
recent_likes = Like.objects.filter(created_at__gte=cutoff).select_related(
    'post__author', 'comment__author'
)

# Tally up karma
user_karma = {}
for like in recent_likes:
    if like.post_id:
        author = like.post.author
        user_karma[author.id] = user_karma.get(author.id, 0) + 5  # post = 5 karma
    if like.comment_id:
        author = like.comment.author
        user_karma[author.id] = user_karma.get(author.id, 0) + 1  # comment = 1 karma
```

Sorted and sliced to get top 5. Simple and it works.

---

## The AI Audit

I used AI assistance during development. Here's one place it messed up:

### The Bug: Complex ORM Aggregation

The AI initially suggested this for the leaderboard:

```python
User.objects.annotate(
    karma=Count('posts__likes', filter=Q(...)) * 5 + Count('comments__likes', filter=Q(...))
).order_by('-karma')
```

**The problem:** Django's ORM doesn't handle nested aggregations across multiple JOINs well. The counts got inflated because of how the rows multiply during JOINs.

**My fix:** I just fetched the likes and calculated in Python. Less "elegant" maybe, but it actually works and I can understand what it's doing. Sometimes the simple approach is the right one.

### Another issue: Recursive serializer

The AI wanted to do:

```python
def get_replies(self, obj):
    return CommentSerializer(obj.replies.all(), many=True).data  # N+1!
```

This hits the database for every comment. I fixed it by prefetching everything upfront and attaching the replies in memory before serialization.

---

## Concurrency (Double-Likes)

Two things prevent someone from liking the same post twice:

1. **Database constraint** - `UniqueConstraint(fields=['user', 'post'])` makes the DB reject duplicates

2. **Atomic transaction** - I wrap the like toggle in `transaction.atomic()` with `select_for_update()` to lock the row while checking/creating

```python
with transaction.atomic():
    existing = Like.objects.filter(user=user, post=post).select_for_update().first()
    if existing:
        existing.delete()  # unlike
    else:
        Like.objects.create(user=user, post=post)  # like
```

Even if two requests come in at the exact same time, one will wait for the other to finish.
