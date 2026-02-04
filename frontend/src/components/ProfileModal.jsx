import { useState, useEffect, useRef } from 'react';
import { getUserProfile, updateProfile } from '../api';
import PostCard from './PostCard';

export default function ProfileModal({ username, currentUser, onClose, onUpdate, onViewPost }) {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('posts');
    const [error, setError] = useState(null);

    // Edit State
    const [isEditing, setIsEditing] = useState(false);
    const [editName, setEditName] = useState('');
    const [editAvatar, setEditAvatar] = useState(null);
    const [previewAvatar, setPreviewAvatar] = useState(null);
    const [saving, setSaving] = useState(false);
    const fileInputRef = useRef(null);

    useEffect(() => {
        loadProfile();
    }, [username]);

    async function loadProfile() {
        try {
            setLoading(true);
            const data = await getUserProfile(username);
            setProfile(data);
            setEditName(data.name || '');
            setPreviewAvatar(data.avatar);
        } catch (err) {
            setError('Failed to load profile');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }

    async function handleSave() {
        try {
            setSaving(true);
            const formData = new FormData();
            formData.append('name', editName);
            if (editAvatar) {
                formData.append('avatar', editAvatar);
            }

            const updatedUser = await updateProfile(formData);

            // Reload profile data locally
            setProfile(prev => ({
                ...prev,
                name: updatedUser.name,
                avatar: updatedUser.avatar
            }));

            setIsEditing(false);
            setEditAvatar(null);
            if (onUpdate) onUpdate(); // Refresh other components if needed
        } catch (err) {
            alert('Failed to update profile');
        } finally {
            setSaving(false);
        }
    }

    function handleFileChange(e) {
        const file = e.target.files[0];
        if (file) {
            setEditAvatar(file);
            setPreviewAvatar(URL.createObjectURL(file));
        }
    }

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric'
        });
    }

    const isOwner = currentUser && currentUser.username === username;

    if (!username) return null;

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200">

                {/* Header */}
                <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                    <h2 className="text-xl font-bold text-gray-800">
                        {isEditing ? 'Validating Profile...' : 'User Profile'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 rounded-full bg-white text-gray-500 hover:text-gray-800 flex items-center justify-center transition-colors"
                    >
                        ✕
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {loading ? (
                        <div className="flex justify-center py-12">
                            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                        </div>
                    ) : error ? (
                        <div className="text-center text-red-500 py-8">{error}</div>
                    ) : profile ? (
                        <div className="space-y-6">

                            {/* Profile Info */}
                            <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
                                <div className="relative group">
                                    <div className="w-24 h-24 rounded-full overflow-hidden shadow-lg bg-gray-200 flex-shrink-0">
                                        {(isEditing ? previewAvatar : profile.avatar) ? (
                                            <img
                                                src={isEditing ? previewAvatar : profile.avatar}
                                                alt={profile.username}
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-full h-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white text-4xl font-bold">
                                                {profile.name ? profile.name[0].toUpperCase() : profile.username[0].toUpperCase()}
                                            </div>
                                        )}
                                    </div>

                                    {isEditing && (
                                        <button
                                            onClick={() => fileInputRef.current?.click()}
                                            className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded-full cursor-pointer"
                                        >
                                            <span className="text-white text-xs font-bold">Change</span>
                                        </button>
                                    )}
                                    <input
                                        type="file"
                                        accept="image/*"
                                        className="hidden"
                                        ref={fileInputRef}
                                        onChange={handleFileChange}
                                    />
                                </div>

                                <div className="flex-1 text-center sm:text-left">
                                    {isEditing ? (
                                        <div className="space-y-3">
                                            <div>
                                                <label className="block text-xs font-semibold text-gray-500 uppercase">Display Name</label>
                                                <input
                                                    type="text"
                                                    value={editName}
                                                    onChange={e => setEditName(e.target.value)}
                                                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-1.5 focus:ring-blue-500 focus:border-blue-500"
                                                    placeholder="Your Name"
                                                />
                                            </div>
                                            <div className="flex gap-2 justify-center sm:justify-start">
                                                <button
                                                    onClick={handleSave}
                                                    disabled={saving}
                                                    className="px-4 py-1.5 bg-blue-600 text-white rounded-md text-sm font-semibold hover:bg-blue-700 disabled:opacity-50"
                                                >
                                                    {saving ? 'Saving...' : 'Save Changes'}
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        setIsEditing(false);
                                                        setEditName(profile.name || '');
                                                        setPreviewAvatar(profile.avatar);
                                                        setEditAvatar(null);
                                                    }}
                                                    className="px-4 py-1.5 bg-gray-200 text-gray-700 rounded-md text-sm font-semibold hover:bg-gray-300"
                                                >
                                                    Cancel
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <>
                                            <h1 className="text-2xl font-bold text-gray-900">
                                                {profile.name || profile.username}
                                                <span className="text-gray-500 text-lg font-normal ml-2">@{profile.username}</span>
                                            </h1>
                                            <p className="text-gray-500">Joined {formatDate(profile.date_joined)}</p>

                                            {isOwner && (
                                                <button
                                                    onClick={() => setIsEditing(true)}
                                                    className="mt-2 text-sm text-blue-600 font-semibold hover:underline"
                                                >
                                                    Edit Profile
                                                </button>
                                            )}

                                            <div className="flex gap-6 mt-4 justify-center sm:justify-start">
                                                <div className="text-center sm:text-left">
                                                    <div className="text-xl font-bold text-blue-600">{profile.stats.total_karma}</div>
                                                    <div className="text-xs text-gray-500 uppercase tracking-wide font-semibold">Karma</div>
                                                </div>
                                                <div className="text-center sm:text-left">
                                                    <div className="text-xl font-bold text-gray-800">{profile.stats.post_count}</div>
                                                    <div className="text-xs text-gray-500 uppercase tracking-wide font-semibold">Posts</div>
                                                </div>
                                                <div className="text-center sm:text-left">
                                                    <div className="text-xl font-bold text-gray-800">{profile.stats.comment_count}</div>
                                                    <div className="text-xs text-gray-500 uppercase tracking-wide font-semibold">Replies</div>
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </div>
                            </div>

                            {/* Tabs */}
                            {!isEditing && (
                                <>
                                    <div className="flex border-b border-gray-200">
                                        <button
                                            onClick={() => setActiveTab('posts')}
                                            className={`px-6 py-3 font-medium text-sm transition-colors relative ${activeTab === 'posts'
                                                ? 'text-blue-600'
                                                : 'text-gray-500 hover:text-gray-800'
                                                }`}
                                        >
                                            Recent Posts
                                            {activeTab === 'posts' && (
                                                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600" />
                                            )}
                                        </button>
                                        <button
                                            onClick={() => setActiveTab('comments')}
                                            className={`px-6 py-3 font-medium text-sm transition-colors relative ${activeTab === 'comments'
                                                ? 'text-blue-600'
                                                : 'text-gray-500 hover:text-gray-800'
                                                }`}
                                        >
                                            Recent Replies
                                            {activeTab === 'comments' && (
                                                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600" />
                                            )}
                                        </button>
                                    </div>

                                    <div className="space-y-4">
                                        {activeTab === 'posts' && (
                                            <>
                                                {profile.recent_posts.length === 0 ? (
                                                    <p className="text-gray-500 text-center py-8">No posts yet.</p>
                                                ) : (
                                                    profile.recent_posts.map(post => (
                                                        <PostCard
                                                            key={post.id}
                                                            post={post}
                                                            user={currentUser}
                                                            onUpdate={onUpdate}
                                                        />
                                                    ))
                                                )}
                                            </>
                                        )}

                                        {activeTab === 'comments' && (
                                            <>
                                                {profile.recent_comments.length === 0 ? (
                                                    <p className="text-gray-500 text-center py-8">No replies yet.</p>
                                                ) : (
                                                    <div className="space-y-3">
                                                        {profile.recent_comments.map(comment => (
                                                            <div key={comment.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:bg-white transition-colors cursor-pointer"
                                                                onClick={() => onViewPost && onViewPost(comment.post)}>
                                                                <div className="text-xs text-gray-500 mb-2 flex items-center gap-2">
                                                                    <span className="bg-gray-200 px-2 py-0.5 rounded text-gray-600 font-medium">
                                                                        Replying to @{comment.post_author_username}
                                                                    </span>
                                                                    <span>•</span>
                                                                    <span>{new Date(comment.created_at).toLocaleDateString()}</span>
                                                                </div>

                                                                {/* Context Snippet */}
                                                                <div className="text-xs text-gray-500 mb-3 italic border-l-2 border-blue-200 pl-3 py-1">
                                                                    "{comment.post_title && comment.post_title.length > 60
                                                                        ? comment.post_title.substring(0, 60) + '...'
                                                                        : comment.post_title || 'Post'}"
                                                                </div>

                                                                <p className="text-gray-800 font-medium">{comment.content}</p>

                                                                <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
                                                                    <span className="flex items-center gap-1 group-hover:text-blue-600 transition-colors">
                                                                        <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                                                                            <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                                                                        </svg>
                                                                        {comment.like_count} likes
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </>
                                        )}
                                    </div>
                                </>
                            )}

                        </div>
                    ) : null}
                </div>
            </div>
        </div>
    );
}
