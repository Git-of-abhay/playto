import React, { useState, useEffect } from 'react';
import { followUser, unfollowUser, blockUser, reportContent } from '../api';

export default function UserActions({ targetUser, currentUser, onUpdate }) {
    const [following, setFollowing] = useState(targetUser.is_following);
    const [showReportModal, setShowReportModal] = useState(false);
    const [showMenu, setShowMenu] = useState(false);

    if (!currentUser || targetUser.id === currentUser.id) {
        return null; // Don't show actions for own profile
    }

    async function handleFollow() {
        try {
            if (following) {
                await unfollowUser(targetUser.username);
                setFollowing(false);
            } else {
                await followUser(targetUser.username);
                setFollowing(true);
            }
            if (onUpdate) onUpdate();
        } catch (err) {
            console.error('Follow action failed:', err);
        }
    }

    async function handleBlock() {
        if (confirm(`Block @${targetUser.username}? You won't see their posts.`)) {
            try {
                await blockUser(targetUser.username);
                setShowMenu(false);
                if (onUpdate) onUpdate();
            } catch (err) {
                console.error('Block failed:', err);
            }
        }
    }

    async function handleReport(reason, description) {
        try {
            await reportContent({
                reported_user: targetUser.id,
                reason,
                description
            });
            alert('Report submitted successfully');
            setShowReportModal(false);
        } catch (err) {
            console.error('Report failed:', err);
        }
    }

    return (
        <div className="flex gap-2 items-center">
            <button
                onClick={handleFollow}
                className={`px-4 py-2 rounded-full font-semibold text-sm ${following
                    ? 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
            >
                {following ? 'Following' : 'Follow'}
            </button>

            <div className="relative">
                <button
                    onClick={() => setShowMenu(!showMenu)}
                    className="p-2 hover:bg-gray-100 rounded-full"
                >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z" />
                    </svg>
                </button>

                {showMenu && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                        <button
                            onClick={handleBlock}
                            className="w-full text-left px-4 py-2 hover:bg-gray-100 text-red-600"
                        >
                            Block User
                        </button>
                        <button
                            onClick={() => { setShowReportModal(true); setShowMenu(false); }}
                            className="w-full text-left px-4 py-2 hover:bg-gray-100 text-red-600"
                        >
                            Report User
                        </button>
                    </div>
                )}
            </div>

            {showReportModal && (
                <ReportModal
                    onClose={() => setShowReportModal(false)}
                    onSubmit={handleReport}
                />
            )}
        </div>
    );
}

function ReportModal({ onClose, onSubmit }) {
    const [reason, setReason] = useState('spam');
    const [description, setDescription] = useState('');

    function handleSubmit(e) {
        e.preventDefault();
        onSubmit(reason, description);
    }

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
                <h2 className="text-xl font-bold mb-4">Report User</h2>
                <form onSubmit={handleSubmit}>
                    <select
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        className="w-full border rounded-lg p-2 mb-4"
                    >
                        <option value="spam">Spam</option>
                        <option value="harassment">Harassment</option>
                        <option value="inappropriate">Inappropriate Content</option>
                        <option value="violence">Violence</option>
                        <option value="misinformation">Misinformation</option>
                        <option value="other">Other</option>
                    </select>

                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Additional details (optional)"
                        className="w-full border rounded-lg p-2 mb-4 h-24"
                    />

                    <div className="flex gap-2 justify-end">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                        >
                            Submit Report
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
