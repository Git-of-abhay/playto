import { useState } from 'react';
import { createPost } from '../api';

export default function CreatePost({ onCreated, user }) {
    const [content, setContent] = useState('');
    const [submitting, setSubmitting] = useState(false);

    async function handleSubmit(e) {
        e.preventDefault();
        if (!content.trim() || submitting) return;

        setSubmitting(true);
        try {
            const newPost = await createPost(content);
            setContent('');
            onCreated(newPost);
        } catch (err) {
            console.error('Failed to create post:', err);
        } finally {
            setSubmitting(false);
        }
    }

    return (
        <form onSubmit={handleSubmit}>
            <div className="flex gap-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
                    {user?.username?.[0]?.toUpperCase() || '?'}
                </div>
                <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="What do you want to talk about?"
                    rows={3}
                    className="flex-1 bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-gray-800 placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:bg-white resize-none"
                />
            </div>
            <div className="flex justify-end pt-3">
                <button
                    type="submit"
                    disabled={submitting || !content.trim()}
                    className="px-6 py-2 bg-blue-600 text-white rounded-full font-semibold text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    {submitting ? 'Posting...' : 'Post'}
                </button>
            </div>
        </form>
    );
}
