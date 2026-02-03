import { useState } from 'react';
import { createComment } from '../api';

export default function CreateComment({ postId, parentId = null, onCreated, onCancel, user }) {
    const [content, setContent] = useState('');
    const [submitting, setSubmitting] = useState(false);

    async function handleSubmit(e) {
        e.preventDefault();
        if (!content.trim() || submitting) return;

        setSubmitting(true);
        try {
            const newComment = await createComment(postId, content, parentId);
            setContent('');
            onCreated(newComment);
        } catch (err) {
            console.error('Failed to create comment:', err);
        } finally {
            setSubmitting(false);
        }
    }

    return (
        <form onSubmit={handleSubmit} className="flex gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                {user?.username?.[0]?.toUpperCase() || '?'}
            </div>
            <div className="flex-1 flex gap-2">
                <input
                    type="text"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder={parentId ? "Write a reply..." : "Add a comment..."}
                    className="flex-1 bg-gray-100 border border-gray-200 rounded-full px-4 py-2 text-sm text-gray-800 placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:bg-white"
                />
                <button
                    type="submit"
                    disabled={submitting || !content.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-full font-semibold text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    {parentId ? 'Reply' : 'Post'}
                </button>
                {onCancel && (
                    <button
                        type="button"
                        onClick={onCancel}
                        className="px-3 py-2 text-gray-500 hover:text-gray-700 text-sm"
                    >
                        Cancel
                    </button>
                )}
            </div>
        </form>
    );
}
