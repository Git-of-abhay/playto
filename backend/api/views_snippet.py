
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
        
        return Response({
            'username': target_user.username,
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
