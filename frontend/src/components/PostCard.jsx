import { useState, useEffect } from 'react';
import { likePost } from '../api';
import CommentThread from './CommentThread';
import CreateComment from './CreateComment';

export default function PostCard({ post, user, onUpdate, onUserClick }) {
    const [liked, setLiked] = useState(post.user_has_liked || false);
    const [likeCount, setLikeCount] = useState(post.like_count || 0);
    const [liking, setLiking] = useState(false);
    const [showComments, setShowComments] = useState(false);
    const [comments, setComments] = useState(post.comments || []);

    // Sync state with props - fixes "double click" issues if props update
    useEffect(() => {
        setLiked(post.user_has_liked || false);
        setLikeCount(post.like_count || 0);
        if (post.comments) {
            setComments(post.comments);
        }
    }, [post.user_has_liked, post.like_count, post.comments]);

    async function handleLike() {
        if (liking || !user) return;
        setLiking(true);

        // Optimistic update
        const wasLiked = liked;
        setLiked(!wasLiked);
        setLikeCount(prev => wasLiked ? prev - 1 : prev + 1);

        try {
            const result = await likePost(post.id);
            // Use server response as source of truth
            setLiked(result.liked);
            setLikeCount(result.like_count);
            if (onUpdate) onUpdate(); // Trigger global refresh
        } catch (err) {
            console.error('Like failed:', err);
            // Revert on error
            setLiked(wasLiked);
            setLikeCount(prev => wasLiked ? prev + 1 : prev - 1);
        } finally {
            setLiking(false);
        }
    }

    function handleNewComment(newComment) {
        setComments(prev => [...prev, newComment]);
        if (onUpdate) onUpdate(); // Trigger global refresh
    }

    function formatTime(dateStr) {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = (now - date) / 1000;

        if (diff < 60) return 'just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    const topLevelComments = comments.filter(c => !c.parent);

    return (
        <article className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            {/* Post content */}
            <div className="p-4">
                <div className="flex gap-3">
                    {/* Avatar */}
                    {/* Avatar */}
                    <div
                        className="w-12 h-12 rounded-full flex-shrink-0 cursor-pointer hover:opacity-90 overflow-hidden bg-gray-200"
                        onClick={() => onUserClick && onUserClick(post.author.username)}
                    >
                        {post.author.avatar ? (
                            <img src={post.author.avatar} alt="" className="w-full h-full object-cover" />
                        ) : (
                            <div className="w-full h-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white font-bold text-lg">
                                {(post.author.name || post.author.username)[0].toUpperCase()}
                            </div>
                        )}
                    </div>

                    <div className="flex-1 min-w-0">
                        {/* Header */}
                        <div className="flex items-center gap-2">
                            <span
                                className="font-semibold text-gray-900 hover:text-blue-600 hover:underline cursor-pointer"
                                onClick={() => onUserClick && onUserClick(post.author.username)}
                            >
                                {post.author.name || post.author.username}
                            </span>
                            <span className="text-gray-400">•</span>
                            <span className="text-gray-500 text-sm">{formatTime(post.created_at)}</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">@{post.author.username}</p>

                        {/* Content */}
                        <p className="text-gray-800 mt-3 whitespace-pre-wrap leading-relaxed">{post.content}</p>
                    </div>
                </div>
            </div>

            {/* Stats bar */}
            <div className="px-4 py-2 border-t border-gray-100 flex items-center gap-4 text-xs text-gray-500">
                {likeCount > 0 && (
                    <span className="flex items-center gap-1.5">
                        <span className="w-5 h-5 rounded-full bg-blue-600 flex items-center justify-center">
                            <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                            </svg>
                        </span>
                        <span className="font-medium">{likeCount} {likeCount === 1 ? 'like' : 'likes'}</span>
                    </span>
                )}
                {topLevelComments.length > 0 && (
                    <span
                        className="hover:underline cursor-pointer hover:text-blue-600"
                        onClick={() => setShowComments(!showComments)}
                    >
                        {topLevelComments.length} {topLevelComments.length === 1 ? 'comment' : 'comments'}
                    </span>
                )}
            </div>

            {/* Actions */}
            <div className="px-2 py-1 border-t border-gray-200 flex">
                <button
                    onClick={handleLike}
                    disabled={liking || !user}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 mx-1 rounded-lg transition-all duration-200 ${liked
                        ? 'text-blue-600 bg-blue-50 font-semibold'
                        : 'text-gray-600 hover:bg-gray-100'
                        } ${!user ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                    <svg className="w-5 h-5" fill={liked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={liked ? 0 : 1.5} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                    </svg>
                    <span className="text-sm font-medium">{liked ? 'Liked' : 'Like'}</span>
                </button>

                <button
                    onClick={() => setShowComments(!showComments)}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 mx-1 rounded-lg transition-colors ${showComments ? 'text-blue-600 bg-blue-50' : 'text-gray-600 hover:bg-gray-100'
                        }`}
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <span className="text-sm font-medium">Comment</span>
                </button>
            </div>

            {/* Comments Section */}
            {showComments && (
                <div className="border-t border-gray-200 bg-gray-50 p-4">
                    {user && (
                        <div className="mb-4">
                            <CreateComment
                                postId={post.id}
                                onCreated={handleNewComment}
                                user={user}
                            />
                        </div>
                    )}

                    <div className="space-y-4">
                        {topLevelComments.map(comment => (
                            <CommentThread
                                key={comment.id}
                                comment={comment}
                                postId={post.id}
                                user={user}
                                allComments={comments}
                                onUpdate={onUpdate}
                                onUserClick={onUserClick}
                            />
                        ))}
                        {topLevelComments.length === 0 && (
                            <p className="text-gray-500 text-sm text-center py-4">No comments yet. Be the first to comment!</p>
                        )}
                    </div>
                </div>
            )}
        </article>
    );
}
