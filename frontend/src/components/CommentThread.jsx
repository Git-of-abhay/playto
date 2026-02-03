import { useState, useEffect } from 'react';
import { likeComment } from '../api';
import CreateComment from './CreateComment';

export default function CommentThread({ comment, postId, user, allComments, depth = 0, onUpdate, onUserClick }) {
    const [liked, setLiked] = useState(comment.user_has_liked || false);
    const [likeCount, setLikeCount] = useState(comment.like_count || 0);
    const [liking, setLiking] = useState(false);
    const [showReply, setShowReply] = useState(false);
    const [replies, setReplies] = useState(comment.replies || []);

    const maxDepth = 3;

    // Sync state with props
    useEffect(() => {
        setLiked(comment.user_has_liked || false);
        setLikeCount(comment.like_count || 0);
        setReplies(comment.replies || []);
    }, [comment.user_has_liked, comment.like_count, comment.replies]);

    async function handleLike() {
        if (liking || !user) return;
        setLiking(true);

        const wasLiked = liked;
        setLiked(!wasLiked);
        setLikeCount(prev => wasLiked ? prev - 1 : prev + 1);

        try {
            const result = await likeComment(comment.id);
            setLiked(result.liked);
            setLikeCount(result.like_count);
            if (onUpdate) onUpdate(); // Trigger global refresh (Leaderboard etc)
        } catch (err) {
            console.error('Like failed:', err);
            setLiked(wasLiked);
            setLikeCount(prev => wasLiked ? prev + 1 : prev - 1);
        } finally {
            setLiking(false);
        }
    }

    function handleNewReply(newReply) {
        setReplies(prev => [...prev, newReply]);
        setShowReply(false);
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

    return (
        <div className={depth > 0 ? 'ml-8 border-l-2 border-gray-200 pl-4' : ''}>
            <div className="flex gap-3">
                <div
                    className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 cursor-pointer overflow-hidden"
                    onClick={() => onUserClick && onUserClick(comment.author.username)}
                >
                    {comment.author.avatar ? (
                        <img src={comment.author.avatar} alt="" className="w-full h-full object-cover" />
                    ) : (
                        (comment.author.name || comment.author.username)[0].toUpperCase()
                    )}
                </div>

                <div className="flex-1">
                    <div className="bg-gray-100 rounded-xl px-4 py-2">
                        <div className="flex items-center gap-2">
                            <span
                                className="font-semibold text-gray-900 text-sm cursor-pointer hover:text-blue-600 hover:underline"
                                onClick={() => onUserClick && onUserClick(comment.author.username)}
                            >
                                {comment.author.name || comment.author.username}
                            </span>
                            <span className="text-xs text-gray-500">{formatTime(comment.created_at)}</span>
                        </div>
                        <p className="text-gray-800 text-sm mt-1">{comment.content}</p>
                    </div>

                    {/* Comment actions */}
                    <div className="flex items-center gap-4 mt-1.5 ml-2 text-xs">
                        <button
                            onClick={handleLike}
                            disabled={liking || !user}
                            className={`font-semibold transition-colors ${liked ? 'text-blue-600' : 'text-gray-500 hover:text-blue-600'
                                } ${!user ? 'opacity-50' : ''}`}
                        >
                            {liked ? 'Liked' : 'Like'} {likeCount > 0 && `(${likeCount})`}
                        </button>

                        {user && depth < maxDepth && (
                            <button
                                onClick={() => setShowReply(!showReply)}
                                className="font-semibold text-gray-500 hover:text-blue-600 transition-colors"
                            >
                                Reply
                            </button>
                        )}

                        {replies.length > 0 && (
                            <span className="text-gray-400">
                                {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {showReply && (
                <div className="mt-3 ml-11">
                    <CreateComment
                        postId={postId}
                        parentId={comment.id}
                        onCreated={handleNewReply}
                        onCancel={() => setShowReply(false)}
                        user={user}
                    />
                </div>
            )}

            {replies.length > 0 && (
                <div className="mt-3 space-y-3">
                    {replies.map(reply => (
                        <CommentThread
                            key={reply.id}
                            comment={reply}
                            postId={postId}
                            user={user}
                            allComments={allComments}
                            depth={depth + 1}
                            onUpdate={onUpdate}
                            onUserClick={onUserClick}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
